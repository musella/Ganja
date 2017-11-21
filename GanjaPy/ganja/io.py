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

from glob import glob

from tqdm import tqdm_notebook as tqdm
## from tqdm import tqdm

from . import utils
from .preprocessing import pixel_metrics, WeighterWithCache, normalize

from functools import reduce

from threading import Thread, Event, Lock
try:
    from Queue import Queue, Full, Empty
except:
    from queue import Queue, Full, Empty


# -------------------------------------------------------------------------------------------
def list_folders(folders,pattern='[0-9]*.json',**kwargs):
    return { folder:sorted(list_folder(folder,pattern,**kwargs))  for folder in folders }

# -------------------------------------------------------------------------------------------
def list_folder(folder,pattern,replace=None):
    pattern = os.path.join(folder,pattern)
    if replace is None:
        replace = "."+pattern.split(".")[-1]
    return list(map(lambda x: int(os.path.basename(x).replace(replace,'')), glob(pattern) ))

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

hd5_lock = Lock()

def read_dataset(folder,files,proc,xs,provenance=True,quiet=False,randomize_file=None,**kwargs):
    dfs = []
    nevents = 0.
    if not quiet:
        files = tqdm(files,desc=os.path.basename(folder),leave=False)
    for fil in files:
        try:
            jfil = open(os.path.join(folder,'%s.json' % fil))
            nevents += json.loads(jfil.read())['nevents']
            jfil.close()
        except:
            pass
        hd5_lock.acquire()
        df = pd.read_hdf(os.path.join(folder,'%s_info.hd5' % fil), **kwargs)
        hd5_lock.release()
        if provenance:
            df['file'] = fil
            df['row'] = df.index
        if randomize_file is not None:
            df['file_partition'] = np.random.choice(randomize_file,1)[0]
        dfs.append( df  )
    df = pd.concat(dfs)
    if nevents > 0.:
        df['weight'] = xs / nevents
    else:
        df['weight'] = 1.
    df['proc'] = proc
    return df

# -------------------------------------------------------------------------------------------
def read_datasets(inputs,cross_sections="data/cross_sections.json", quiet=False,**kwargs):

    dfs = []
    proc_ids = {}
    itr = enumerate(inputs.items())
    if not quiet:
        itr = tqdm(itr,desc='reading datasets')
    for proc,item in itr:
        folder,files = item
        try:
            xs = utils.read_xsection(folder,cross_sections)
        except:
            xs = 1.
        proc_ids[proc] = folder
        # print('reading %s' % folder)
        dfs.append( read_dataset(folder,files,proc,xs,quiet=quiet,**kwargs) )
    return proc_ids,pd.concat(dfs)


# -------------------------------------------------------------------------------------------
def read_images(folder,files,compressed=True,quiet=False,**kwargs):
    fils = []
    gens, recos = [], []
    if not quiet:
        files = tqdm(files,desc=os.path.basename(folder),leave=False) 
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
def unpack_images():
    pass

# -------------------------------------------------------------------------------------------
def read_datasets_images(inputs, quiet=False, **kwargs):
    fils = []
    proc_ids = {}
    itr = enumerate(inputs.items())
    if not quiet:
        tqdm(itr,desc='reading images')
    for proc,item in itr: 
        folder,files = item
        fils.append( read_images(folder,files,quiet=quiet,**kwargs) )
    return fils
    




# -------------------------------------------------------------------------------------------
## def make_partition(ipart,info,proc_ids,target):
def make_partition(ipart,part,proc_ids,procs,target,compress=False,**kwargs):
    if not 'mmap_mode' in kwargs: kwargs['mmap_mode'] ='r'
    part_inputs = {}
    gens = []
    recos = []
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



