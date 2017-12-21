import FWCore.ParameterSet.Config as cms

process = cms.Process("Ganja")

process.load("FWCore.MessageService.MessageLogger_cfi")
process.MessageLogger.cerr.FwkReport.reportEvery = 100



process.maxEvents = cms.untracked.PSet( input = cms.untracked.int32(-1) )

process.TFileService = cms.Service("TFileService",
      fileName = cms.string("XXXOUTFILE"),
      closeFileFast = cms.untracked.bool(True)
)


process.source = cms.Source("PoolSource",
    fileNames = cms.untracked.vstring(
XXXFILES
    )
)

process.ganja = cms.EDAnalyzer('GanjaTree'
)


process.p = cms.Path(process.ganja)
