#!/bin/bash

# activate shell for conda
echo ". /home/idies/miniconda3/etc/profile.d/conda.sh" >> ~/.bashrc
source ~/.bashrc

# create a new conda environment and activate 
conda env create --file env_sciserver.yml
conda activate lsst_train

# install new ipython kernel
python -m ipykernel install --user --name lsst_train --display-name "LSST_Train"

# source again to activate current shell and conda env
source ~/.bashrc
conda activate lsst_train

