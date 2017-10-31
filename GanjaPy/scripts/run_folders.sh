#!/bin/bash

base=/mnt/t3nfs01/data01/shome/pandolf/CMSSW_5_3_32_Ganja/src/Ganja/GanjaTree/test

prod=prod_oct25_v0

outdir=/scratch/musella/ganja

ls --color=none -C1 $base/$prod/ | parallel --gnu --ungroup -j 5 "./scripts/run_folder.sh {} $base $prod $outdir"

