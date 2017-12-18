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

#include "CommonTools/UtilAlgos/interface/TFileService.h"

#include "TFile.h"
#include "TTree.h"
#include "TLorentzVector.h"

#include <cmath>

#include "fastjet/ClusterSequence.hh"
#include "fastjet/ClusterSequenceArea.hh"
#include "fastjet/AreaDefinition.hh"
#include "fastjet/GhostedAreaSpec.hh"
#include "fastjet/PseudoJet.hh"
#include "fastjet/JetDefinition.hh"

#include "fastjet/contrib/Nsubjettiness.hh"
#include "fastjet/contrib/Njettiness.hh"
#include "fastjet/contrib/NjettinessPlugin.hh"


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
   iEvent.getByLabel("addPileupInfo", pupInfo);


   event =   (int) iEvent.id().event();
   run   =   (int) iEvent.id().run();
   lumi  =   (int) iEvent.id().luminosityBlock();


   nVert = vertexCollection->size();
   nPU   = getPileUp(pupInfo);


   //// Defining Nsubjettiness parameters
   //double beta = 1.0; // power for angular dependence, e.g. beta = 1 --> linear k-means, beta = 2 --> quadratic/classic k-means
   //double R0 = 1.0; // Characteristic jet radius for normalization	      
   //double Rcut = 1.0; // maximum R particles can be from axis to be included in jet	      
 
   fastjet::contrib::Nsubjettiness nSub1KT(1, fastjet::contrib::OnePass_KT_Axes(), fastjet::contrib::UnnormalizedMeasure(1));
   fastjet::contrib::Nsubjettiness nSub2KT(2, fastjet::contrib::OnePass_KT_Axes(), fastjet::contrib::UnnormalizedMeasure(1));

   fastjet::JetDefinition jetDef(fastjet::antikt_algorithm, 0.4);    
   int activeAreaRepeats = 1;
   double ghostArea = 0.01;
   double ghostEtaMax = 7.0;
   fastjet::GhostedAreaSpec fjActiveArea(ghostEtaMax,activeAreaRepeats,ghostArea);
   fastjet::AreaDefinition fjAreaDefinition( fastjet::active_area, fjActiveArea );


   int maxJetsAnalyzed = 2;
   int nJetsAnalyzed   = 0;

   for ( GenJetCollection::const_iterator it = genJets->begin(); it != genJets->end() && nJetsAnalyzed<maxJetsAnalyzed; it++ ) {


     // initialize jet image:
     for( unsigned i=0; i<nIMGMAX; ++i ) {
       jetImageReco[i] = 0.;
       jetImageGen [i] = 0.;
     }

     TLorentzVector p4_genJet;
     p4_genJet.SetPtEtaPhiM( it->pt(), it->eta(), it->phi(), it->mass() );

     GenJet* genJet = (GenJet*)(&(*it));


     // match to reco:
     float deltaRmax = 0.3;
     float deltaRbest = 999.;
     PFJet* pfJet=0;
     TLorentzVector p4_pfJet;

     for ( PFJetCollection::const_iterator it2 = pfJets->begin(); it2 != pfJets->end(); it2++ ) {

       TLorentzVector p4_thisJet;
       p4_thisJet.SetPtEtaPhiM( it2->pt(), it2->eta(), it2->phi(), it2->mass() );

       float deltaR = p4_thisJet.DeltaR(p4_genJet);

       if( deltaR<deltaRbest ) {

         deltaRbest = deltaR;
         pfJet = (PFJet*)(&(*it2));
         p4_pfJet.SetPtEtaPhiM( it2->pt(), it2->eta(), it2->phi(), it2->mass() );

       }

     }

     if( deltaRbest > deltaRmax ) { // no match

       pt   = 0.;
       eta  = -999.;
       phi  = 0.;
       mass = 0.;

     } else {
 
       pt   = p4_pfJet.Pt();
       eta  = p4_pfJet.Eta();
       phi  = p4_pfJet.Phi();
       mass = p4_pfJet.M();

     }
 
     ptGen   = p4_genJet.Pt();
     etaGen  = p4_genJet.Eta();
     phiGen  = p4_genJet.Phi();
     massGen = p4_genJet.M();
 
     if( pfJet!=0 ) {

       //getMatchedGenParticle(&*jet, genParticles);
       //partonId = (matchedJet) ? matchedGenParticle->pdgId() : 0;

       std::vector<const reco::Candidate*> pfCands = pfJet->getJetConstituentsQuick();

       float sum_weight   = 0.;
       float sum_deta     = 0.; 
       float sum_dphi     = 0.; 
       float sum_deta2    = 0.; 
       float sum_dphi2    = 0.;
       float sum_detadphi = 0.;
       float sum_pt       = 0.;

       for( std::vector< const reco::Candidate* >::const_iterator iCand = pfCands.begin(); iCand!=pfCands.end(); ++iCand ) {

         //if( (*iCand)->pt()<1. ) continue;

         TLorentzVector p4_cand;
         p4_cand.SetPtEtaPhiM( (*iCand)->pt(), (*iCand)->eta(), (*iCand)->phi(), (*iCand)->mass() );

         float dEtaCandJet = p4_cand.Eta()-p4_genJet.Eta();
         float dPhiCandJet = p4_cand.DeltaPhi(p4_genJet);

         dEtaCandJet = std::copysign(std::min(drMax,std::abs(dEtaCandJet)),dEtaCandJet);
         dPhiCandJet = std::copysign(std::min(drMax,std::abs(dPhiCandJet)),dPhiCandJet);
          

         this->fillImage( p4_cand.Pt()/p4_genJet.Pt(), dEtaCandJet, dPhiCandJet, nPix_1D, pixelSize, jetImageReco );

         float p2 = p4_cand.Pt()*p4_cand.Pt();
         sum_pt       += p4_cand.Pt();
         sum_weight   += p2;
         sum_deta     += dEtaCandJet*p2;
         sum_dphi     += dPhiCandJet*p2;
         sum_deta2    += dEtaCandJet*dEtaCandJet*p2;
         sum_detadphi += dEtaCandJet*dPhiCandJet*p2;
         sum_dphi2    += dPhiCandJet*dPhiCandJet*p2;

       } // for cands
       
       computeQGvars( sum_weight, sum_pt, sum_deta, sum_dphi, sum_deta2, sum_dphi2, sum_detadphi, axis1, axis2, ptD );

     } // if PFJet ! = 0


     std::vector<const reco::Candidate*> genCands = genJet->getJetConstituentsQuick();
     fastjet::PseudoJet curjet;  
     std::vector< fastjet::PseudoJet > newparticles;

     float gensum_weight   = 0.;
     float gensum_deta     = 0.; 
     float gensum_dphi     = 0.; 
     float gensum_deta2    = 0.; 
     float gensum_dphi2    = 0.;
     float gensum_detadphi = 0.;
     float gensum_pt       = 0.;


     int iCandGen=0;

     for( std::vector< const reco::Candidate* >::const_iterator iCand = genCands.begin(); iCand!=genCands.end(); ++iCand ) {

       //if( (*iCand)->pt()<1. ) continue;
       newparticles.push_back( fastjet::PseudoJet( (*iCand)->px(), (*iCand)->py(), (*iCand)->pz(), (*iCand)->energy() ) );

       TLorentzVector p4_cand;
       p4_cand.SetPtEtaPhiM( (*iCand)->pt(), (*iCand)->eta(), (*iCand)->phi(), (*iCand)->mass() );

       float dEtaCandJet = p4_cand.Eta()-p4_genJet.Eta();
       float dPhiCandJet = p4_cand.DeltaPhi(p4_genJet);
       dEtaCandJet = std::copysign(std::min(drMax,std::abs(dEtaCandJet)),dEtaCandJet);
       dPhiCandJet = std::copysign(std::min(drMax,std::abs(dPhiCandJet)),dPhiCandJet);

       this->fillImage( p4_cand.Pt()/p4_genJet.Pt(), dEtaCandJet, dPhiCandJet, nPix_1D, pixelSize, jetImageGen );

       float p2 = p4_cand.Pt()*p4_cand.Pt();
       gensum_pt       += p4_cand.Pt();
       gensum_weight   += p2;
       gensum_deta     += dEtaCandJet*p2;
       gensum_dphi     += dPhiCandJet*p2;
       gensum_deta2    += dEtaCandJet*dEtaCandJet*p2;
       gensum_detadphi += dEtaCandJet*dPhiCandJet*p2;
       gensum_dphi2    += dPhiCandJet*dPhiCandJet*p2;

       iCandGen++;

     } // for cands

     computeQGvars( gensum_weight, gensum_pt, gensum_deta, gensum_dphi, gensum_deta2, gensum_dphi2, gensum_detadphi, axis1Gen, axis2Gen, ptDGen );

     fastjet::ClusterSequenceArea* thisClustering = new fastjet::ClusterSequenceArea(newparticles, jetDef, fjAreaDefinition);
     std::vector<fastjet::PseudoJet> out_jets = sorted_by_pt(thisClustering->inclusive_jets(0.01));        
         
     // fill into curjet
     curjet = out_jets[0];

     tau1Gen  = nSub1KT(curjet);        
     tau2Gen  = nSub2KT(curjet);        

     tree->Fill();
     nJetsAnalyzed++;
     event = -event; //second jet has negative event number


   } // for genJets


  

}


