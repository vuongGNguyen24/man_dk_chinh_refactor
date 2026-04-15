import serial
import time

# Cấu hình các thông số - Hãy thay đổi cho khớp với thiết bị của bạn
SERIAL_PORT = '/dev/serial/by-id/usb-1a86_USB_Serial-if00-port0'  # Trên Windows thường là 'COM3', 'COM4'
BAUD_RATE = 9600              # Tốc độ baud (thường là 9600 hoặc 115200)
TIMEOUT = 1                   # Thời gian chờ đọc dữ liệu (giây)

def check_rs485_data():
    try:
        # Khởi tạo kết nối Serial
        ser = serial.Serial(
            port=SERIAL_PORT,
            baudrate=BAUD_RATE,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=TIMEOUT
        )
        
        print(f"--- Đang lắng nghe trên cổng {SERIAL_PORT} ({BAUD_RATE}bps) ---")
        print("Nhấn Ctrl+C để dừng lại.\n")
        a = 1
        while True:
            if ser.in_waiting > 0:
                raw_data = ser.read(ser.in_waiting)
                
                hex_data = raw_data.hex(' ').upper()
                

                print(f"  > Raw (Hex): {hex_data}")
            time.sleep(1)  # Giảm tải cho CPU
            # ser.setRTS(True)
            # time.sleep(0.01)
            print()
            ser.write(bytes([0x6D, a, 1, 0xAE]))
            a ^= 1
            ser.flush()
            # ser.setRTS(False)
            time.sleep(1)
    except serial.SerialException as e:
        print(f"Lỗi kết nối: {e}")
    except KeyboardInterrupt:
        print("\nĐã dừng chương trình.")
    finally:
        if 'ser' in locals() and ser.is_open:
            ser.close()
            print("Đã đóng cổng kết nối.")

if __name__ == "__main__":
    check_rs485_data()