#! /usr/bin/env python
import os
import sys


if (len(sys.argv) != 2):
    print "usage sendFullProduction.py prodName"
    sys.exit(1)

prodName = sys.argv[1]


os.system('eos mkdir /eos/cms/store/user/pandolf/Ganja/'+prodName)
#os.system('python sendOnBatch.py '+prodName+' QCD_Pt_30to50 2')
#os.system('python sendOnBatch.py '+prodName+' QCD_Pt_50to80 5')
os.system('python sendOnBatch.py '+prodName+' QCD_Pt_80to120 2')
