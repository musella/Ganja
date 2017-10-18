#ifndef GanjaCommon_h
#define GanjaCommon_h



class GanjaCommon {

 public:

  GanjaCommon();
  ~GanjaCommon();

  static void setStyle();
  static void setColors( int baseColor, unsigned nColors, double* levels, float zMax = 0.2 );

  static float binToDelta( int bin );
  static void getEtaPhiBins( int i, int nPix1D, int& etaBin, int& phiBin );
  static float pixelSize();

 private:


};



#endif
