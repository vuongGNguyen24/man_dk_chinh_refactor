import random
DIRECTION_L = 0
DIRECTION_R = 0
ANGLE_L = 0
ANGLE_R = 0
DISTANCE_L = 0
DISTANCE_R = 0
AIM_DIRECTION_L = 0
AIM_DIRECTION_R = 0
AIM_ANGLE_L = 0
AIM_ANGLE_R = 0
W_DIRECTION = 30  # Hướng của tàu so với địa lý (độ, 0 = Bắc)
AMMO_L = [bool(random.randint(0, 1)) for i in range(18)]
AMMO_R = [bool(random.randint(0, 1)) for i in range(18)]
# AMMO_L = [bool(1) for i in range(18)]
# AMMO_R = [bool(1) for i in range(18)]
FIRE_L = [False for i in range(18)]
FIRE_R = [False for i in range(18)]
NUMBER_LIST = [[ 2,10,14,17,11, 3],
               [ 6,16, 8, 5,15, 7],
               [ 4,12,18,13, 9, 1]]

# Trạng thái đèn thông báo
POWER_STATUS = True   # True = xanh (bình thường), False = đỏ (bất thường)
READY_STATUS = True   # True = xanh (bình thường), False = đỏ (bất thường)

# Chế độ nhập khoảng cách (True = Tự động từ CAN, False = Thủ công)
DISTANCE_MODE_AUTO_L = True  # Chế độ tự động cho giàn trái
DISTANCE_MODE_AUTO_R = True  # Chế độ tự động cho giàn phải

# Bảng bắn được sử dụng (True = Bảng bắn cao, False = Bảng bắn thấp)
USE_HIGH_TABLE_L = False  # Bảng bắn cho giàn trái
USE_HIGH_TABLE_R = False  # Bảng bắn cho giàn phải

# Chế độ nhập góc hướng (True = Tự động từ CAN, False = Thủ công)
DIRECTION_MODE_AUTO_L = True  # Chế độ tự động cho giàn trái
DIRECTION_MODE_AUTO_R = True  # Chế độ tự động cho giàn phải

# Chế độ nhập góc tầm (True = Tính từ khoảng cách, False = Nhập trực tiếp góc tầm)
ELEVATION_INPUT_FROM_DISTANCE_L = True  # Giàn trái: True = nhập khoảng cách, False = nhập góc tầm trực tiếp
ELEVATION_INPUT_FROM_DISTANCE_R = True  # Giàn phải: True = nhập khoảng cách, False = nhập góc tầm trực tiếp

# Chế độ nhập góc tầm trực tiếp (True = Tự động từ CAN, False = Thủ công)
ELEVATION_MODE_AUTO_L = True  # Chế độ tự động cho giàn trái
ELEVATION_MODE_AUTO_R = True  # Chế độ tự động cho giàn phải
