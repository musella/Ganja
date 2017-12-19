import keras.backend as K
import keras.losses
import keras.utils.generic_utils

import numpy as np

# ---------------------------------------------------------------------------------------------------
def stratified_mean_absolute_error(y_true,y_pred):
    y_pred = K.flatten(y_pred)
    y_true = K.flatten(y_true)
    mask = K.cast(K.greater(y_true,0),K.floatx())
    absdiff = K.abs(y_pred-y_true)
    loss1 = K.sum(mask*absdiff) / K.sum(mask)
    loss0 = K.sum( (1.-mask)*absdiff ) / K.sum(1.-mask)
    return loss0+loss1

# ---------------------------------------------------------------------------------------------------
def stratified_mean_absolute_error_with_total(y_true,y_pred):
    y_pred_tot = K.sum(y_pred,axis=(1,2,3))
    y_true_tot = K.sum(y_true,axis=(1,2,3))
    y_pred = K.flatten(y_pred)
    y_true = K.flatten(y_true)
    mask = K.cast(K.greater(y_true,0),K.floatx())
    absdiff = K.abs(y_pred-y_true)
    loss1 = K.sum(mask*absdiff) / K.sum(mask)
    loss0 = K.sum( (1.-mask)*absdiff ) / K.sum(1.-mask)
    return loss0+loss1+K.mean(K.abs(y_pred_tot-y_true_tot))

# ---------------------------------------------------------------------------------------------------
def stratified_mean_squared_error(y_true,y_pred):
    y_pred = K.flatten(y_pred)
    y_true = K.flatten(y_true)
    mask = K.cast(K.greater(y_true,0),K.floatx())
    absdiff = K.square(y_pred-y_true)
    loss1 = K.sum(mask*absdiff) / K.sum(mask)
    loss0 = K.sum( (1.-mask)*absdiff ) / K.sum(1.-mask)
    return loss0+loss1

# ---------------------------------------------------------------------------------------------------
def stratified_mean_squared_error_with_total(y_true,y_pred):
    y_pred_tot = K.sum(y_pred,axis=(1,2,3))
    y_true_tot = K.sum(y_true,axis=(1,2,3))
    y_pred = K.flatten(y_pred)
    y_true = K.flatten(y_true)
    mask = K.cast(K.greater(y_true,0),K.floatx())
    absdiff = K.square(y_pred-y_true)
    loss1 = K.sum(mask*absdiff) / K.sum(mask)
    loss0 = K.sum( (1.-mask)*absdiff ) / K.sum(1.-mask)
    return loss0+loss1+K.mean(K.square(y_pred_tot-y_true_tot))

# ---------------------------------------------------------------------------------------------------
def soft_mask_mean_squared_error(y_true,y_pred):
    y_pred,soft_pred = y_pred[:,:,:,0],y_pred[:,:,:,1]
    y_true,mask_true = y_true[:,:,:,0],y_true[:,:,:,1]
    ## mask = K.cast(K.greater(y_true,0),K.floatx())
    loss = -K.mean( mask_true*(K.log(soft_pred+K.epsilon()) - 0.5*K.square(y_true-y_pred)) + (1.-mask_true)*(K.log(1.-soft_pred+K.epsilon()) ) )
    return loss

# ---------------------------------------------------------------------------------------------------
def soft_mask_mean_absolute_error(y_true,y_pred):
    y_pred,soft_pred = y_pred[:,:,:,0],y_pred[:,:,:,1]
    y_true,mask_true = y_true[:,:,:,0],y_true[:,:,:,1]
    loss = -K.mean( mask_true*(K.log(soft_pred+K.epsilon()) - 0.5*K.abs(y_true-y_pred)) + (1.-mask_true)*(K.log(1.-soft_pred+K.epsilon()) ) )
    return loss

