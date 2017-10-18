#include <iostream>
#include <stdlib.h>

#include "math.h"

#include "TFile.h"
#include "TTree.h"
#include "TProfile.h"
#include "TProfile2D.h"
#include "TLegend.h"
#include "TCanvas.h"
#include "TH1D.h"
#include "TH2D.h"
#include "TStyle.h"
#include "TPaveText.h"
#include "TColor.h"

#include "interface/GanjaCommon.h"



bool DEBUG_ = false;
bool FAST_ = false;
int nColors = 9;
float zMax = 0.2;


std::string etaString( float eta );
void drawImages( TTree* tree, int entryStart, int entryStop, int baseColor=kRed );
//void drawImage( TProfile2D* hp, const std::string& saveName, int baseColor );


int main( int argc, char* argv[] ) {

  int entryStart = 0;
  int entryStop  = 0;

  if( argc==1 ) {
  
    std::cout << "USAGE: ./drawJetImage [entryStart] [entryStop]" << std::endl;
    exit(1);

  } else {

    entryStart = (int)(atoi(argv[1]));

    entryStop = (argc>2) ? (int)(atoi(argv[2])) : entryStart;

  }

  if( entryStart==0 ) exit(2);


  std::cout << "Will draw jet images from entry: " << entryStart << " to entry: " << entryStop << std::endl;


  GanjaCommon::setStyle();

  system( "mkdir -p jetImages/" );

  TFile* file = TFile::Open("../test/ganjaTree.root", "read");
  TTree* tree = (TTree*)file->Get("ganja/ganjaTree");

  std::cout << "-> Starting draw images..." << std::endl;
  drawImages( tree, entryStart, entryStop, kRed );

  return 0;

}


