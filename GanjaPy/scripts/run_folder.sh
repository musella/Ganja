#!/bin/bash 

folder=$1 && shift

base=''
[[ -n $1 ]] && base=$1 && shift

prod=prod_oct25_v0
[[ -n $1 ]] && prod=$1 && shift

outdir''
[[ -n $1 ]] && outdir=$1 && shift

mkdir $outdir

nfiles=$(ls -C1  | wc -l)
for file in $base/$prod/$folder/ganjaTree_*.root; do
    echo "Processing $file"
    fname=$(echo $file | sed "s%$base/$prod/$folder/%%")    
    ifil=$(echo $fname | sed "s%ganjaTree_%%; s%.root%%")
    echo $file $ifil $fname
    nb_batch read_and_reshape.ipynb logs/${folder}_${ifil}.ipynb  --Parameters.outdir=$outdir --Parameters.base=$base --Parameters.prod=$prod  --Parameters.folder=$folder --Parameters.inpfiles=$fname --Parameters.ijob=$ifil >& logs/${folder}_${ifil}.log
done

