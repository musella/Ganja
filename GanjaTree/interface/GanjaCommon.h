#ifndef GanjaCommon_h
#define GanjaCommon_h

#include "TPaveText.h"



class GanjaCommon {

 public:

  GanjaCommon();
  ~GanjaCommon();

  static void setStyle();
  static void setColors( int baseColor, int nColors, Double_t* levels, float zMax = 0.2 );

  static TPaveText* get_labelTop();
  static TPaveText* get_labelCMS();


  static float binToDelta( int bin );
  static void getEtaPhiBins( int i, int nPix1D, int& etaBin, int& phiBin );
  static float pixelSize();

 private:


};



#endif