# -------------------------------------------------------------------------------------------
def make_partitions(df,npartitions,proc_ids,target,n_jobs=2,compress=False):
    
    df['partition'] = np.random.choice(np.arange(npartitions),df.shape[0])
    if 'file_partition' in df: df['partition'] += df['file_partition']*npartitions
    partitions = df.groupby(['partition','proc','file']).apply(lambda x: x['row'].values)
    parts = partitions.index.levels[0]
    procs = partitions.index.levels[1]
    
    print('Partitioning images')
    with Parallel(n_jobs=n_jobs) as parallel:
        metrics = parallel( delayed(make_partition)
                            (ipart,partitions[ipart],proc_ids,procs,target,
                                                    compress=compress,quiet=True) for ipart in tqdm(parts)
        )
        
    infos = []
    print('Partitioning infos')
    for ipart,info in tqdm(df.groupby('partition')):
        write_out(target,'',ipart,{'nevents':info.shape[0]},info,None,None)
        infos.append(info.shape)
            
    with open(target+'/proc_ids.json','w+') as rec:
        rec.write(json.dumps( proc_ids  ))
        rec.close()

# ------------------------------------------------------------------------------------------
class Worker:
    def __init__(self,in_queue,out_queue):
        self.in_queue = in_queue
        self.thread = None
        self.ret_queue = out_queue
        self.cancel = Event()
        
    def start(self):
        if self.thread is None:
            self.cancel.clear()
            self.thread = Thread(target=self)
            self.thread.start()

    def stop(self):
        if self.thread is not None:
            self.cancel.set()
            self.thread.join()
            self.thread = None
            
            
    def __call__(self):
        while True:
            if self.cancel.is_set():
                return
            ## print(self.in_queue.empty(),self.ret_queue.empty())
            try:
                task = self.in_queue.get(timeout=1.)
                if self.cancel.is_set():
                    return
                ret = task.get()
                while True:
                    try:
                        self.ret_queue.put(ret,timeout=1.)
                        break
                    except Full:
                        pass
                self.in_queue.task_done()
                self.in_queue.put(task)
            except Empty:
                pass
            except Exception as e:
                print(e)

# ------------------------------------------------------------------------------------------
class MultiReader:

    
    def __init__(self,inputs,ncache,nthreads,*args,**kwargs):

        self.readers = [  Reader({folder:[fil]},*args,**kwargs) for folder,files in inputs.items() for fil in files  ]

        ncache = min(ncache,len(self.readers))
        self.nthreads = min(max(1,ncache-1),nthreads)
        self.in_queue = Queue(len(self.readers)+self.nthreads)
        self.out_queue = Queue(max(1,ncache-self.nthreads))
        for reader in self.readers:
            self.in_queue.put(reader)
        self.workers = [ Worker(self.in_queue,self.out_queue) for thread in range(self.nthreads) ]
        print('Readers: %d Workers: %d Cache size: %d ' % ( len(self.readers), len(self.workers), self.out_queue.maxsize) )
        self.occupancy = []
        self.has_cond = len(kwargs.get("cond_names",[]))>0
        self.has_noise = kwargs.get("noise_dim",0)>0
        print('Has cond: ',self.has_cond)
        print('Has noise: ',self.has_noise)
        
    def start(self):
        for worker in self.workers: worker.start()

    def stop(self):
        for worker in self.workers: worker.stop()
        while not self.out_queue.empty():
            self.out_queue.get()
        
    def __call__(self,batch_size,win0=None,win1=None):
        def get_batch(xvals,yvals,weights,noise,cond,first,last):
            xret = [xvals[first:last,win0:win1,win0:win1]]
            if noise is not None:
                xret.append(noise[first:last])
            if cond is not None:
                xret.append(cond[first:last])
            return xret,yvals[first:last,win0:win1,win0:win1],weights[first:last]
        while True:
            for iread in range(len(self.readers)):
                self.occupancy.append(self.out_queue.qsize())
                read = self.out_queue.get()
                ## if len(read) == 3:
                ##     xvals,yvals,weights = read
                ##     cond = None
                ## else:
                ##     yvals,xvals,cond,weights = read
                xvals,yvals = read[:2]
                cond,noise = None,None
                if self.has_noise:
                    noise = read[2]
                if self.has_cond:
                    cond = read[2+self.has_noise]
                weights = read[-1]
                self.out_queue.task_done()
                nbatches = yvals.shape[0] // batch_size
                for ibatch in range(nbatches):
                    yield get_batch(xvals,yvals,weights,noise,cond,ibatch*batch_size,(ibatch+1)*batch_size)
                if yvals.shape[0] % batch_size != 0:
                    yield get_batch(xvals,yvals,weights,noise,cond,nbatches*batch_size,-1)
                
    
