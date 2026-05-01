#!/bin/bash
RETRY_COUNT=0
MAX_RETRIES=5
while [ $RETRY_COUNT -lt $MAX_RETRIES ];
do
    sudo ip link set can0 down
    sudo ip link set can0 up type can bitrate 125000
    if ip link show can0 | grep -q "UP"; then
        echo "Ok"
        sleep 1
        break
    else
        RETRY_COUNT=$((RETRY_COUNT + 1))
        echo "retry"
        sleep 2
    fi
done


if [ $RETRY_COUNT -eq $MAX_RETRIES ]; then 
    echo "Can not open CAN interface"
    exit 1
fi

# Đường dẫn dự án
cd /home/nvidia/Documents/man_dk_chinh_refactor

# Kích hoạt Conda
source /home/nvidia/Downloads/anaconda3/etc/profile.d/conda.sh
conda activate test


# Chạy main.py
python main.py
