import matplotlib.pyplot as plt
import numpy as np

from GAN.plotting import batch

from keras.utils import to_categorical

from matplotlib.colors import LogNorm

saveto = None

# -----------------------------------------------------------------------------
def show_img(img, title, xlabel='$i\eta$', ylabel='$i\phi$', **kwargs):
    
    plt.title(title)
    plt.xlabel(xlabel)
    plt.ylabel(ylabel)    
    plt.imshow(img,**kwargs)
    plt.colorbar()
    
# -----------------------------------------------------------------------------
def show_prediction(img,gen,reco,pred):
    has_prob = False
    
    plt.figure(figsize=(15,7.5))

    plt.subplot(231)
    show_img(gen[img,:,:,0],"gen",cmap='Reds')
    
    plt.subplot(232)
    show_img(reco[img,:,:,0],"reco",cmap='Reds')

    plt.subplot(233)
    show_img(pred[img,:,:,0],"pred",cmap='Reds')

    plt.subplot(234)
    show_img(reco[img,:,:,0]-gen[img,:,:,0],"reco - gen",cmap='Blues')

    plt.subplot(235)
    show_img(pred[img,:,:,0]-gen[img,:,:,0],"pred - gen",cmap='Greens')

    plt.subplot(236)
    show_img(pred[img,:,:,0]-reco[img,:,:,0],"pred - reco",cmap='Reds')
    
    plt.tight_layout()
        
# -----------------------------------------------------------------------------
def scatter_pred(gen,reco,pred,mask=None,title=None,figsize=(15,7.5),rng=[0,0.1]):
    
    if mask is not None:
        gen = gen[:,mask]
        reco = reco[:,mask]
        pred = pred[:,mask]
    
    kwargs = dict(range=[rng,rng], bins=100, norm=LogNorm())
    plt.figure(figsize=figsize)
    plt.subplot(121)
    plt.hist2d(  gen.ravel(), reco.ravel(), cmap='Reds', **kwargs );
    plt.xlabel('gen')
    plt.ylabel('reco')
    if title is not None:
        plt.title(title)
    
    plt.subplot(122)
    plt.hist2d(  gen.ravel(), pred.ravel(), cmap='Blues', **kwargs );
    plt.xlabel('gen')
    plt.ylabel('pred')
    if title is not None:
        plt.title(title)
    
        
# -----------------------------------------------------------------------------
def distrib_pred(gen,reco,pred,mask=None,title=None,figsize=(7.5,7.5)):
    
    if mask is not None:
        gen = gen[:,mask].sum(axis=(1,2))
        reco = reco[:,mask].sum(axis=(1,2))
        pred = pred[:,mask].sum(axis=(1,2))
    else:
        gen = gen.sum(axis=(1,2,3))
        reco = reco.sum(axis=(1,2,3))
        pred = pred.sum(axis=(1,2,3))
    kwargs = dict(range=[0,2.], bins=100)
    plt.figure(figsize=figsize)
    plt.hist(  reco.ravel(), label='reco', **kwargs );
    plt.hist(  pred.ravel(), label='pred', alpha=0.5, **kwargs );
    plt.xlabel('$\sum p_T^i / p_T^{gen} (jet)$')
    plt.legend()
    plt.yscale('log')
    
# -----------------------------------------------------------------------------
def aggregate(imgs,mask=None,weights=None,moments=False,categories=None):#,quantiles=[]):
    if mask is not None:
        imgs = imgs[:,mask].sum(axis=(1,2))
    else:
        imgs = imgs.sum(axis=(1,2,3))

    if moments:
        if categories is not None:
            imgs = imgs.reshape(-1,1) * categories
            if weights is not None:
                weights = weights.reshape(-1,1) * categories
        mean = np.average(imgs,weights=weights,axis=0)
        mean2 = np.average(imgs**2,weights=weights,axis=0)
        return mean, np.sqrt( mean2 - mean**2 )
    return imgs

# -----------------------------------------------------------------------------
def get_moments(imgs,xvar,xbins,yvar=None,ybins=None,mask=None,weights=None):
    ibin = to_categorical(np.digitize(xvar,xbins)-1)
    bins = xbins
    if yvar is not None:
        ibin *= to_categorical(np.digitize(yvar,ybins)-1)
        bins = (xbins,ybins)
    mean,std = aggregate(imgs,mask,weights,moments=True,categories=ibin)
    return bins,mean,std

# -----------------------------------------------------------------------------
def show_moments(reco,pred,xvar,xbins,xlabel=None,title=None,weights=None,mask=None):
    _,reco_mean,reco_std = get_moments(reco,xvar,xbins,weights=weights,mask=mask)
    _,pred_mean,pred_std = get_moments(pred,xvar,xbins,weights=weights,mask=mask)
    ## _,gen_mean,gen_std = get_moments(gen,xvar,xbins,weights=weights,mask=mask)
    
    plt.plot(xbins,reco_mean,label='reco')
    plt.fill_between(xbins,reco_mean-reco_std,reco_mean+reco_std,alpha=0.5)
    
    plt.plot(xbins,pred_mean,label='pred')
    plt.fill_between(xbins,pred_mean-pred_std,pred_mean+pred_std,alpha=0.5)

    ## plt.plot(bins,gen_mean)
    ## plt.fill_between(bins,gen_mean-gen_std,gen_mean+gen_std,alpha=0.5)
    plt.legend()
    if title is not None:
        plt.title(title)
    if xlabel:
        plt.xlabel(xlabel)
    plt.ylabel("$\sum p_T^i / p^{gen}_T (jet) $")
    

# -----------------------------------------------------------------------------
def make_masks(radii,cumulative=False,npix=16,rad=0.3):
    x, y= np.ogrid[-npix:npix,-npix:npix]
    radius = np.sqrt( (x/npix*rad)**2 + (y/npix*rad)**2 )
    
    radii = list(sorted(set(list(radii)+[0.])))
    
    rings = list(zip(radii[:-1],radii[1:]))
    if cumulative:
        masks = [ radius < y  for x,y in rings  ]
    else:
        masks = [ (radius >= x) & (radius < y)  for x,y in rings  ]
    
    return rings,masks

# -----------------------------------------------------------------------------
def show_masks(masks,ncols=3,size=7.5):
    nrows = len(masks) // ncols + (len(masks) % ncols != 0)
    layout = 100*mrows+10*ncols
    print(layout)
    plt.figure(figsize=(size*ncols,size*nrows))
    for imask,mask in enumerate(ring_masks):
        plt.subplot(layout+imask+1)
        plt.imshow(mask)
    
    