# ---------------------------------------------------------------------------------------------------
def soft_mask_mean_squared_error_with_total(y_true,y_pred):
    y_pred_tot = K.sum(y_pred[:,:,:,0]*y_pred[:,:,:,1],axis=(1,2))
    y_true_tot = K.sum(y_true[:,:,:,0]*y_true[:,:,:,1],axis=(1,2))
    return soft_mask_mean_squared_error(y_true,y_pred)+0.5*K.mean(K.square(y_pred_tot-y_true_tot))

# ---------------------------------------------------------------------------------------------------
def soft_mask_mean_absolute_error_with_total(y_true,y_pred):
    y_pred_tot = K.sum(K.prod([y_pred[:,:,:,0],y_pred[:,:,:,1]],axis=(1,2)),axis=(1,2))
    y_true_tot = K.sum(K.prod([y_true[:,:,:,0],y_true[:,:,:,1]],axis=(1,2)),axis=(1,2))
    return soft_mask_mean_absolute_error(y_true,y_pred)+0.5*K.mean(K.abs(y_pred_tot-y_true_tot))

# ---------------------------------------------------------------------------------------------------
class SoftMaskMeanSquaredError(object):

    __name__ = 'SoftMaskMeanSquaredError'
    
    def __init__(self,lmbd=1.,alpha=1.):
        self.lmbd = lmbd
        self.alpha = alpha
        super(SoftMaskMeanSquaredError,self).__init__()
        
    def get_config(self):
        return { "lmbd" : self.lmbd, "alpha" : self.alpha }

    def __call__(self,y_true,y_pred):
        y_pred,soft_pred = y_pred[:,:,:,0],y_pred[:,:,:,1]
        y_true,mask_true = y_true[:,:,:,0],y_true[:,:,:,1]
        loss = -K.mean( mask_true*(K.log(soft_pred+K.epsilon()) - 0.5*self.lmbd*K.square(y_true-y_pred)) + self.alpha*(1.-mask_true)*(K.log(1.-soft_pred+K.epsilon()) ) )
        return loss


# ---------------------------------------------------------------------------------------------------
class SoftMaskMeanSquaredErrorWithTotal(SoftMaskMeanSquaredError):

    __name__ = 'SoftMaskMeanSquaredErrorWithTotal'
    
    def __init__(self,tau=1.,**kwargs):
        self.tau = tau
        super(SoftMaskMeanSquaredErrorWithTotal,self).__init__(**kwargs)
        
    def get_config(self):
        cfg = super(SoftMaskMeanSquaredErrorWithTotal,self).get_config()
        cfg.update({ "tau" : self.tau })
        return cfg

    def __call__(self,y_true,y_pred):
        loss1 = super(SoftMaskMeanSquaredErrorWithTotal,self).__call__(y_true,y_pred)
        if self.tau != 0.:
            y_pred_tot = K.sum(y_pred[:,:,:,0]*y_pred[:,:,:,1],axis=(1,2))
            y_true_tot = K.sum(y_true[:,:,:,0]*y_true[:,:,:,1],axis=(1,2))
            loss2 = 0.5*K.mean(K.square(y_pred_tot-y_true_tot))
            return loss1 + self.tau*loss2
        return loss1

# ---------------------------------------------------------------------------------------------------
class SoftMaskWeightedMeanSquaredError(object):

    __name__ = 'SoftMaskWeightedMeanSquaredError'
    
    def __init__(self,lmbd=1.,alpha=1.,weights=1.):
        self.lmbd = lmbd
        self.alpha = alpha
        self.weights = weights
        super(SoftMaskWeightedMeanSquaredError,self).__init__()
        
    def get_config(self):
        return { "lmbd" : self.lmbd, "alpha" : self.alpha, "weights" : self.weights }

    def __call__(self,y_true,y_pred):
        y_pred,soft_pred = y_pred[:,:,:,0],y_pred[:,:,:,1]
        y_true,mask_true = y_true[:,:,:,0],y_true[:,:,:,1]
        loss = -K.mean( self.weights*(mask_true*(K.log(soft_pred+K.epsilon()) - 0.5*self.lmbd*K.square(y_true-y_pred)) + self.alpha*(1.-mask_true)*(K.log(1.-soft_pred+K.epsilon()) )) )
        return loss


