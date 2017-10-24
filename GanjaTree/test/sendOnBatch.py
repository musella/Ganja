#! /usr/bin/env python
import os
import sys
import time
import re
# set parameters to use cmst3 batch 
#######################################
### usage  cmst3_submit_manyfilesperjob.py dataset njobs applicationName queue 
#######################################
if (len(sys.argv) != 3):
    print "usage sendOnBatch.py dataset filesPerJob"
    sys.exit(1)
dataset = sys.argv[1]
inputlist = "files_"+dataset+".txt"
#settingfile = "config/RSZZsettings.txt"
# choose among cmt3 8nm 1nh 8nh 1nd 1nw 
#queue = "cmst3"
#queue = "cms8nht3"
queue = "8nh"
#queue = "2nd"
#ijobmax = 40
ijobmax = int(sys.argv[2])
#eosdir = "/eos/cern.ch/user/p/pandolf/NTUPLES/" + dataset
#outputmain = castordir+output
# to write on local disks
################################################
#diskoutputdir = "/cmsrm/pc21_2/pandolf/MC/"+dataset
#diskoutputmain2 = eosdir
#diskoutputmain = diskoutputdir
#os.system("mkdir -p "+diskoutputmain2)
# prepare job to write on the cmst3 cluster disks
################################################
dir = "batch_" + dataset
os.system("mkdir -p "+dir)
os.system("mkdir -p "+dir+"/log/")
os.system("mkdir -p "+dir+"/input/")
os.system("mkdir -p "+dir+"/output/")
os.system("mkdir -p "+dir+"/src/")


#look for the current directory
#######################################
pwd = os.environ['PWD']
#######################################
inputListfile=open(inputlist)
inputfiles = inputListfile.readlines()
ijob=0

#copy the configuration in the actual run directory
#os.system("cp -r config "+dataset_name)

while (len(inputfiles) > 0):

    cfgname = dir+"/input/ganjatree_cfg_" + str(ijob) + ".py"
    with open(pwd+"/ganjatree_cfg_TMPL.py", "rt") as fin:
       with open(cfgname, "wt") as fout:
          for line in fin:
            if 'XXXOUTFILE' in line:
               fout.write(line.replace('XXXOUTFILE', pwd+"/"+dir+"/output/ganjaTree_"+str(ijob)+".root"))
            elif 'XXXFILES' in line:
               for ntp in range(0,min(ijobmax,len(inputfiles))):
                  ntpfile = inputfiles.pop()
                  if ntpfile != '':
                      fout.write('\''+ntpfile.strip()+'\',\n')
            else:
               fout.write(line)
 

    bsubcmd = "bsub -q "+queue+" -o "+pwd+"/"+dir+"/log/log_"+str(ijob)+".log cmsRun "+pwd+"/"+cfgname
    os.system("echo " + bsubcmd )
    os.system(bsubcmd )

    ijob = ijob+1
    ##time.sleep(2.)
    continue
