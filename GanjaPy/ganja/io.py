import numpy as np
import root_numpy as rnp
import pandas as pd

from skimage.transform import downscale_local_mean
from sklearn.utils import shuffle

# from sklearn.externals.joblib import Parallel, parallel_backend, register_parallel_backend
from joblib import Parallel, delayed

import os
import json
import gc


from tqdm import tqdm_notebook as tqdm

from . import utils
from .preprocessing import pixel_metrics


# -------------------------------------------------------------------------------------------
def read_root(fnames,tree=None,inpshape=(64,64,1),
              imgen='jetImageGen',imreco='jetImageReco',
              rebin_as=None,
              post_process=None,
              crop_left=None,
              **kwargs):

    if not 'branches' in kwargs:
        kwargs['branches'] = ['nPU','rho',
                              'ptGen','etaGen','phiGen',
                              'pt','eta','phi',
        ]
    keys = filter(lambda x: x not in [imreco,imgen], kwargs['branches'])

    if not imgen in kwargs['branches']:
        kwargs['branches'].append(imgen)
    if not imreco in kwargs['branches']:
        kwargs['branches'].append(imreco)

    arr = rnp.root2array(fnames,tree,**kwargs)
    if rebin_as is not None:
        factors = np.array(inpshape).astype(np.int) / np.array(rebin_as).astype(np.int)
        scale_back = factors.prod()
        factors = tuple(factors.tolist())
        def rebin(img):            
            img = img.reshape(inpshape)
            if crop_left:
                img = img[crop_left:,crop_left:]
            ret=downscale_local_mean(img, factors)
            return ret
        gen = np.array(list(map(rebin, arr[imgen])))
        reco = np.array(list(map(rebin, arr[imreco])))
        gen *= scale_back
        reco *= scale_back
    else:
        gen = np.vstack(arr[imgen]).reshape( (-1,)+inpshape )
        reco = np.vstack(arr[imreco]).reshape( (-1,)+inpshape )
    gc.collect()
    
    cols = { x:arr[x] for x in keys}
    df = pd.DataFrame(data=cols)
    if post_process:
        gen,reco = post_process(df,gen,reco)

    # gc.collect()
    return df,gen,reco

# -------------------------------------------------------------------------------------------
def write_out(dest,folder,fnum,record,df,gen,reco,compress=True):

    dirname = "%s/%s" % (dest,folder)
    if not os.path.exists(dirname):
        os.mkdir(dirname)
    basename = "%s/%d" % (dirname,fnum)
    
    if df is not None:
        df.to_hdf(basename+'_info.hd5','info',format='t',mode='w',complib='bzip2',complevel=9)
        
    if gen is not None:
        assert( reco is not None )
        if compress:
            np.savez_compressed(basename+'_images.npz',gen=gen,reco=reco)
        else:
            np.save(basename+'_gen.npy',gen)
            np.save(basename+'_reco.npy',reco)
            
    if record is not None:
        with open(basename+'.json','w+') as rec:
            rec.write(json.dumps( record  ))
            rec.close()
    


# -------------------------------------------------------------------------------------------
def read_dataset(folder,files,proc,xs, **kwargs):
    dfs = []
    nevents = 0.
    for fil in tqdm(files,desc=os.path.basename(folder),leave=False):
        jfil = open(os.path.join(folder,'%s.json' % fil))
        nevents += json.loads(jfil.read())['nevents']
        jfil.close()
        df = pd.read_hdf(os.path.join(folder,'%s_info.hd5' % fil, **kwargs) )
        df['file'] = fil
        df['row'] = df.index
        dfs.append( df  )
    df = pd.concat(dfs)
    df['weight'] = xs / nevents
    df['proc'] = proc
    return df

