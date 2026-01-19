#!/usr/bin/bash

SCRIPT_PATH="$(readlink -f "$0")" 		# jTrans/env/conda.sh
SCRIPT_DIR="$(dirname "$SCRIPT_PATH")"	# jTrans/env
CONDA_DIR="${SCRIPT_DIR}/miniconda3"

source ${CONDA_DIR}/bin/activate
conda activate jtrans


# EOF
