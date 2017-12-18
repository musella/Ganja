#ifndef GanjaTree_h
#define GanjaTree_h



#include <memory>


#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "FWCore/ServiceRegistry/interface/Service.h"

#include "fastjet/ClusterSequence.hh"
#include "fastjet/ClusterSequenceArea.hh"
#include "fastjet/AreaDefinition.hh"
#include "fastjet/GhostedAreaSpec.hh"
#include "fastjet/PseudoJet.hh"
#include "fastjet/JetDefinition.hh"

#include "fastjet/contrib/Nsubjettiness.hh"
#include "fastjet/contrib/Njettiness.hh"
#include "fastjet/contrib/NjettinessPlugin.hh"



#define nIMGMAX 99999

class TTree;
class PileupSummaryInfo;


class GanjaTree : public edm::EDAnalyzer {

   public:

      explicit GanjaTree(const edm::ParameterSet&);
      ~GanjaTree();

      static void fillDescriptions(edm::ConfigurationDescriptions& descriptions);


   private:

      virtual void beginJob() ;
      virtual void analyze(const edm::Event&, const edm::EventSetup&);
      virtual void endJob() ;

      virtual void beginRun(edm::Run const&, edm::EventSetup const&);
      virtual void endRun(edm::Run const&, edm::EventSetup const&);
      virtual void beginLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);
      virtual void endLuminosityBlock(edm::LuminosityBlock const&, edm::EventSetup const&);

      void fillImage( float ptRatio, float dEta, float dPhi, int nPix_1D, float pixelSize, float* image );
      void computeQGvars( float sum_weight, float sum_pt, float sum_deta, float sum_dphi, float sum_deta2, float sum_dphi2, float sum_detadphi, float& a_axis1, float& a_axis2, float& a_ptD );
      float computeTau21( const std::vector< fastjet::PseudoJet >& newparts );
      int getPileUp( edm::Handle<std::vector<PileupSummaryInfo>>& pupInfo );


      // ----------member data ---------------------------

      //const JetCorrector *JEC;
      edm::Service<TFileService> fs;
      TTree* tree;
      float rho, pt, eta, phi, mass, ptGen, etaGen, phiGen, massGen, btag;
      float axis1, axis2, ptD, tau21;
      float axis1Gen, axis2Gen, ptDGen, tau21Gen;
      int event, run, lumi, nVert, nPU, partonId, jetIdLevel;

      float pixelSize = 0.0046875; // so as to have 64x2 pixels
      float drMax = 0.3; // + pixelSize;

      unsigned int nPix_1D= 2* int(drMax/pixelSize);
      unsigned int nPix = nPix_1D*nPix_1D;

      float jetImageReco[nIMGMAX];
      float jetImageGen [nIMGMAX];


      fastjet::contrib::Nsubjettiness *nSub1KT;
      fastjet::contrib::Nsubjettiness *nSub2KT;
      fastjet::JetDefinition *jetDef;
      fastjet::GhostedAreaSpec *fjActiveArea;
      fastjet::AreaDefinition *fjAreaDefinition;

};


#endif