# ------------------------------------------------------------------------------------------
class Reader:

    def __init__(self,inputs,weights,gen_moments=None,reco_moments=None,
                 cond_names=[],cond_transform=None,cache_img=False,cache_cond=False,
                 compressed=False,shuffle=True,swap=False,noise_dim=0):
        self.inputs = inputs
        self.cache_img = cache_img
        self.cache_cond = cache_cond
        self.weights = weights
        self.gen_moments = gen_moments
        self.reco_moments = reco_moments
        self.cond_names = cond_names
        self.cond_transform = cond_transform
        self.compressed = compressed
        self.swap = swap
        self.shuffle = shuffle
        self.noise_dim = noise_dim
        self.cold_ = True
        self.weighter_ = None
        self.reco_ = None
        self.gen_ = None
        self.cond_ = None

    def get(self):
        info = None
        if self.cold_ or not self.cache_img or not self.cache_cond:
            if self.cold_ or not self.cache_cond and len(self.cond_names) > 0:
                _,info = read_datasets(self.inputs,provenance=False,quiet=True,
                                       columns=self.weights[0]+self.cond_names)
            if self.cold_:
                self.weighter_ = WeighterWithCache(info,*self.weights)
            
            images = read_datasets_images(self.inputs,compressed=self.compressed,quiet=True,
                                          mmap_mode='r')
            images = list(reduce(lambda y,z: y+z, images))
            if self.compressed:
                get_reco = lambda: list(map(lambda x: x['reco'], images))
            else:
                get_reco = lambda: images[1]
            if self.compressed:
                get_gen = lambda: list(map(lambda x: x['gen'], images))
            else:
                get_gen = lambda: images[0]
            if self.reco_moments is not None:
                reco = normalize(np.concatenate( get_reco() ),*self.reco_moments)
            else:
                reco = np.concatenate( get_reco() )
            if self.gen_moments is not None:
                gen = normalize(np.concatenate( get_gen() ),*self.gen_moments)
            else:
                gen = np.concatenate( get_gen() )
            if self.compressed:
                for img in images:
                    img.close()
            cond = None
            if len(self.cond_names) > 0 and (self.cold_ or not self.cache_cond):
                cond = info[self.cond_names].values.reshape(info.shape[0],1,-1)
                if self.cond_transform is not None:
                    self.cond_transform.transform(cond,copy=False)        
            
        if self.cache_img:
            if self.cold_:
                self.reco_ = reco
                self.gen_ = gen
            else:
                reco = self.reco_
                gen = self.gen_
        if self.cache_cond:
            if self.cold_:
                self.cond_ = cond
            else:
                cond = self.cond_
            
        weights = self.weighter_.get()
        self.cold_ = False

        ## if info is not None:
        ##     del info
        if self.swap:
            swap = gen
            gen = reco
            reco = swap
        rets = [gen,reco]
        if self.noise_dim>0:
            rets.append(np.random.normal(0,1,(gen.shape[0],1,self.noise_dim)))
        if cond is not None:
            rets.append(cond)
        rets.append(weights)
        if self.shuffle:
            return shuffle(*rets)
            ## if cond is not None:
            ##     return shuffle(gen,reco,cond,weights)
            ## else:
            ##     return shuffle(gen,reco,weights)
        ## return gen,reco,cond,weights
        return rets
