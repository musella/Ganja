#!/bin/bash

base=/scratch/musella/ganja

prod=nov2

outdir=$base/converted

ls --color=none -C1 $base/production/$prod/ | parallel --gnu --ungroup -j 5 "./scripts/run_folder.sh {} $base/production $prod $outdir"


nb_batch split.ipynb logs/split_${prod}.ipynb  --Parameters.base=$base --Parameters.version=$prod  --Parameters.nparts=200 --Parameters.njobs=10 >& logs/split_${prod}.log
