#! /usr/bin/env python
import os
import sys


if (len(sys.argv) != 2):
    print "usage sendFullProduction.py prodName"
    sys.exit(1)

prodName = sys.argv[1]


os.system('eos mkdir /eos/cms/store/user/pandolf/Ganja/'+prodName)
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_30to50 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_50to80 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_80to120 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_120to170 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_170to300 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_300to470 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_470to600 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_600to800 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_800to1000 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_1000to1400 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_1400to1800 2')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_1800 2')
