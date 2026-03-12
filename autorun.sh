#!/bin/bash

# Đường dẫn dự án
cd /home/nvidia/Downloads/man_dk_chinh_refactor

# Kích hoạt Conda
source /home/nvidia/miniconda3/etc/profile.d/conda.sh
conda activate wm18

# Chạy main.py
python main.py