void GanjaTree::fillImage( float ptRatio, float dEta, float dPhi, int nPix_1D, float pixelSize, float* image ) {

  dEta /= pixelSize;
  dPhi /= pixelSize;
  dEta += (float)nPix_1D/2.;
  dPhi += (float)nPix_1D/2.;

  int etaBin = (int)std::round(dEta);
  int phiBin = (int)std::round(dPhi)*nPix_1D;

  if( etaBin < 0 ) {
    std::cout << "WARNING!! dEta=" << dEta << std::endl;
    exit(1);
  }
  if( phiBin < 0 ) {
    std::cout << "WARNING!! dPhi=" << dPhi << std::endl;
    exit(11);
  }

  image[ etaBin + phiBin ] += ptRatio;

}


void GanjaTree::computeQGvars( float sum_weight, float sum_pt, float sum_deta, float sum_dphi, float sum_deta2, float sum_dphi2, float sum_detadphi, float& a_axis1, float& a_axis2, float& a_ptD ) {

  float a = 0., b = 0., c = 0.;
  float ave_deta = 0., ave_dphi = 0., ave_deta2 = 0., ave_dphi2 = 0.;
  if(sum_weight > 0){
    ave_deta  = sum_deta/sum_weight;
    ave_dphi  = sum_dphi/sum_weight;
    ave_deta2 = sum_deta2/sum_weight;
    ave_dphi2 = sum_dphi2/sum_weight;
    a         = ave_deta2 - ave_deta*ave_deta;                          
    b         = ave_dphi2 - ave_dphi*ave_dphi;                          
    c         = -(sum_detadphi/sum_weight - ave_deta*ave_dphi);                
  }
  float delta = sqrt(fabs((a-b)*(a-b)+4*c*c));
  a_axis2 = (a+b-delta > 0 ?  sqrt(0.5*(a+b-delta)) : 0);
  a_axis1 = (a+b+delta > 0 ?  sqrt(0.5*(a+b+delta)) : 0);
  a_ptD   = (sum_weight > 0 ? sqrt(sum_weight)/sum_pt : 0);

  a_axis2 = -log(a_axis2);
  a_axis1 = -log(a_axis1);

}


