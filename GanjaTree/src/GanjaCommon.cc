#include "../interface/GanjaCommon.h"

#include "TStyle.h"
#include "TColor.h"

#include <cmath>
#include <iostream>



GanjaCommon::GanjaCommon() {}

GanjaCommon::~GanjaCommon() {}


float GanjaCommon::binToDelta( int bin ) {

  float delta = -0.3 + GanjaCommon::pixelSize()*(((float)bin)-1.) + 0.00001; // the small extra to avoid annoying ROOT binning problems
  return delta;
 
}


void GanjaCommon::getEtaPhiBins( int i, int nPix1D, int& etaBin, int& phiBin ) {

  etaBin = i % (nPix1D);
  phiBin = floor((float)i/((float)(nPix1D)));  
  etaBin += 1; // because ROOT binning starts at 1
  phiBin += 1;

}


float GanjaCommon::pixelSize() {

  return 0.005;

}


TPaveText* GanjaCommon::get_labelTop() {

  TPaveText* label_top = new TPaveText(0.4,0.959,0.975,0.963, "brNDC");
  label_top->SetBorderSize(0);
  label_top->SetFillColor(0);
  label_top->SetTextSize(0.038);
  label_top->SetTextAlign(31);
  label_top->SetTextFont(42);
  label_top->AddText("#sqrt{s} = 13 TeV");

  return label_top;

}



TPaveText* GanjaCommon::get_labelCMS() {

  TPaveText* label_cms = new TPaveText(0.143,0.96,0.27,0.965, "brNDC");
  label_cms->SetBorderSize(0);
  label_cms->SetFillColor(0);
  label_cms->SetTextSize(0.042);
  label_cms->SetTextAlign(11);
  label_cms->SetTextFont(42);
  label_cms->AddText( "CMS Simulation" );

  return label_cms;

}



void GanjaCommon::setStyle() {

  TStyle* style = new TStyle("DrawBaseStyle", "");
  style->SetCanvasColor(0);
  style->SetPadColor(0);
  style->SetFrameFillColor(0);
  style->SetStatColor(0);
  style->SetOptStat(0);
  style->SetTitleFillColor(0);
  style->SetCanvasBorderMode(0);
  style->SetPadBorderMode(0);
  style->SetFrameBorderMode(0);
  style->SetPadBottomMargin(0.12);
  style->SetPadLeftMargin(0.12);
  style->cd();
  // For the canvas:
  style->SetCanvasBorderMode(0);
  style->SetCanvasColor(kWhite);
  style->SetCanvasDefH(600); //Height of canvas
  style->SetCanvasDefW(600); //Width of canvas
  style->SetCanvasDefX(0); //POsition on screen
  style->SetCanvasDefY(0);
  // For the Pad:
  style->SetPadBorderMode(0);
  style->SetPadColor(kWhite);
  style->SetPadGridX(false);
  style->SetPadGridY(false);
  style->SetGridColor(0);
  style->SetGridStyle(3);
  style->SetGridWidth(1);
  // For the frame:
  style->SetFrameBorderMode(0);
  style->SetFrameBorderSize(1);
  style->SetFrameFillColor(0);
  style->SetFrameFillStyle(0);
  style->SetFrameLineColor(1);
  style->SetFrameLineStyle(1);
  style->SetFrameLineWidth(1);
  // Margins:
  style->SetPadTopMargin(0.05);
  style->SetPadBottomMargin(0.15);//0.13);
  style->SetPadLeftMargin(0.15);//0.16);
  style->SetPadRightMargin(0.05);//0.02);
  // For the Global title:
  style->SetOptTitle(0);
  style->SetTitleFont(42);
  style->SetTitleColor(1);
  style->SetTitleTextColor(1);
  style->SetTitleFillColor(10);
  style->SetTitleFontSize(0.05);
  // For the axis titles:
  style->SetTitleColor(1, "XYZ");
  style->SetTitleFont(42, "XYZ");
  style->SetTitleSize(0.05, "XYZ");
  style->SetTitleXOffset(1.15);//0.9);
  style->SetTitleYOffset(1.5); // => 1.15 if exponents
  // For the axis labels:
  style->SetLabelColor(1, "XYZ");
  style->SetLabelFont(42, "XYZ");
  style->SetLabelOffset(0.007, "XYZ");
  style->SetLabelSize(0.045, "XYZ");
  // For the axis:
  style->SetAxisColor(1, "XYZ");
  style->SetStripDecimals(kTRUE);
  style->SetTickLength(0.03, "XYZ");
  style->SetNdivisions(510, "XYZ");
  //  style->SetPadTickX(1); // To get tick marks on the opposite side of the frame
  style->SetPadTickY(1);
  // for histograms:
  style->SetHistLineColor(1);
  // for the palette
  Double_t stops[5] = { 0.00, 0.34, 0.61, 0.84, 1.00 };
  Double_t red  [5] = { 0.00, 0.00, 0.87, 1.00, 0.51 };
  Double_t green[5] = { 0.00, 0.81, 1.00, 0.20, 0.00 };
  Double_t blue [5] = { 0.51, 1.00, 0.12, 0.00, 0.00 };
  TColor::CreateGradientColorTable(5, stops, red, green, blue, 100);
  style->SetNumberContours(100);

  gStyle->SetPadTopMargin(0.1);
  gStyle->SetPadBottomMargin(0.15);//0.13);
  gStyle->SetPadLeftMargin(0.15);//0.16);
  gStyle->SetPadRightMargin(0.15);//0.02);


  style->cd();

}


void GanjaCommon::setColors( int baseColor, int nColors, Double_t* levels, float zMax ) {

  int colors[nColors];
  colors[0] = kWhite;
  colors[1] = baseColor-10;
  colors[2] = baseColor-7;
  colors[3] = baseColor-4;
  for( unsigned i=4; i<nColors; ++i )
    colors[i] = baseColor+i-4;
  gStyle->SetPalette(nColors,colors);

  if( levels!=0 ) {

    levels[0] = 0.;
    levels[1] = 1e-10;
    Double_t levBinSize = zMax/((Double_t)nColors-1.);
    for( unsigned iLev = 2; iLev<(nColors+1); ++iLev )
      levels[iLev] = levels[iLev-1]+levBinSize;

    std::cout << "Setting levels:" << std::endl;    
    for( unsigned i=0; i<nColors+1; ++i )
      std::cout << " levels[" << i << "]: " << levels[i] << std::endl;

  }

}



