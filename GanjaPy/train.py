#!/bin/env python 

import numpy as np

import GAN.models as models
import ganja.io as io
import ganja.utils as utils
import ganja.plotting as plotting
import os

import GAN.unet as unet
import json

from keras.callbacks import TensorBoard, CSVLogger, ModelCheckpoint

from keras.optimizers import Adam

# ------------------------------------------------------------------------------------
class Parameters(utils.Parameters):
    
    # dataset to be loaded
    # ---------------------------------------------------------------
    base_folder = utils.param(os.getenv('SCRATCH')+'/ganja/split')
    version = utils.param('nov2_v3')
    compressed = utils.param(False)
    cond_variables = utils.param(['ptGen','etaGen','phiGen','nPU'])
    noise_dim = utils.param(0)
    
    # preprocessing
    # ---------------------------------------------------------------
    weights = utils.param('weights_nov2_pt.npy') 
    moments = utils.param('moments_nov2.npz')
    stdev_regularzation = utils.param(0.02)
    
    # train and validation samples size
    # ---------------------------------------------------------------
    ntrain = utils.param(2) ## roughly 1M jets
    nvalid = utils.param(1)
    valid_frac = utils.param(5) ## just take 1/5 of the validation examples

    # network parameters
    # ---------------------------------------------------------------
    nfilters = utils.param(8)
    n_encoding=utils.param(6)
    max_encoding=utils.param(16)
    decoding_last_plateau=utils.param(2)

    ## nfilters = utils.param(8)
    ## n_encoding=utils.param(5)
    ## max_encoding=utils.param(16)
    ## decoding_last_plateau=utils.param(1)

    # crop images
    # ---------------------------------------------------------------
    win_min=utils.param(0)
    img_size=utils.param(32)
    ## win_min=utils.param(8)
    ## img_size=utils.param(16)
    
    # network parameters
    # ---------------------------------------------------------------
    batch_size = utils.param(256)
    epochs = utils.param(200)
    
    # misc
    # ---------------------------------------------------------------
    monitor_dir = utils.param('log') # folder for logging
    batch = utils.param(True) # are we running in batch?

# Read all parameters above from command line. 
# Note: names are all converted to be all capital
class MyApp(utils.MyApp):
    classes = utils.List([Parameters])
notebook_parameters = Parameters(MyApp(is_main=True)).get_params()

# copy parameters to global scope
globals().update(notebook_parameters)

WIN_MAX=WIN_MIN+IMG_SIZE
#DM_OPTS.update( {"loss":LOSS} )
#AM_OPTS.update( {"loss":LOSS} )


plotting.batch = BATCH 

print("Parameters")
print("\n".join(map(lambda x: x[0]+":"+str(x[1]), notebook_parameters.items())))


weights = np.load(WEIGHTS.format(VERSION=VERSION),encoding='latin1')
weights = weights[0],weights[2:],weights[1]

moments = np.load(MOMENTS.format(VERSION=VERSION))
reco_moments = moments['reco_mean'],moments['reco_std'],STDEV_REGULARZATION
gen_moments = moments['gen_mean'],moments['gen_std'],STDEV_REGULARZATION

with open(BASE_FOLDER+'/'+VERSION+'/train_valid_test.json') as fin:
    split_map = json.loads(fin.read())

train_inputs = {os.path.join(BASE_FOLDER,VERSION) : split_map['train'][:NTRAIN]}
valid_inputs = {os.path.join(BASE_FOLDER,VERSION) : split_map['valid'][:NVALID]}

print("Training inputs")
print(train_inputs)

print("Validation inputs")
print(valid_inputs)

c_shape = None
z_shape = None
if len(COND_VARIABLES) > 0:
    c_shape = (1,len(COND_VARIABLES))
if NOISE_DIM > 0:
    z_shape = (1,NOISE_DIM)
model = unet.UnetGBuilder(nfilters=NFILTERS,
                          n_encoding=N_ENCODING,
                          max_encoding=MAX_ENCODING,
                          decoding_last_plateau=DECODING_LAST_PLATEAU)(
                              x_shape=(IMG_SIZE,IMG_SIZE,1),
                              c_shape=c_shape,
                              z_shape=z_shape
                          )

print('Model ')
print(model.summary())

readers_kwargs=dict(compressed=COMPRESSED,cache_img=True,cache_cond=True,
                    cond_names=COND_VARIABLES,noise_dim=NOISE_DIM
)
#,gen_moments=gen_moments)

train_reader = io.MultiReader(train_inputs,4,15,weights,**readers_kwargs)
valid_reader = io.MultiReader(valid_inputs,2,1,weights,**readers_kwargs)


train_reader.start()
valid_reader.start()


train_njets = 500000 * len(train_reader.readers)
valid_njets = 500000 * len(valid_reader.readers)


train_nbatches = train_njets // BATCH_SIZE 
valid_nbatches = valid_njets // BATCH_SIZE // VALID_FRAC

train_generator = train_reader(BATCH_SIZE,WIN_MIN,WIN_MAX)
valid_generator = valid_reader(BATCH_SIZE,WIN_MIN,WIN_MAX)

## train_reader = io.Reader(train_inputs,weights,compressed=COMPRESSED)#,gen_moments=gen_moments)
## valid_reader = io.Reader(valid_inputs,weights,compressed=COMPRESSED)#,gen_moments=gen_moments)
## print('Reading training data')
## X_train_buf,y_train_buf,w_train = train_reader.get()
## X_train = X_train_buf[:,WIN_MIN:WIN_MAX,WIN_MIN:WIN_MAX,:]
## y_train = y_train_buf[:,WIN_MIN:WIN_MAX,WIN_MIN:WIN_MAX,:]
## print(X_train.shape)
## 
## print('Reading validation data')
## X_valid_buf,y_valid_buf,w_valid = valid_reader.get()
## if VALID_FRAC > 1:
##     max_valid = X_valid_buf.shape[0] // VALID_FRAC
## else:
##     max_valid = None
## print('max_valid ', max_valid)
## X_valid = X_valid_buf[:max_valid,WIN_MIN:WIN_MAX,WIN_MIN:WIN_MAX,:]
## y_valid = y_valid_buf[:max_valid,WIN_MIN:WIN_MAX,WIN_MIN:WIN_MAX,:]
## w_valid = w_valid[:max_valid]
## print(X_valid.shape)

optimizer = Adam(lr=0.0002)

if not os.path.exists(MONITOR_DIR):
    os.mkdir(MONITOR_DIR)

with open(os.path.join(MONITOR_DIR,'config.json'),'w+') as cfg:
    cfg.write(json.dumps(notebook_parameters))
    
csv = CSVLogger("%s/metrics.csv" % MONITOR_DIR)
checkpoint = ModelCheckpoint("%s/model-{epoch:02d}.hdf5" % MONITOR_DIR, monitor='loss',
                             save_best_only=True, save_weights_only=False,
                             )

model.compile(loss='mean_squared_error',optimizer=optimizer)

print(model.optimizer)


## model.fit(X_train,y_train,sample_weight=w_train,
##           batch_size=BATCH_SIZE,
##           validation_data=(X_valid,y_valid,w_valid),
##           callbacks=[csv,checkpoint],
##           epochs=EPOCHS,shuffle=False  # already shuffled by reader
## )

model.fit_generator(train_generator,steps_per_epoch=train_nbatches,
                    validation_data=valid_generator,validation_steps=valid_nbatches,
		    callbacks=[csv,checkpoint],
                    epochs=EPOCHS
)