int GanjaTree::getPileUp( edm::Handle<std::vector<PileupSummaryInfo>>& pupInfo ) {

  if(!pupInfo.isValid()) return -1;
  auto PVI = pupInfo->begin();
  while(PVI->getBunchCrossing() != 0 && PVI != pupInfo->end()) ++PVI;
  if(PVI != pupInfo->end()) return PVI->getPU_NumInteractions();
  else return -1;

} 



//reco::GenParticleCollection::const_iterator GanjaTree::getMatchedGenParticle(const TLorentzVector& jet, edm::Handle<reco::GenParticleCollection>& genParticles ) {
//
//  float deltaRmin = 999.;
//  auto matchedGenParticle = genParticles->end();
//
//  for ( auto genParticle = genParticles->begin(); genParticle != genParticles->end(); ++genParticle ) {
//
//    if( !genParticle->isHardProcess() ) continue; // This status flag is exactly the pythia8 status-23 we need (i.e. the same as genParticles->status() == 23), probably also ok to use for other generators
//    if( abs(genParticle->pdgId()) > 5 && abs(genParticle->pdgId() != 21) ) continue; // only udscb quarks and gluons
//
//    float thisDeltaR = reco::deltaR(*genParticle, *jet);
//    if(thisDeltaR < deltaRmin && thisDeltaR < deltaRcut){
//      deltaRmin = thisDeltaR;
//      matchedGenParticle = genParticle;
//    }
//  }
//  return matchedGenParticle;
//}




// ------------ method called once each job just before starting event loop  ------------
void 
GanjaTree::beginJob()
{


  //file = TFile::Open("ganjaTree.root", "recreate" );
  //file->cd();

  //tree = new TTree( "ganjaTree", "" );

  tree = fs->make<TTree>("ganjaTree","ganjaTree");
  tree->Branch("event" , &event, "event/I");
  tree->Branch("run"   , &run  , "run/I");
  tree->Branch("lumi"  , &lumi , "lumi /I");
  tree->Branch("rho"   , &rho  , "rho/F");
  tree->Branch("nVert" , &nVert, "nVert/I");
  tree->Branch("nPU"   , &nPU  , "nPU/I");
  tree->Branch("pt"    , &pt   , "pt/F");
  tree->Branch("eta"   , &eta  , "eta/F");
  tree->Branch("phi"   , &phi  , "phi/F");
  tree->Branch("mass"  , &mass , "mass/F");
  tree->Branch("axis1" , &axis1, "axis1/F");
  tree->Branch("axis2" , &axis2, "axis2/F");
  tree->Branch("ptD"   , &ptD  , "ptD/F");
  tree->Branch("ptGen"    , &ptGen   , "ptGen/F");
  tree->Branch("etaGen"   , &etaGen  , "etaGen/F");
  tree->Branch("phiGen"   , &phiGen  , "phiGen/F");
  tree->Branch("massGen"  , &massGen , "massGen/F");
  tree->Branch("axis1Gen" , &axis1Gen, "axis1Gen/F");
  tree->Branch("axis2Gen" , &axis2Gen, "axis2Gen/F");
  tree->Branch("ptDGen"   , &ptDGen  , "ptDGen/F");
  tree->Branch("tau1Gen"   , &tau1Gen  , "tau1Gen/F");
  tree->Branch("tau2Gen"   , &tau2Gen  , "tau2Gen/F");
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

  //file->cd();
  //tree->Write();
  //file->Close();

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
