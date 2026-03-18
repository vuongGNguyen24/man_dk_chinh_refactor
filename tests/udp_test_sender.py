import socket
import struct
import json
import time
import random

HOST = "127.0.0.1"
PORT = 9600   # phải trùng với config communication.yaml

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# Nếu hệ thống bạn match addr theo (ip, port)
# thì cần bind cố định
LOCAL_PORT = 50000
sock.bind((HOST, LOCAL_PORT))


# -------------------------------------------------
# 1) SEND ELECTRICAL BITMASK
# Format:
# [id][4 byte bitmask][0x21][0x22]
# total 6 byte
# -------------------------------------------------

def send_electrical_packet():
    packet_id = 0x01   # phải khớp decode_mapping_choice

    # random 4 bit đầu
    bitmask = random.randint(0, 0b1111)
    bitmask_bytes = struct.pack(">I", bitmask)

    packet = bytes([
        packet_id,
        *bitmask_bytes,
        0x21,
        0x22
    ])

    sock.sendto(packet, (HOST, PORT))
    print("Sent electrical bitmask:", bin(bitmask))


# -------------------------------------------------
# 2) SEND DISTANCE (JSON)
# arbitration_id = 0x100
# -------------------------------------------------

def send_distance():
    value = random.uniform(10, 300)
    data = struct.pack("<f", value)

    payload = {
        "arbitration_id": 0x100,
        "data": list(data)
    }

    sock.sendto(
        json.dumps(payload).encode("utf-8"),
        (HOST, PORT)
    )

    print("Sent distance:", value)


# -------------------------------------------------
# 3) SEND ANGLE (JSON)
# arbitration_id = 0x00F
# -------------------------------------------------

def send_angle():
    elev = random.randint(0, 300)      # raw
    direction = random.randint(-6000, 6000)
    print(elev * 0.1, direction * 0.01)
    if direction < 0:
        direction &= 0xFFFF

    data = [
        0,
        (elev >> 8) & 0xFF,
        elev & 0xFF,
        (direction >> 8) & 0xFF,
        direction & 0xFF,
        0
    ]

    payload = {
        "arbitration_id": 0x00F,
        "data": data
    }

    sock.sendto(
        json.dumps(payload).encode("utf-8"),
        (HOST, PORT)
    )
    
    payload = {
        "arbitration_id": 0x00E,
        "data": data
    }

    sock.sendto(
        json.dumps(payload).encode("utf-8"),
        (HOST, PORT)
    )

    print("Sent angle packet")


# -------------------------------------------------
# 4) SEND AMMO STATUS
# arbitration_id = 0x98
# -------------------------------------------------

def send_ammo():
    byte1 = random.randint(0, 255)
    byte2 = random.randint(0, 255)
    byte3 = random.randint(0, 3)

    payload = {
        "arbitration_id": 0x98,
        "data": [0, 0, byte1, byte2, byte3]
    }

    sock.sendto(
        json.dumps(payload).encode("utf-8"),
        (HOST, PORT)
    )
    
    payload = {
        "arbitration_id": 0x99,
        "data": [0, 0, byte1, byte2, byte3]
    }

    sock.sendto(
        json.dumps(payload).encode("utf-8"),
        (HOST, PORT)
    )

    print("Sent ammo status")


# -------------------------------------------------
# MAIN LOOP
# -------------------------------------------------

print("UDP test sender started...")

while True:
    send_electrical_packet()
    send_distance()
    send_angle()
    send_ammo()

    time.sleep(3)
    break