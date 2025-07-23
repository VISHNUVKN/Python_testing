import serial
import serial.tools.list_ports
import threading
import time
import sys

# Get all available serial ports
def get_ports():
    return serial.tools.list_ports.comports()

# Filter and classify ports (WiFi and Bluetooth)
def classify_ports(ports):
    wifi_ports = []
    bt_ports = []
    others = []

    for port in ports:
        str_port = str(port)
        if 'WiFi' in str_port or 'ESP' in str_port or 'Silicon Labs' in str_port or 'CH340' in str_port:
            wifi_ports.append(port)
        elif 'Bluetooth' in str_port:
            bt_ports.append(port)
        else:
            others.append(port)
    return wifi_ports, bt_ports, others

# Display all ports with details
def display_ports(wifi, bt, others):
    print("\nAvailable Serial Ports:")
    index = 0
    all_ports = wifi + bt + others
    for port in all_ports:
        print(f"\n[{index}] {port.device} - {port.description}")
        print(f"     VID:PID         = {format_vid_pid(port.vid, port.pid)}")
        print(f"     Manufacturer    = {port.manufacturer}")
        print(f"     Serial Number   = {port.serial_number}")
        index += 1
    return all_ports

# Format VID:PID nicely
def format_vid_pid(vid, pid):
    if vid is not None and pid is not None:
        return f"{vid:04X}:{pid:04X}"
    return "N/A"

# Input with timeout and countdown
def timed_input(prompt, timeout=20):
    user_input = [None]

    def get_input():
        user_input[0] = input(prompt)

    thread = threading.Thread(target=get_input)
    thread.daemon = True
    thread.start()

    for i in range(timeout, 0, -1):
        if user_input[0] is not None:
            break
        print(f"Waiting for input... {i:2} seconds remaining", end='\r')
        time.sleep(1)
    print()

    if user_input[0] is not None:
        thread.join()
        return user_input[0]
    return None

# Main execution
found_ports = get_ports()
wifi_ports, bt_ports, other_ports = classify_ports(found_ports)

if not (wifi_ports or bt_ports or other_ports):
    print("No serial devices found.")
    sys.exit()

all_ports = display_ports(wifi_ports, bt_ports, other_ports)

response = timed_input("Select port index to connect (auto-selects WiFi after 20s): ", timeout=20)

# Select port
if response is None or response.strip() == "":
    if wifi_ports:
        connect_port = wifi_ports[0].device
        print(f"No input received. Automatically connecting to default WiFi device: {connect_port}")
    elif bt_ports:
        connect_port = bt_ports[0].device
        print(f"No WiFi device found. Connecting to default Bluetooth device: {connect_port}")
    else:
        connect_port = all_ports[0].device
        print(f"No preferred device found. Connecting to first available port: {connect_port}")
else:
    try:
        index = int(response.strip())
        if 0 <= index < len(all_ports):
            connect_port = all_ports[index].device
            print(f"Connecting to selected device: {connect_port}")
        else:
            print("Invalid index. Exiting.")
            sys.exit()
    except ValueError:
        print("Invalid input. Exiting.")
        sys.exit()

# Connect to the selected port
try:
    ser = serial.Serial(connect_port, baudrate=9600, timeout=1)
    print(f"\n✅ Connected to {connect_port}")
    ser.write(b'Hello Device\n')
    data = ser.readline().decode().strip()
    print(f"📬 Device responded: {data if data else '[No response]'}")
    ser.close()
except Exception as e:
    print(f"❌ Failed to connect to {connect_port}: {e}")

print("\nDONE")