void drawImages( TTree* tree, int entryStart, int entryStop, int baseColor ) {

  int event;
  tree->SetBranchAddress( "event", &event );
  int run;
  tree->SetBranchAddress( "run", &run );
  float rho;
  tree->SetBranchAddress( "rho", &rho );
  int nPix;
  tree->SetBranchAddress( "nPix", &nPix );
  float drMax;
  tree->SetBranchAddress( "drMax", &drMax );
  float pixelSize;
  tree->SetBranchAddress( "pixelSize", &pixelSize );
  float jetImageReco[99999];
  TBranch *b_jetImageReco;
  tree->SetBranchAddress( "jetImageReco", jetImageReco, &b_jetImageReco );
  float jetImageGen[99999];
  TBranch *b_jetImageGen;
  tree->SetBranchAddress( "jetImageGen", jetImageGen, &b_jetImageGen );
  float pt;
  tree->SetBranchAddress( "pt", &pt );
  float eta;
  tree->SetBranchAddress( "eta", &eta );
  float ptGen;
  tree->SetBranchAddress( "ptGen", &ptGen );
  float etaGen;
  tree->SetBranchAddress( "etaGen", &etaGen );

  tree->GetEntry(0);


  int nPix_1D = sqrt(nPix);


  Double_t levels[nColors+1];
  GanjaCommon::setColors(baseColor, nColors, levels, zMax);


  TH2D* h2_jetImageReco = new TH2D( "jetImageReco", "", nPix_1D, -drMax, drMax, nPix_1D, -drMax, drMax );
  h2_jetImageReco->SetContour((sizeof(levels)/sizeof(Double_t)), levels);
  TH2D* h2_jetImageGen = new TH2D( "jetImageGen", "", nPix_1D, -drMax, drMax, nPix_1D, -drMax, drMax );
  h2_jetImageGen->SetContour((sizeof(levels)/sizeof(Double_t)), levels);




  for( unsigned iEntry=entryStart; iEntry<=entryStop; iEntry++ ) {

    tree->GetEntry(iEntry);


    for( unsigned i=0; i<nPix; ++i ) {

      int etaBin, phiBin;
      GanjaCommon::getEtaPhiBins( i, nPix_1D, etaBin, phiBin );

      float dEta = GanjaCommon::binToDelta(etaBin);
      float dPhi = GanjaCommon::binToDelta(phiBin);

      float dR = sqrt( dEta*dEta + dPhi*dPhi );

      int dRbin = int( dR/pixelSize );


      if( DEBUG_ ) {
        if( jetImageReco[i]>0. ) {
          std::cout << "jetImageReco: " << jetImageReco[i] << std::endl;
          std::cout << "etaBin: " << etaBin << std::endl;
          std::cout << "phiBin: " << phiBin << std::endl;
          std::cout << "deta: " << dEta << std::endl;
          std::cout << "dphi: " << dPhi << std::endl;
          std::cout << "dR: " << dR << std::endl;
          std::cout << "dRbin: " << dRbin << std::endl;
        }
      }


      h2_jetImageReco->SetBinContent( etaBin, phiBin, jetImageReco[i] );
      h2_jetImageGen ->SetBinContent( etaBin, phiBin, jetImageGen [i] );


    } // for nPix


    TCanvas* c1 = new TCanvas("c1", "", 1200, 600);
    c1->Divide( 2, 1 );
    c1->cd(1);


    TH2D* h2_axes = new TH2D("axes", "", 10, -0.3, 0.3, 10, -0.3, 0.3);
    h2_axes->Draw("");

    TPaveText* labelGen = new TPaveText(0.18, 0.67, 0.52, 0.82, "brNDC");
    labelGen->SetTextSize(0.032);
    labelGen->SetFillColor(0);
    labelGen->SetTextAlign(11);
    labelGen->AddText( "GenJet" );
    labelGen->AddText( Form("p_{T} = %.0f GeV",ptGen) );
    labelGen->AddText( Form("#eta = %.1f",etaGen) );
    labelGen->Draw("same");

    h2_jetImageGen->DrawClone("col same");
    h2_jetImageGen->GetZaxis()->SetRangeUser(0., zMax);
    h2_jetImageGen->GetZaxis()->SetNdivisions(804,false);
    h2_jetImageGen->Draw("col z same");

    TPaveText* labelGanja = new TPaveText( 0.1, 0.9, 0.9, 0.95, "brNDC" );
    labelGanja->SetTextSize(0.04);
    labelGanja->SetFillColor(0);
    labelGanja->AddText( "CMS Open Data Simulation, #sqrt{s} = 7 TeV, Ganja" );
    labelGanja->Draw("same");


    c1->cd(2);

    //TH2D* h2_axes = new TH2D("axes", "", 10, -0.3, 0.3, 10, -0.3, 0.3);
    h2_axes->Draw("");

    TPaveText* labelReco = new TPaveText(0.18, 0.67, 0.52, 0.82, "brNDC");
    labelReco->SetTextSize(0.032);
    labelReco->SetFillColor(0);
    labelReco->SetTextAlign(11);
    labelReco->AddText( "PFJet" );
    labelReco->AddText( Form("p_{T} = %.0f GeV",pt) );
    labelReco->AddText( Form("#eta = %.1f",eta) );
    labelReco->Draw("same");

    h2_jetImageReco->DrawClone("col same");
    h2_jetImageReco->GetZaxis()->SetRangeUser(0., zMax);
    h2_jetImageReco->GetZaxis()->SetNdivisions(804,false);
    h2_jetImageReco->Draw("col z same");

    TPaveText* labelEvent = new TPaveText( 0.1, 0.9, 0.9, 0.95, "brNDC" );
    labelEvent->SetTextSize(0.032);
    labelEvent->SetFillColor(0);
    labelEvent->AddText( Form("Run=%d, Event=%d, #rho=%.1f GeV", run, event, rho) );
    labelEvent->Draw("same");


    gPad->RedrawAxis();


    c1->SaveAs( Form("jetImages/jetImage_%d.pdf", iEntry) );
    c1->SaveAs( Form("jetImages/jetImage_%d.eps", iEntry) );


    delete c1;
    delete h2_axes;
    delete labelReco;
    delete labelGen;


  } // for entries


  //drawImage( hp_jetImage_gluon, "jetImage_gluon", kRed );
  //drawImage( hp_jetImage_quark, "jetImage_quark", kRed );

  //drawImage( hp_jetImageZoom_gluon, "jetImageZoom_gluon", kRed );
  //drawImage( hp_jetImageZoom_quark, "jetImageZoom_quark", kRed );

  //drawImage( hp_jetImageLite_gluon, "jetImageLite_gluon", kRed );
  //drawImage( hp_jetImageLite_quark, "jetImageLite_quark", kRed );

}


//void drawImage( TProfile2D* hp, const std::string& saveName, int baseColor ) {
//
//  TCanvas* c1 = new TCanvas( "c1", "", 600, 600 );
//  c1->cd();
//
//  setColors( baseColor, nColors );
//
//  hp->DrawClone("col");
//  hp->GetZaxis()->SetRangeUser(0., zMax);
//  hp->GetZaxis()->SetNdivisions(804,false);
//  hp->Draw("col z same");
//
//  gPad->RedrawAxis();
//
//  c1->SaveAs( Form("figures/%s.eps", saveName.c_str()) );
//  c1->SaveAs( Form("figures/%s.pdf", saveName.c_str()) );
//
//  delete c1;
//  
//}




std::string etaString( float eta ) {

  double intpart;
  return std::string( Form("%.0fp%.0f", eta, 10.*modf(eta, &intpart)) );

}



