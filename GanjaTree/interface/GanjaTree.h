#ifndef GanjaTree_h
#define GanjaTree_h



#include <memory>


#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"

#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"

#include "FWCore/ParameterSet/interface/ParameterSet.h"

#include "CommonTools/UtilAlgos/interface/TFileService.h"


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

      void fillImage( float pt, float dEta, float dPhi, int nPix_1D, float pixelSize, float* image );
      int getPileUp( edm::Handle<std::vector<PileupSummaryInfo>>& pupInfo );


      // ----------member data ---------------------------

      //const JetCorrector *JEC;
      //TFileService fs;
      //edm::Service<TFileService> fs;
      TFile* file;
      TTree* tree;
      float rho, pt, eta, phi, mass, ptGen, etaGen, phiGen, massGen, btag;
      int event, run, lumi, nVert, nPU, partonId, jetIdLevel;

      float drMax = 0.3;
      float pixelSize = 0.005;

      unsigned int nPix_1D= 2* int(drMax/pixelSize);
      unsigned int nPix = nPix_1D*nPix_1D;

      float jetImageReco[99999];
      float jetImageGen [99999];

};


#endif