# ---------------------------------------------------------------------------------------------------
class SoftMaskWeightedMeanSquaredErrorWithTotal(SoftMaskWeightedMeanSquaredError):

    __name__ = 'SoftMaskWeightedMeanSquaredErrorWithTotal'
    
    def __init__(self,tau=1.,tau2=0.,use_last=False,**kwargs):
        self.tau = tau
        self.tau2 = tau2
        self.use_last = use_last
        super(SoftMaskWeightedMeanSquaredErrorWithTotal,self).__init__(**kwargs)
        
    def get_config(self):
        cfg = super(SoftMaskWeightedMeanSquaredErrorWithTotal,self).get_config()
        cfg.update({ "tau" : self.tau, "tau2" : self.tau2, "use_last" : self.use_last })
        return cfg

    def __call__(self,y_true,y_pred):
        loss = super(SoftMaskWeightedMeanSquaredErrorWithTotal,self).__call__(y_true,y_pred)
        if self.tau != 0.:
            y_true_tot = K.sum(y_true[:,:,:,0]*y_true[:,:,:,1],axis=(1,2))
            if self.use_last:
                y_pred_tot = K.sum(y_pred[:,:,:,-1],axis=(1,2))
            else:
                y_pred_tot = K.sum(y_pred[:,:,:,0]*y_pred[:,:,:,1],axis=(1,2))
            loss = loss + self.tau*0.5*K.mean(K.square(y_pred_tot-y_true_tot))
            if self.tau2 != 0.:
                print('tau2 != 0',self.tau2)
                ## loss = loss + self.tau*self.tau2*0.5*K.mean(K.square(K.square(y_pred_tot)-K.square(y_true_tot)))
                loss = loss + self.tau*self.tau2*0.5*K.mean(K.square(y_pred_tot)*(K.square(y_pred_tot)-2.*K.square(y_true_tot)))
        return loss

#### # ---------------------------------------------------------------------------------------------------
#### class GanSoftMaskWeightedMeanSquaredErrorWithTotal(SoftMaskWeightedMeanSquaredErrorWithTotal):
#### 
####     __name__ = 'SoftMaskWeightedMeanSquaredErrorWithTotal'
####     
####     def __init__(self,eta=1.,**kwargs):
####         self.eta = eta
####         super(GanSoftMaskWeightedMeanSquaredErrorWithTotal,self).__init__(**kwargs)
####         
####     def get_config(self):
####         cfg = super(GanSoftMaskWeightedMeanSquaredErrorWithTotal,self).get_config()
####         cfg.update({ "eta" : self.eta })
####         return cfg
#### 
####     def __call__(self,y_true,y_pred):
####         loss = super(GanSoftMaskWeightedMeanSquaredErrorWithTotal,self).__call__(y_true,y_pred)
####         if self.tau != 0.:
####             y_pred_tot = K.sum(y_pred[:,:,:,0]*y_pred[:,:,:,1],axis=(1,2))
####             y_true_tot = K.sum(y_true[:,:,:,0]*y_true[:,:,:,1],axis=(1,2))
####             loss = loss + self.tau*0.5*K.mean(K.square(y_pred_tot-y_true_tot))
####             if self.tau2 != 0.:
####                 loss = loss + self.tau*self.tau2*0.5*K.mean(K.pow(y_pred_tot-y_true_tot,4))
####         return loss


