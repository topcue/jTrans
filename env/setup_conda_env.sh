#!/usr/bin/bash

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)" # jTrans/env
CONDA_DIR="${SCRIPT_DIR}/miniconda3"
JTRANS_DIR="$(cd "${SCRIPT_DIR}/.." && pwd -P)"

source ${CONDA_DIR}/bin/activate

conda tos accept

conda create -n jtrans python=3.12 -y
conda activate jtrans

pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cpu

pip3 install -r ${JTRANS_DIR}/requirements.txt

# EOF
