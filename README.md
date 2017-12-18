# Welcome to GAN Jet Analysis (Ganja)

After checking out the git repository, move to the `GanjaTree` directory. You're gonna have to install fastjet:

`curl -O http://fastjet.fr/repo/fastjet-3.3.0.tar.gz `
`tar zxvf fastjet-3.3.0.tar.gz`
`cd fastjet-3.3.0/`
`./configure --prefix=$PWD/../fastjet-install`
`make `
`make check`
`make install`
`cd ..`
`wget http://fastjet.hepforge.org/contrib/downloads/fjcontrib-1.030.tar.gz`
`tar -zxvf fjcontrib-1.030.tar.gz`
`cd fjcontrib-1.030/`
`./configure --fastjet-config="$PWD/../fastjet-install/bin/fastjet-config"`
`make `
`make check`
`make install`
`make fragile-shared-install`
`mv libfastjetcontribfragile.so ../fastjet-install/lib/`
`cd ..`
`cp extras/fastjet.xml ../../../config/toolbox/slc6_amd64_gcc472/tools/selected/`


, and compile the analyzer with `scram b -j 4`.

Then move to the `test` directory and run the config with `cmsRun ganjatree_cfg.py`. By default it will loop over the first 100 entries of a QCD Pt50-80 MC file found in:

`/afs/cern.ch/work/p/pandolf/public/QCD_Pt50to80_CMSSW_5_3_32.root`

The output file, called `ganjaTree.root`, will contain a flat TTree in `ganja/ganjaTree`. 
The tree is filled (maximum) twice per event: it looks for the two leading anti-kt 0.5 genJets in the event, checks if they are
correctly (dR<0.3) matched with a PFJet, and for each matched jet it finds it fills the tree once. Therefore each entry
of the tree corresponds to a given *jet*, not a given event.

For each jet, a jet image is saved (one for reco and one for gen). All candidates are used, and a pixel size of 0.005 in the eta-phi
plane is used. It is a square image, and reaches out to deltaEta and deltaPhi of +/-0.3.

To have a look at some jet images, go to the `analysis` directory and compile drawJetImages.cpp with `make drawJetImages.cpp`.
You can then run it (provided that a rootfile with a valid tree has been already created in the `test` directory) with:

`./drawJetImages [(int)startEntry] [(int)stopEntry]`

The above command will draw a comparison between the gen and reco images of the jets in the tree, from entry `startEntry` to entry `stopEntry`.

Enjoy!