# ---------------------------------------------------------------------------------------------------
class SoftMaskMeanAbsoluteError(object):

    __name__ = 'SoftMaskMeanAbsoluteError'

    def __init__(self,lmbd=1.,alpha=1.):
        self.lmbd = lmbd
        self.alpha = alpha
        super(SoftMaskMeanAbsoluteError,self).__init__()
        
    def get_config(self):
        return { "lmbd" : self.lmbd, "alpha" : self.alpha }

    def __call__(self,y_true,y_pred):
        y_pred,soft_pred = y_pred[:,:,:,0],y_pred[:,:,:,1]
        y_true,mask_true = y_true[:,:,:,0],y_true[:,:,:,1]
        loss = -K.mean( mask_true*(K.log(soft_pred+K.epsilon()) - 0.5*self.lmbd*K.abs(y_true-y_pred)) + self.aplha*(1.-mask_true)*(K.log(1.-soft_pred+K.epsilon()) ) )
        return loss

    
# ---------------------------------------------------------------------------------------------------
class SoftMaskMeanAbsoluteErrorWithTotal(SoftMaskMeanAbsoluteError):

    __name__ = 'SoftMaskMeanAbsoluteErrorWithTotal'

    def __init__(self,tau=1.,**kwargs):
        self.tau = tau
        super(SoftMaskMeanAbsoluteErrorWithTotal,self).__init__(**kwargs)
        
    def get_config(self):
        cfg = super(SoftMaskMeanAbsoluteErrorWithTotal,self).get_config()
        cfg.update({ "tau" : self.tau })
        return cfg

    def __call__(self,y_true,y_pred):
        loss1 = super(SoftMaskMeanAbsoluteErrorWithTotal,self).__call__(y_true,y_pred)
        if self.tau != 0.:
            y_pred_tot = K.sum(y_pred[:,:,:,0]*y_true[:,:,:,1],axis=(1,2))
            y_true_tot = K.sum(y_true[:,:,:,0]*y_true[:,:,:,1],axis=(1,2))
            loss2 = 0.5*K.mean(K.abs(y_pred_tot-y_true_tot))
            return  loss1 + self.tau*loss2
        return loss1

# ---------------------------------------------------------------------------------------------------
def radial_weights(img_size):
    img_size2 = img_size // 2
    img_sizer = img_size % 2
    first = -img_size2
    last  = img_size2 + img_sizer
    ## print(img_size2,img_sizer,first,last)
    offset = float(img_sizer) / 2.
    x, y= np.ogrid[first:last,first:last ]
    radius = np.sqrt( (x+offset)**2 + (y+offset)**2 )
    
    radius[ radius == 0. ] = 1.
    ## print(radius)
    radius = (radius.max() / radius).reshape(1,img_size,img_size)#,1)
    radius *= (img_size**2) / radius.sum()
    return radius

    
# ---------------------------------------------------------------------------------------------------
keras.losses.soft_mask_mean_squared_error = soft_mask_mean_squared_error
keras.losses.soft_mask_mean_absolute_error = soft_mask_mean_absolute_error

keras.losses.soft_mask_mean_squared_error_with_total = soft_mask_mean_squared_error_with_total
keras.losses.soft_mask_mean_absolute_error_with_total = soft_mask_mean_absolute_error_with_total

keras.losses.stratified_mean_absolute_error = stratified_mean_absolute_error
keras.losses.stratified_mean_absolute_error_with_total = stratified_mean_absolute_error_with_total

keras.losses.stratified_mean_squared_error = stratified_mean_squared_error
keras.losses.stratified_mean_squared_error_with_total = stratified_mean_squared_error_with_total

keras.utils.generic_utils.get_custom_objects().update(
    dict(SoftMaskMeanSquaredError=SoftMaskMeanSquaredError,
         SoftMaskMeanSquaredErrorWithTotal=SoftMaskMeanSquaredErrorWithTotal,
         SoftMaskWeightedMeanSquaredError=SoftMaskWeightedMeanSquaredError,
         SoftMaskWeightedMeanSquaredErrorWithTotal=SoftMaskWeightedMeanSquaredErrorWithTotal,
         SoftMaskMeanAbsoluteError=SoftMaskMeanAbsoluteError,
         SoftMaskMeanAbsoluteErrorWithTotal=SoftMaskMeanAbsoluteErrorWithTotal)
)
