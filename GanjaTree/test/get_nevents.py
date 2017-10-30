#!/usr/bin/env python

import sys

base = sys.argv[1]
cfg = sys.argv[2]

execfile(cfg)#'/mnt/t3nfs01/data01/shome/pandolf/CMSSW_5_3_32_Ganja/src/Ganja/GanjaTree/test/prod_oct25_v0/QCD_Pt_80to120/input/ganjatree_cfg_0.py')

# print(process.source)

import ROOT as RT

tot_evts = 0
for fil in process.source.fileNames:
    fin=RT.TFile.Open(fil)
    tot_evts += fin.Get('Events').GetEntriesFast()
    fin.Close()

print('"%s": %d' % ( cfg.replace(base,'').replace("input/ganjatree_cfg","output/ganjaTree").replace(".py",".root"), tot_evts ) )
    
