// -*- C++ -*-
//
// Package:    GanjaTree
// Class:      GanjaTree
// 
/**\class GanjaTree GanjaTree.cc Ganja/GanjaTree/src/GanjaTree.cc

 Description: [one line class summary]

 Implementation:
     [Notes on implementation]
*/
//
// Original Author:  Francesco Pandolfi,32 3-B02,+41227676027,
//         Created:  Wed Oct 18 10:51:59 CEST 2017
// $Id$
//
//



#include "../interface/GanjaTree.h"

#include "FWCore/Framework/interface/ESHandle.h"

#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/JetReco/interface/GenJet.h"
#include "DataFormats/VertexReco/interface/Vertex.h"
#include "DataFormats/VertexReco/interface/VertexFwd.h"

#include "DataFormats/JetReco/interface/GenJetCollection.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"

#include "SimDataFormats/PileupSummaryInfo/interface/PileupSummaryInfo.h"

#include "TFile.h"
#include "TTree.h"
#include "TLorentzVector.h"


//
// constants, enums and typedefs
//

//
// static data member definitions
//

//
// constructors and destructor
//
GanjaTree::GanjaTree(const edm::ParameterSet& iConfig)

{
   //jecService( iConfig.getParameter<std::string>("jec")),


}


GanjaTree::~GanjaTree()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
GanjaTree::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{

   using namespace edm;
   using namespace reco;

   Handle<PFJetCollection> pfJets_h;
   iEvent.getByLabel( "ak5PFJets", pfJets_h);
   const PFJetCollection* pfJets = pfJets_h.product();

   Handle<GenJetCollection> genJets_h;
   iEvent.getByLabel( "ak5GenJets", genJets_h);
   const GenJetCollection* genJets = genJets_h.product(); 

   Handle<double> rhoHandle;
   iEvent.getByLabel("fixedGridRhoFastjetAll", rhoHandle);
   rho = (float) *rhoHandle;

   Handle< std::vector<Vertex> > vertexCollection;
   iEvent.getByLabel("offlinePrimaryVerticesWithBS", vertexCollection);

   Handle<std::vector<PileupSummaryInfo>> pupInfo;
   iEvent.getByLabel("slimmedAddPileupInfo", pupInfo);



   nVert = vertexCollection->size();
   nPU   = getPileUp(pupInfo);


   int maxJetsAnalyzed = 2;
   int nJetsAnalyzed   = 0;

   for ( GenJetCollection::const_iterator it = genJets->begin(); it != genJets->end() && nJetsAnalyzed<maxJetsAnalyzed; it++ ) {

     TLorentzVector p4_genJet;
     p4_genJet.SetPtEtaPhiM( it->pt(), it->eta(), it->phi(), it->mass() );


     // match to reco:
     float deltaRmax = 0.3;
     float deltaRbest = 999.;
     PFJet* pfJet=0;
     TLorentzVector p4_pfJet;

     for ( PFJetCollection::const_iterator it2 = pfJets->begin(); it2 != pfJets->end(); it2++ ) {

       p4_pfJet.SetPtEtaPhiM( it2->pt(), it2->eta(), it2->phi(), it2->mass() );

       float deltaR = p4_pfJet.DeltaR(p4_genJet);

       if( deltaR<deltaRbest ) {

         deltaRbest = deltaR;
         pfJet = (PFJet*)(&(*it2));

       }

     }

     if( deltaRbest > deltaRmax ) continue; // no match, no party

     pt   = p4_pfJet.Pt();
     eta  = p4_pfJet.Eta();
     phi  = p4_pfJet.Phi();
     mass = p4_pfJet.M();
 
     ptGen   = p4_genJet.Pt();
     etaGen  = p4_genJet.Eta();
     phiGen  = p4_genJet.Phi();
     massGen = p4_genJet.M();
 
     if( pfJet!=0 ) {

       std::vector<const reco::Candidate*> pfCands = pfJet->getJetConstituentsQuick();

       for( std::vector< const reco::Candidate* >::const_iterator iCand = pfCands.begin(); iCand!=pfCands.end(); ++iCand ) {

         //if( (*iCand)->pt()<1. ) continue;

         TLorentzVector p4_cand;
         p4_cand.SetPtEtaPhiM( (*iCand)->pt(), (*iCand)->eta(), (*iCand)->phi(), (*iCand)->mass() );

         float dRcandJet = p4_cand.DeltaR(p4_pfJet);
         if( dRcandJet > drMax ) continue;

         float dEtaCandJet = p4_cand.Eta()-p4_pfJet.Eta();
         float dPhiCandJet = p4_cand.DeltaPhi(p4_pfJet);

         this->fillImage( p4_cand.Pt()/p4_pfJet.Pt(), dEtaCandJet, dPhiCandJet, nPix_1D, pixelSize, jetImageReco );

       } // for cands

     } // if PFJet ! = 0



     nJetsAnalyzed++;


   } // for genJets




}


