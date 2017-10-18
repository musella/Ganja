// -*- C++ -*-
//
// Package:    GanjaNtuplizer
// Class:      GanjaNtuplizer
// 
/**\class GanjaNtuplizer GanjaNtuplizer.cc Ganja/GanjaNtuplizer/src/GanjaNtuplizer.cc

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



#include "../interface/GanjaNtuplizer.h"

#include "FWCore/Framework/interface/ESHandle.h"

#include "DataFormats/JetReco/interface/PFJet.h"
#include "DataFormats/JetReco/interface/GenJet.h"

#include "DataFormats/JetReco/interface/GenJetCollection.h"
#include "DataFormats/JetReco/interface/PFJetCollection.h"

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
GanjaNtuplizer::GanjaNtuplizer(const edm::ParameterSet& iConfig)

{
   //jecService( iConfig.getParameter<std::string>("jec")),


}


GanjaNtuplizer::~GanjaNtuplizer()
{
 
   // do anything here that needs to be done at desctruction time
   // (e.g. close files, deallocate resources etc.)

}


//
// member functions
//

// ------------ method called for each event  ------------
void
GanjaNtuplizer::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{

   using namespace edm;
   using namespace reco;

   Handle<PFJetCollection> pfJets_h;
   iEvent.getByLabel( "ak5PFJets", pfJets_h);
   const PFJetCollection* pfJets = pfJets_h.product();

   Handle<GenJetCollection> genJets_h;
   iEvent.getByLabel( "ak5GenJets", genJets_h);
   const GenJetCollection* genJets = genJets_h.product(); 


   int maxJetsAnalyzed = 2;
   int nJetsAnalyzed   = 0;

   for ( GenJetCollection::const_iterator it = genJets->begin(); it != genJets->end() && nJetsAnalyzed<maxJetsAnalyzed; it++ ) {

     TLorentzVector p4_genJet;
     p4_genJet.SetPtEtaPhiM( it->pt(), it->eta(), it->phi(), it->mass() );


     // match to reco:
     float deltaRmax = 0.3;
     float deltaRbest = 999.;
     PFJet* pfJet=0;
     //TLorentzVector pfJet;

     for ( PFJetCollection::const_iterator it2 = pfJets->begin(); it2 != pfJets->end(); it2++ ) {

       TLorentzVector p4_pfJet;
       p4_pfJet.SetPtEtaPhiM( it2->pt(), it2->eta(), it2->phi(), it2->mass() );


       float deltaR = p4_pfJet.DeltaR(p4_genJet);

       if( deltaR<deltaRbest ) {

         deltaRbest = deltaR;
         pfJet = (PFJet*)(&(*it2));

       }

     }

     if( deltaRbest > deltaRmax ) continue; // no match, no party
 
     if( pfJet!=0 ) {

       std::vector<const reco::Candidate*> pfCands = pfJet->getJetConstituentsQuick();

       for( std::vector< const reco::Candidate* >::const_iterator iCand = pfCands.begin(); iCand!=pfCands.end(); ++iCand ) {

         //if( (*iCand)->pt()<1. ) continue;

         TLorentzVector p4_cand;
         p4_cand.SetPtEtaPhiM( (*iCand)->pt(), (*iCand)->eta(), (*iCand)->phi(), (*iCand)->mass() );

         float dRcandJet = p4_cand.DeltaR(p4_pfJet);

         float dEtaCandJet = p4_cand.Eta()-p4_pfJet.Eta();
         float dPhiCandJet = p4_cand.DeltaPhi(p4_pfJet);

         fillImage( p4_cand.pt()/pfJet.pt(), dEtaCandJet, dPhiCandJet, nPix_1D, pixelSize, jetImageReco );

       } // for cands

     } // if PFJet ! = 0



     nJetsAnalyzed++;


   } // for genJets




}


void GanjaNtuplizer::fillImage( float pt, float dEta, float dPhi, int nPix_1D, float pixelSize, float* image ) {

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



// ------------ method called once each job just before starting event loop  ------------
void 
GanjaNtuplizer::beginJob()
{


  tree = fs->make<TTree>("qgMiniTuple","qgMiniTuple");
  tree->Branch("event" , &event, "event/I");
  tree->Branch("run"   , &run  , "run/I");
  tree->Branch("lumi"  , &lumi , "lumi /I");
  tree->Branch("rho"   , &rho  , "run/I");
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
  tree->Branch("nch",&nch,"nch/I");
  tree->Branch("nnh",&nnh,"nnh/I");
  tree->Branch("nph",&nph,"nph/I");
  tree->Branch("pt_ch",pt_ch,"pt_ch[nch]/F");
  tree->Branch("pt_nh",pt_nh,"pt_nh[nnh]/F");
  tree->Branch("pt_ph",pt_ph,"pt_ph[nph]/F");
  tree->Branch("dr_ch",dr_ch,"dr_ch[nch]/F");
  tree->Branch("dr_nh",dr_nh,"dr_nh[nnh]/F");
  tree->Branch("dr_ph",dr_ph,"dr_ph[nph]/F");
  tree->Branch("nDRch", &nDRch, "nDRch/I");
  tree->Branch("nDRnh", &nDRnh, "nDRnh/I");
  tree->Branch("nDRph", &nDRph, "nDRph/I");
  tree->Branch("deltaRch",deltaRch, "deltaRch[nDRch]/F");
  tree->Branch("deltaRph",deltaRph, "deltaRph[nDRph]/F");
  tree->Branch("pixelSize", &pixelSize, "pixelSize/F");
  tree->Branch("drMax", &drMax, "drMax/F");
  tree->Branch("nPix", &nPix, "nPix/I");
  tree->Branch("jetImageReco",jetImageReco, "jetImageReco[nPix]/F");
  tree->Branch("jetImageGen" ,jetImageGen , "jetImageGen[nPix]/F");



}

// ------------ method called once each job just after ending the event loop  ------------
void 
GanjaNtuplizer::endJob() 
{
}

// ------------ method called when starting to processes a run  ------------
void 
GanjaNtuplizer::beginRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a run  ------------
void 
GanjaNtuplizer::endRun(edm::Run const&, edm::EventSetup const&)
{
}

// ------------ method called when starting to processes a luminosity block  ------------
void 
GanjaNtuplizer::beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method called when ending the processing of a luminosity block  ------------
void 
GanjaNtuplizer::endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&)
{
}

// ------------ method fills 'descriptions' with the allowed parameters for the module  ------------
void
GanjaNtuplizer::fillDescriptions(edm::ConfigurationDescriptions& descriptions) {
  //The following says we do not know what parameters are allowed so do no validation
  // Please change this to state exactly what you do use, even if it is no parameters
  edm::ParameterSetDescription desc;
  desc.setUnknown();
  descriptions.addDefault(desc);
}

//define this as a plug-in
DEFINE_FWK_MODULE(GanjaNtuplizer);
