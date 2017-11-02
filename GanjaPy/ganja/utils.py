import json
import os

from GAN.utils import *

# -------------------------------------------------------------------------------------------
def read_nevents(fnames,base,index):

    idx=open(index)
    index = json.loads(idx.read())
    idx.close()
    
    nevents = reduce(lambda y,z: y+z, map(lambda x: index.get(os.path.relpath(x,base)), fnames))
    
    return nevents


# -------------------------------------------------------------------------------------------
def read_xsection(folder,index):
    idx=open(index)
    index = json.loads(idx.read())
    idx.close()

    return index[os.path.basename(folder)]
