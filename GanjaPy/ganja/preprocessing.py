import numpy as np
from skimage.transform import downscale_local_mean

from GAN.preprocessing import *


# ------------------------------------------------------------------------------------------
class WeighterWithCache:

    def __init__(self,df,variables,bins,weights,base=None,offset=False):
        self.df = df
        self.variables = variables
        self.bins = bins
        self.weights = weights
        self.base = base
        self.offset = offset
        self.cache_ = None

    def get(self):
        if self.cache_ is None:
            self.cache_ = reweight(self.df,self.variables,self.bins,self.weights,self.base,self.offset).values
            self.df,self.bins,self.weights = None,None,None
        return self.cache_
    
    
# ------------------------------------------------------------------------------------------
def normalize(x,mean,std,reg=None):
    x -= mean
    if reg is not None:
        x /= np.sqrt(std**2+reg**2)
    else:
        x /= std
    return x
    ## if reg is not None:
    ##     return (x - mean)/np.sqrt(std**2+reg**2)
    ## return (x - mean)/std    

# ------------------------------------------------------------------------------------------
def unnormalize(x,mean,std,reg=None):
    if reg is not None:
        return x*np.sqrt(std**2+reg**2) + mean
    return x*std + mean

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
