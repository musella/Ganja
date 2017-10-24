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
    print("Starting " + cfgname)
    with open(pwd+"/ganjatree_cfg_TMPL.py", "rt") as fin:
       with open(cfgname, "wt") as fout:
          for line in fin:
            if 'XXXJOBNUMBER' in line:
               fout.write(line.replace('XXXJOBNUMBER', str(ijob)))
            elif 'XXXFILES' in line:
               for ntp in range(0,min(ijobmax,len(inputfiles))):
                  ntpfile = inputfiles.pop()
                  if ntpfile != '':
                      fout.write('\''+ntpfile.strip()+'\',\n')
            else:
               fout.write(line)
 

    #inputfilename = pwd+"/"+dir+"/input/input_"+str(ijob)+".list"
    #inputfile = open(inputfilename,'w')


    #inputfile.close()

    ## prepare the script to run
    #outputname = dir+"/src/submit_"+str(ijob)+".src"
    #outputfile = open(outputname,'w')
    #outputfile.write('#!/bin/bash\n')
    #outputfile.write('export LANGUAGE=C\n')
    #outputfile.write('export LC_ALL=C\n')
    #outputfile.write('cd /afs/cern.ch/work/p/pandolf/CMSSW_5_3_32_Ganja/src/; eval `scramv1 runtime -sh` ; cd -\n')
    ##outputfile.write('cp '+pwd+'/SF_*.txt $WORKDIR\n')
    ##outputfile.write('cp '+pwd+'/Cert_*.txt $WORKDIR\n')
    ##outputfile.write('cp '+pwd+'/AK5PF_Uncertainty*.txt $WORKDIR\n')
    ##outputfile.write('cp '+pwd+'/GR_*.txt $WORKDIR\n')
    #outputfile.write('cd $WORKDIR\n')
    ##outputfile.write(pwd+'/'+application+" "+dataset+" "+inputfilename+" _"+str(ijob)+"\n")
    #outputfile.write(pwd+'/cmsRun ganjatree_cfg.py " "+dataset+" "+inputfilename+" "+str(ijob)+"\n")
    #outputfile.write('rm QG_QCD_Pt_15to3000_TuneZ2_Flat*.root\n')
    #outputfile.write('rm Pileup*.root\n')
    #outputfile.write('ls *.root | xargs -i scp -o BatchMode=yes -o StrictHostKeyChecking=no {} pccmsrm24:'+diskoutputmain+'/{}\n') 
    ##outputfile.write('cp *.root '+diskoutputmain2+'\n') 
    #outputfile.close
    #os.system("echo bsub -q "+queue+" -o "+dir+"/log/"+dataset+"_"+str(ijob)+".log source "+pwd+"/"+outputname)
    #os.system("bsub -q "+queue+" -o "+dir+"/log/"+dataset+"_"+str(ijob)+".log source "+pwd+"/"+outputname+" -copyInput="+dataset+"_"+str(ijob))
    ijob = ijob+1
    ##time.sleep(2.)
    continue
