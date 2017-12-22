#ifndef __SubstructureComputer__C__
#define __SubstructureComputer__C__

#include "fastjet/ClusterSequence.hh"
#include "fastjet/ClusterSequenceArea.hh"
#include "fastjet/AreaDefinition.hh"
#include "fastjet/GhostedAreaSpec.hh"
#include "fastjet/PseudoJet.hh"
#include "fastjet/JetDefinition.hh"

#include "fastjet/contrib/Nsubjettiness.hh"
#include "fastjet/contrib/Njettiness.hh"
#include "fastjet/contrib/NjettinessPlugin.hh"

#include "TLorentzVector.h"

#include <cmath>


class SubstructureComputer
{

public:
  SubstructureComputer( int activeAreaRepeats = 1,
			double ghostArea = 0.01,
			double ghostEtaMax = 7.0
			) : 
    nSub1KT(1, fastjet::contrib::OnePass_KT_Axes(), fastjet::contrib::UnnormalizedMeasure(1)), 
    nSub2KT(2, fastjet::contrib::OnePass_KT_Axes(), fastjet::contrib::UnnormalizedMeasure(1)), 
    nSub3KT(3, fastjet::contrib::OnePass_KT_Axes(), fastjet::contrib::UnnormalizedMeasure(1)), 
    jetDef(fastjet::antikt_algorithm, 0.5),
    fjActiveArea(ghostEtaMax,activeAreaRepeats,ghostArea),
    fjAreaDefinition( fastjet::active_area, fjActiveArea )
  {};
  
  
  void operator()  (size_t np, float* E, float *px, float *py, float *pz  ) {
    
    std::vector< fastjet::PseudoJet > newparticles;
    ptD=0., axis1=0., axis2=0., tau21=0., tau1=0., tau2=0., tau3=0.;
    
    float sum_weight   = 0.;
    float sum_deta     = 0.; 
    float sum_dphi     = 0.; 
    float sum_deta2    = 0.; 
    float sum_dphi2    = 0.;
    float sum_detadphi = 0.;
    float sum_pt       = 0.;
    

    for(unsigned ip=0; ip < np; ++ip) {
      fastjet::PseudoJet pj( px[ip], py[ip], pz[ip], E[ip] );
      newparticles.push_back( pj  );
      float p2 = pj.pt2();
      float eta = pj.eta();
      float phi = pj.phi();
      sum_pt       += pj.pt();
      sum_weight   += p2;
      sum_deta     += eta*p2;
      sum_dphi     += phi*p2;
      sum_deta2    += eta*eta*p2;
      sum_detadphi += eta*phi*p2;
      sum_dphi2    += phi*phi*p2;
      
    }
    
    // compute QG vars:
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
    axis2 = (a+b-delta > 0 ?  sqrt(0.5*(a+b-delta)) : 0);
    axis1 = (a+b+delta > 0 ?  sqrt(0.5*(a+b+delta)) : 0);
    ptD   = (sum_weight > 0 ? sqrt(sum_weight)/sum_pt : 0);
    
    // axis2 = -log(axis2);
    // axis1 = -log(axis1);
        
    // compute tau21:
    fastjet::ClusterSequenceArea thisClustering(newparticles, jetDef, fjAreaDefinition);
    std::vector<fastjet::PseudoJet> out_jets = sorted_by_pt(thisClustering.inclusive_jets(0.01));        
    // std::cerr << out_jets.size() << std::endl;
    // std::cerr <<  out_jets[0].pt() << " " << out_jets[0].eta() << " " << out_jets[0].phi() << std::endl;
    
    tau1 = (nSub1KT)(out_jets[0]);
    tau2 = (nSub2KT)(out_jets[0]);
    tau3 = (nSub3KT)(out_jets[0]);
    tau21 = tau2/tau1;
    
  }
  
  float ptD, axis1, axis2, tau21, tau1, tau2, tau3;
  
private:
  fastjet::contrib::Nsubjettiness nSub3KT, nSub2KT, nSub1KT;
  
  fastjet::JetDefinition jetDef;
  fastjet::GhostedAreaSpec fjActiveArea; 
  fastjet::AreaDefinition fjAreaDefinition;
  

};

#endif // __SubstructureComputer__C__
