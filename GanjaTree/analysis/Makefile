CC = g++
CFLAGS = -Wall -c -g -fpermissive 

ROOFIT_INCLUDE := $(shell cd $(CMSSW_BASE); scram tool info roofitcore | grep INCLUDE= | sed 's|INCLUDE=||')
ROOFIT_LIBDIR := $(shell cd $(CMSSW_BASE); scram tool info roofitcore | grep LIBDIR= | sed 's|LIBDIR=||')

INCLUDES = -I. -I.. -I$(ROOTSYS)/include -I$(ROOFIT_INCLUDE)/ -I$(CMSSW_BASE)/src

ROOTSYS ?= ERROR_RootSysIsNotDefined

ROOTFLAG = `${ROOTSYS}/bin/root-config --cflags --libs`

EXTRALIBS := -L$(ROOTSYS)/lib -L$(ROOFIT_LIBDIR)/ 
#-L$(CMSSW_BASE)/lib/slc6_amd64_gcc491/ -L/cvmfs/cms.cern.ch/slc6_amd64_gcc491/cms/cmssw/CMSSW_7_4_7/lib/slc6_amd64_gcc491/ -lHtml -lMathCore -lGenVector -lMinuit -lEG  -lPhysics -L/cvmfs/cms.cern.ch/slc6_amd64_gcc491/external/zlib/1.2.8-cms/lib -lz -lTreePlayer -lRooFitCore -lRooFit



drawJetImages: drawJetImages.cpp GanjaCommon.o
	$(CC) -Wall $(INCLUDES) -o drawJetImages drawJetImages.cpp GanjaCommon.o $(ROOTFLAG) $(EXTRALIBS)



GanjaCommon.o: ../src/GanjaCommon.cc
	$(CC) -Wall $(INCLUDES) -c ../src/GanjaCommon.cc $(ROOTFLAG) $(EXTRALIBS)
