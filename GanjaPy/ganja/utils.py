import json

# -------------------------------------------------------------------------------------------
def read_nevents(fnames,base,index):

    idx=open(index)
    index = json.loads(idx.read())
    idx.close()
    
    nevents = reduce(lambda y,z: y+z, map(lambda x: index.get(x.replace(base,'')), fnames))
    
    return nevents
