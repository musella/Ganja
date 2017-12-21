import ROOT as RT
RT.gSystem.AddIncludePath("-I$VIRTUAL_ENV/include ")
RT.gSystem.AddLinkedLibs("-L$VIRTUAL_ENV/lib -lfastjettools -lfastjet -lfastjetcontribfragile")
RT.gROOT.ProcessLine(".L SubstructureComputer.C++g")


import numpy as np 
imsize = 3
arr= np.ones( (10, imsize,imsize), dtype=np.float32 )
## arr[0] = 0.
etas = ( np.arange( imsize, dtype=np.float32 ).reshape(1,-1,imsize) + imsize / 2. ) * 0.3+ ( np.arange( 10 ).reshape(-1,1,1) -5. ) * 0.2
phis = ( np.arange( imsize, dtype=np.float32 ).reshape(1,imsize,-1) + imsize / 2. ) * 0.3
## c( arr, etas, phis )


import numpy as np

from pyjet._libpyjet import  PseudoJet

def img2p4(arr, etas, phis ):
    mom = arr * np.cosh( etas )
    px = arr * np.cos( phis )
    py = arr * np.sin( phis )
    pz = np.sqrt( mom*mom - px*px -py*py)
    mask = mom != 0
    return mom[mask].ravel(), px[mask].ravel(), py[mask].ravel(), pz[mask].ravel()

c = RT.SubstructureComputer()

for ijet in range(arr.shape[0]):
    p4 = img2p4( arr[ijet], etas[ijet], phis[0] )
    print(etas[ijet].mean())

    c( p4[0].shape[-1], p4[0].astype(np.float32, order='F'), p4[1].astype(np.float32, order='F'), p4[2].astype(np.float32, order='F'), p4[3].astype(np.float32, order='F') )
    
    print( c.ptD, c.axis1, c.axis2, c.tau21, c.tau1, c.tau2, c.tau3 )
    
