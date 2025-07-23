import serial
import time
expected_binary = (
    "11111001000000100000010111110000011110010000001000000101010100110000000001110100000000000110000100000000011011100000000001100100000000000110000100000000011100100000000001100100000000000100011000000000011010010000000001110010000000000110110100000000011000010000000001110100000000000110000100000000001011100000000001101001000000000110111000000000011011110000000011110111"
)
def bytes_to_binary_string(byte_data):
    return ''.join(f"{byte:08b}" for byte in byte_data)
def check_arduino_boot(port='COM18', baudrate=57600, timeout=5):
    try:
        print(f"Connecting to Arduino on {port} at {baudrate} baud...")
        ser = serial.Serial(port, baudrate, timeout=timeout)
        time.sleep(2)  
        print("Reading boot message...")
        boot_data = ser.read(64)
        ser.close()
        binary_output = bytes_to_binary_string(boot_data)
        print(f"\nReceived binary ({len(binary_output)} bits):\n{binary_output}")
        if binary_output == expected_binary:
            print("\n[✅] Arduino booted successfully. Binary output matches.")
        else:
            print("\n[❌] Bootup binary does not match expected value.")
    except serial.SerialException as e:
        print(f"[❌] Serial connection failed: {e}")
if __name__ == "__main__":
    check_arduino_boot()
