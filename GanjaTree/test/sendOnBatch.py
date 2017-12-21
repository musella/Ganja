#! /usr/bin/env python
import os
import sys
import time
import re
# set parameters to use cmst3 batch 
#######################################
### usage  cmst3_submit_manyfilesperjob.py dataset njobs applicationName queue 
#######################################
if (len(sys.argv) != 4):
    print "usage sendOnBatch.py prodName dataset filesPerJob"
    sys.exit(1)
prodName = sys.argv[1]
dataset  = sys.argv[2]
ijobmax = int(sys.argv[3])

inputlist = "files_"+dataset+".txt"

queue = "8nh"

pwd = os.environ['PWD']

eosdir = "/eos/cms/store/user/pandolf/Ganja/" + prodName + "/" + dataset
os.system("eos mkdir " + eosdir) 

dir = "prod_" + prodName + "/" + dataset
os.system("mkdir -p "+dir)
os.system("mkdir -p "+dir+"/log/")
os.system("mkdir -p "+dir+"/input/")
os.system("mkdir -p "+dir+"/output/")
os.system("mkdir -p "+dir+"/src/")


inputListfile=open(inputlist)
inputfiles = inputListfile.readlines()
ijob=0


while (len(inputfiles) > 0):

    outfile = "ganjaTree_"+str(ijob)+".root"
    
    cfgname = dir+"/input/ganjatree_cfg_" + str(ijob) + ".py"
    with open(pwd+"/ganjatree_cfg_TMPL.py", "rt") as fin:
       with open(cfgname, "wt") as fout:
          for line in fin:
            if 'XXXOUTFILE' in line:
               fout.write(line.replace('XXXOUTFILE', outfile))
               #fout.write(line.replace('XXXOUTFILE', "root://eoscms.cern.ch//"+eosdir+"/ganjaTree_"+str(ijob)+".root"))
               #fout.write(line.replace('XXXOUTFILE', pwd+"/"+dir+"/output/ganjaTree_"+str(ijob)+".root"))
            elif 'XXXFILES' in line:
               for ntp in range(0,min(ijobmax,len(inputfiles))):
                  ntpfile = inputfiles.pop()
                  if ntpfile != '':
                      fout.write('\''+ntpfile.strip()+'\',\n')
            else:
               fout.write(line)
 
    # prepare the script to run
    outputname = dir+"/src/submit_"+str(ijob)+".src"
    outputfile = open(outputname,'w')
    outputfile.write('#!/bin/bash\n')
    outputfile.write('export SCRAM_ARCH=slc6_amd64_gcc472\n')
    outputfile.write('cd /afs/cern.ch/work/p/pandolf/CMSSW_5_3_32_Ganja/src/; eval `scramv1 runtime -sh` ; cd -\n')
    outputfile.write('cd $WORKDIR\n')
    outputfile.write('cmsRun '+pwd+'/'+cfgname+'\n')
    outputfile.write('cp '+outfile+' '+eosdir+'\n')
    outputfile.write('rm '+outfile+'\n')
    #outputfile.write('ls '+analyzerType+'*.root | xargs -i scp -o BatchMode=yes -o StrictHostKeyChecking=no {} pccmsrm25:'+diskoutputmain+'/{}\n') 
    #outputfile.write('cp *.root '+diskoutputmain2+'\n') 
    outputfile.close
 

    bsubcmd = "bsub -q "+queue+" -o "+pwd+"/"+dir+"/log/log_"+str(ijob)+".log source "+pwd+"/"+outputname

    os.system("echo " + bsubcmd )
    os.system(bsubcmd )

    ijob = ijob+1
    ##time.sleep(2.)
    continue
