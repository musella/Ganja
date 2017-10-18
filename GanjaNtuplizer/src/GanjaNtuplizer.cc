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
   //now do what ever initialization is needed

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


   std::cout << "gen: " << std::endl;
   for ( GenJetCollection::const_iterator it = genJets->begin(); it != genJets->end(); it++ ) {

     std::cout << "pt: " << it->pt() << " eta: " << it->eta() << std::endl;

   }


   std::cout << "reco: " << std::endl;
   for ( PFJetCollection::const_iterator it = pfJets->begin(); it != pfJets->end(); it++ ) {

     std::cout << "pt: " << it->pt() << " eta: " << it->eta() << std::endl;

   }


}


// ------------ method called once each job just before starting event loop  ------------
void 
GanjaNtuplizer::beginJob()
{
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
