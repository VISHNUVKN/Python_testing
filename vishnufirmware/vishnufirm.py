import serial
import time

# --- CONFIGURATION ---
PORT = "COM18"
BAUDRATE = 9600
FIRMWARE_NAME = "=== VishnuFirm ==="
FIRMWARE_VERSION = "Version: 1.0.0"
TIMEOUT = 10
BLINKS_TO_VERIFY = 5

print(f"Connecting to {PORT} at {BAUDRATE} baud...")
try:
    with serial.Serial(PORT, BAUDRATE, timeout=1) as ser:
        print("Waiting for firmware information...\n")

        # Read and verify firmware version
        firmware_name_ok = False
        firmware_version_ok = False
        start_time = time.time()

        while time.time() - start_time < TIMEOUT:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print(f"Received: {line}")
                if line == FIRMWARE_NAME:
                    firmware_name_ok = True
                elif line == FIRMWARE_VERSION:
                    firmware_version_ok = True

                if firmware_name_ok and firmware_version_ok:
                    break

        if firmware_name_ok and firmware_version_ok:
            print("\n✅ Firmware name and version verified.")
        else:
            print("\n❌ Firmware verification failed.")
            if not firmware_name_ok:
                print("- Missing or incorrect firmware name.")
            if not firmware_version_ok:
                print("- Missing or incorrect firmware version.")
            exit()

        # Monitor LED blinking (no need to print LED ON/OFF)
        print(f"\n🔄 Monitoring LED blinking ({BLINKS_TO_VERIFY} toggles)...")
        blink_times = []
        blink_count = 0
        last_time = time.time()

        while blink_count < BLINKS_TO_VERIFY:
            line = ser.readline().decode(errors='ignore').strip()
            if "LED ON" in line or "LED OFF" in line:
                current_time = time.time()
                interval = current_time - last_time
                last_time = current_time
                if blink_count > 0:  # Skip the first interval (not useful)
                    blink_times.append(interval)
                blink_count += 1

        avg_interval = sum(blink_times) / len(blink_times)
        print(f"\n✅ LED blink verified. Average interval: {avg_interval:.2f} seconds")

except serial.SerialException as e:
    print(f"\n❌ Serial error: {e}")
except Exception as e:
    print(f"\n❌ Unexpected error: {e}")
