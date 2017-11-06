import numpy as np
from skimage.transform import downscale_local_mean

from GAN.preprocessing import *

# ------------------------------------------------------------------------------------------
def rescale_by_pt(arr,gen,reco):
    gen *= (arr['pt'] / arr['ptGen']).reshape(-1,1,1,1)
    return gen,reco


# ------------------------------------------------------------------------------------------
def resize(target,gen,reco,reco_adjust=1.):

    assert( reco.shape[1:] == gen.shape[1:] )
    factors = np.array(reco.shape[1:3]).astype(np.int) / np.array(target).astype(np.int)
    scale_back = factors[0]*factors[1]
    factors = (1,factors[0],factors[1],1)
    
    # reco = downscale_local_mean(reco,factors)*reco_adjust*scale_back
    # gen = downscale_local_mean(gen,factors)*scale_back
    # reco = np.apply_along_axis(scale,0,reco)*reco_adjust
    # gen = np.apply_along_axis(scale,1,gen)

    
    
    return gen,reco

# ------------------------------------------------------------------------------------------
def pixel_metrics(images,axis=0):
    return np.array([images.min(axis=axis),images.max(axis=axis),images.mean(axis=axis),images.std(axis=axis)], dtype=[('min',np.float32),('max',np.float32),('mean',np.float32),('std',np.float32)])


## # ------------------------------------------------------------------------------------------
## def aggregate_metrics(metrics,axis=0):
##     aggregate = np.concatenate( metrics )
##     return np.array( [aggregate['min'].min(axis=axis),aggregate['max'].max(axis=axis),
##                       aggregate['mean'].sum(axis=axis) / aggregate['count']]
