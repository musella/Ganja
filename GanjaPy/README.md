# GanjaPy README 

This folders contains notebooks and scripts to preprocess the data and run trainings.

## Dependences

The basic depdencies are tensorflow and the packages in `packs.txt`. It's a good practice to create
a dedicated virtualenv for this.
```virtualenv <myenv_folder>
source <myenv_folder>/bin/activate
pip install -r packs.txt```

Also, this package depends on https://github.com/musella/GAN. You should clone the package and make sure that its base
folder is in the python path.
```git clone https://github.com/musella/GAN.git <dest_path>
export PYTHONPATH=<dest_path>:$PYTHONPAH```

Finally, to run the conversion step, you will also ROOT.

### To use this on Piz Daint
```module load python_virtualenv daint-gpu TensorFlow
virtualenv ~/my-env
source ~/my-env/bin/activate

tar zxfC /users/musella/root-6.10.02-mininal-cray-gcc5.3-python3.5.tar.gz ~/

pip install -r packs.txt
git clone https://github.com/musella/Ganja.git
git clone https://github.com/musella/GAN.git ~/GAN

cat >> ~/my-env.sh << EOF
module load daint-gpu
module load TensorFlow

source ~/root/bin/thisroot.sh
source ~/my-env/bin/activate

PYTHONPATH=$PYTHONPATH:~/GAN:~/Ganja/GanjaPy
export PYTONPATH
EOF
```

At each session, you will then simply source the `my-env.sh` script to set up the working environment. 


## Preprocessing

The preprocessing chain has two steps:
1. Root files are converted into python-friendly formats.  `read_and_reshape.ipynb`
   In particular, jet images are saved as npy files, while other jets features are stored as pandas DataFrame.
   In this step the jet images can also be resized.
1. Events from different files are mixed and shuffled in order to create uniform chunks. `split.ipynb`

Notebooks and scripts assume that the data is organised as follows, starting from a `base` folder:
- `<base>/prod/<production_id>` contain the root files from GanjaTree.
- `<base>/converted/<production_id>[_conv_version]` contain the numpy and pandas files  
- `<base>/split/<production_id>[_conv_version][_split_version]` contain the reshuffled data files.

The script `scripts/run_folders.sh` runs the conversion step with parallel jobs.

## Training

The training script is `train.py`. It's way too fresh to describe it here, but the code should be easy to understand.