# -------------------------------------------------------------------------------------------
def read_datasets(inputs,cross_sections="data/cross_sections.json", **kwargs):

    dfs = []
    proc_ids = {}
    for proc,item in tqdm(enumerate(inputs.items()),desc='reading datasets'):
        folder,files = item
        xs = utils.read_xsection(folder,cross_sections)
        proc_ids[proc] = folder
        # print('reading %s' % folder)
        dfs.append( read_dataset(folder,files,proc,xs, **kwargs) )
    return proc_ids,pd.concat(dfs)


# -------------------------------------------------------------------------------------------
def read_images(folder,files,compressed=True,**kwargs):
    fils = []
    gens, recos = [], []
    for fil in files:
        if compressed:
            jfil = np.load(os.path.join(folder,'%s_images.npz' % fil), **kwargs )
            fils.append(jfil)
        else:
            jgen = np.load(os.path.join(folder,'%s_gen.npy' % fil), **kwargs )
            jreco = np.load(os.path.join(folder,'%s_reco.npy' % fil), **kwargs )
            gens.append(jgen)
            recos.append(jreco)
    if compressed:
        return fils
    else:
        return gens,recos
    
# -------------------------------------------------------------------------------------------
def read_datasets_images(inputs, quiet=False, **kwargs):

    ## gen = []
    ## reco = []
    fils = []
    proc_ids = {}
    for proc,item in enumerate(inputs.items()):
        folder,files = item
        if not quiet:
            print('reading images from %s' % folder)
        fils.append( read_images(folder,files,**kwargs) )
        # igen,ireco = 
        # gen.extend(igen)
        # reco.extend(ireco)
    # return np.concatenate(gen),np.concatenate(reco)
    return fils
    




# -------------------------------------------------------------------------------------------
## def make_partition(ipart,info,proc_ids,target):
def make_partition(ipart,part,proc_ids,procs,target,compress=False,**kwargs):
    if not 'mmap_mode' in kwargs: kwargs['mmap_mode'] ='r'
    part_inputs = {}
    ## part = info.groupby(['proc','file']).apply(lambda x: x['row'].values)
    gens = []
    recos = []
    ## procs = part.index.levels[0]
    ## for iproc in part.index.levels[0]:
    for iproc in procs:
        proc = part[iproc]
        files = proc.index
        proc_files = read_datasets_images( { proc_ids[iproc]: files } ,**kwargs)
        for ifil,fil in zip(files,reduce(lambda x,y: x+y, proc_files)):
            rows = proc[ifil]
            gens.append( fil['gen'][rows] )
            recos.append( fil['reco'][rows] )
            fil.close()
    gen = np.concatenate(gens)
    reco = np.concatenate(recos)        
    write_out(target,'',ipart,None,None,gen,reco,compress=compress)
    return pixel_metrics(gen),pixel_metrics(reco)
## return gen,reco



# -------------------------------------------------------------------------------------------
def make_partitions(df,npartitions,proc_ids,target,n_jobs=2,compress=False):
    
    df['partition'] = np.random.choice(np.arange(npartitions),df.shape[0])
    # partitions = df.groupby('partition')
    ## grouped = df.groupby(['partition','proc','file'])
    partitions = df.groupby(['partition','proc','file']).apply(lambda x: x['row'].values)
    parts = partitions.index.levels[0]
    procs = partitions.index.levels[1]
    
    ## for ipart in partitions.index.levels[0]:
    print('Partitioning images')
    with Parallel(n_jobs=n_jobs) as parallel:
        metrics = parallel( delayed(make_partition)
                            (ipart,partitions[ipart],proc_ids,procs,target,
                                                    compress=compress,quiet=True) for ipart in tqdm(parts)
        )
        
    infos = []
    print('Partitioning infos')
    for ipart,info in tqdm(df.groupby('partition')):
        write_out(target,'',ipart,None,info,None,None)
        infos.append(info.shape)
            
    ## for ipart,info in partitions:
    ##     make_partition(ipart,info,proc_ids,target)
    ##     break
    ## print(metrics)
    ## print(zip(ret,infos))
    with open(target+'/proc_ids.json','w+') as rec:
        rec.write(json.dumps( proc_ids  ))
        rec.close()
