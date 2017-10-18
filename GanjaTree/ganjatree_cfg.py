import FWCore.ParameterSet.Config as cms

process = cms.Process("Ganja")

process.load("FWCore.MessageService.MessageLogger_cfi")

process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(100) )
#process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.source = cms.Source("PoolSource",
    # replace 'myfile.root' with the source file you want to use
    fileNames = cms.untracked.vstring(
        'file:/afs/cern.ch/work/p/pandolf/public/QCD_Pt50to80_CMSSW_5_3_32.root'
    )
)

process.demo = cms.EDAnalyzer('GanjaTree'
)


process.p = cms.Path(process.demo)
