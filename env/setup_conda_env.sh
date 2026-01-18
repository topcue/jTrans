#!/usr/bin/bash

source ${HOME}/miniconda3/bin/activate

conda tos accept

conda create -n jtrans python=3.12 -y
conda activate jtrans
conda install pandas tqdm -y

pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu

python -m pip install simpletransformers networkx pyelftools

# for ida
# python -m pip install binaryai

# EOF