void GanjaTree::fillImage( float pt, float dEta, float dPhi, int nPix_1D, float pixelSize, float* image ) {

  dEta /= pixelSize;
  dPhi /= pixelSize;
  dEta += (float)nPix_1D/2.;
  dPhi += (float)nPix_1D/2.;

  int etaBin = (int)dEta;
  int phiBin = (int)dPhi*nPix_1D;

  if( etaBin < 0 ) {
    std::cout << "WARNING!! dEta=" << dEta << std::endl;
    exit(1);
  }
  if( phiBin < 0 ) {
    std::cout << "WARNING!! dPhi=" << dPhi << std::endl;
    exit(11);
  }

  image[ etaBin + phiBin ] += pt;

}


int GanjaTree::getPileUp( edm::Handle<std::vector<PileupSummaryInfo>>& pupInfo ) {

  if(!pupInfo.isValid()) return -1;
  auto PVI = pupInfo->begin();
  while(PVI->getBunchCrossing() != 0 && PVI != pupInfo->end()) ++PVI;
  if(PVI != pupInfo->end()) return PVI->getPU_NumInteractions();
  else return -1;

} 


// ------------ method called once each job just before starting event loop  ------------
void 
GanjaTree::beginJob()
{


  file = TFile::Open("ganjaNtuple.root", "recreate" );
  file->cd();

  tree = new TTree( "ganjaTree", "" );

  //tree = fs->make<TTree>("qgMiniTuple","qgMiniTuple");
  tree->Branch("event" , &event, "event/I");
  tree->Branch("run"   , &run  , "run/I");
  tree->Branch("lumi"  , &lumi , "lumi /I");
  tree->Branch("rho"   , &rho  , "rho/I");
  tree->Branch("nVert" , &nVert, "nVert/I");
  tree->Branch("nPU"   , &nPU  , "nPU/I");
  tree->Branch("pt"    , &pt   , "pt/F");
  tree->Branch("eta"   , &eta  , "eta/F");
  tree->Branch("phi"   , &phi  , "phi/F");
  tree->Branch("mass"  , &mass , "mass/F");
  tree->Branch("ptGen"    , &ptGen   , "ptGen/F");
  tree->Branch("etaGen"   , &etaGen  , "etaGen/F");
  tree->Branch("phiGen"   , &phiGen  , "phiGen/F");
  tree->Branch("massGen"  , &massGen , "massGen/F");
  tree->Branch("btag"  , &btag , "btag/F");
  tree->Branch("partonId"  , &partonId , "partonId/I");
  tree->Branch("jetIdLevel"  , &jetIdLevel , "jetIdLevel/I");
  tree->Branch("pixelSize", &pixelSize, "pixelSize/F");
  tree->Branch("drMax", &drMax, "drMax/F");
  tree->Branch("nPix", &nPix, "nPix/I");
  tree->Branch("jetImageReco",jetImageReco, "jetImageReco[nPix]/F");
  tree->Branch("jetImageGen" ,jetImageGen , "jetImageGen[nPix]/F");



}

// ------------ method called once each job just after ending the event loop  ------------
void 
GanjaTree::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
GanjaTree::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
GanjaTree::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
GanjaTree::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
GanjaTree::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GanjaTree::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GanjaTree);
