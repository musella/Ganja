
void computeSubstructure( float img[32][32], float etamap[32], float phimap[32], float& ptD, float& axis1, float& axis2, float& tau21 ) {

  std::vector< fastjet::PseudoJet > newparticles;

  float sum_weight   = 0.;
  float sum_deta     = 0.; 
  float sum_dphi     = 0.; 
  float sum_deta2    = 0.; 
  float sum_dphi2    = 0.;
  float sum_detadphi = 0.;
  float sum_pt       = 0.;

  for( unsigned ieta=0; ieta<32; ieta++ ) {

    for( unsigned iphi=0; iphi<32; iphi++ ) {

      float ptRel = img[ieta][iphi];
      if( ptRel<=0. ) continue;

      float eta = etamap[ieta];
      float phi = phimap[iphi];

      TLorentzVector p4_cand;
      p4_cand.SetPtEtaPhiM( ptRel, eta, phi, 0. );

      newparticles.push_back( fastjet::PseudoJet( p4_cand.Px(), p4_cand.Py(), p4_cand.Pz(), p4_cand.Energy() ) );


      float dEtaCandJet = eta; //p4_cand.Eta()-p4_genJet.Eta();
      float dPhiCandJet = phi; //p4_cand.DeltaPhi(p4_genJet);

      dEtaCandJet = std::copysign(std::min(0.3,std::abs(dEtaCandJet)),dEtaCandJet);
      dPhiCandJet = std::copysign(std::min(0.3,std::abs(dPhiCandJet)),dPhiCandJet);
       

      float p2 = p4_cand.Pt()*p4_cand.Pt();
      sum_pt       += p4_cand.Pt();
      sum_weight   += p2;
      sum_deta     += dEtaCandJet*p2;
      sum_dphi     += dPhiCandJet*p2;
      sum_deta2    += dEtaCandJet*dEtaCandJet*p2;
      sum_detadphi += dEtaCandJet*dPhiCandJet*p2;
      sum_dphi2    += dPhiCandJet*dPhiCandJet*p2;


    } // for iphi

  } // for ieta

  
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

  axis2 = -log(axis2);
  axis1 = -log(axis1);


  // compute tau21:
  
  fastjet::ClusterSequenceArea* thisClustering = new fastjet::ClusterSequenceArea(newparticles, *jetDef, *fjAreaDefinition);
  std::vector<fastjet::PseudoJet> out_jets = sorted_by_pt(thisClustering->inclusive_jets(0.01));        
      
  tau21 = (*nSub2KT)(out_jets[0])/(*nSub1KT)(out_jets[0]);

}



