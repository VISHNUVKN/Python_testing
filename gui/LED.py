import tkinter as tk
from tkinter import ttk, messagebox
import serial
import serial.tools.list_ports
import threading
import time


class SerialReader(threading.Thread):
    def __init__(self, serial_obj, text_widget):
        super().__init__(daemon=True)
        self.serial_obj = serial_obj
        self.text_widget = text_widget
        self.running = True

    def run(self):
        while self.running:
            if self.serial_obj.in_waiting:
                data = self.serial_obj.readline().decode(errors='ignore').strip()
                self.text_widget.insert(tk.END, data + "\n")
                self.text_widget.see(tk.END)
            time.sleep(0.1)

    def stop(self):
        self.running = False


class ArduinoControlApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Arduino Control with Emoji Status")
        self.root.geometry("700x600")
        self.root.configure(bg="#E0F7FA")

        self.serial_connection = None
        self.reader_thread = None
        self.looping = False
        self.loop_thread = None

        self.setup_ui()

    def setup_ui(self):
        # Port selection
        port_frame = tk.Frame(self.root, bg="#B2EBF2", pady=10)
        port_frame.pack(fill="x")
        tk.Label(port_frame, text="Select COM Port:", bg="#B2EBF2").pack(side="left", padx=10)
        self.port_combo = ttk.Combobox(port_frame, values=self.get_serial_ports(), width=15)
        self.port_combo.pack(side="left", padx=5)
        tk.Button(port_frame, text="Connect", bg="#00BCD4", command=self.connect_serial).pack(side="left", padx=5)

        # Pin control
        pin_frame = tk.Frame(self.root, bg="#E0F7FA", pady=10)
        pin_frame.pack()
        tk.Label(pin_frame, text="Pin:", bg="#E0F7FA").grid(row=0, column=0, padx=10)
        self.pin_combo = ttk.Combobox(pin_frame, values=self.get_arduino_pins(), width=10)
        self.pin_combo.grid(row=0, column=1, padx=5)
        tk.Label(pin_frame, text="ON Time (s):", bg="#E0F7FA").grid(row=0, column=2)
        self.on_time_entry = tk.Entry(pin_frame, width=8)
        self.on_time_entry.grid(row=0, column=3, padx=5)
        tk.Label(pin_frame, text="OFF Time (s):", bg="#E0F7FA").grid(row=0, column=4)
        self.off_time_entry = tk.Entry(pin_frame, width=8)
        self.off_time_entry.grid(row=0, column=5, padx=5)

        # Buttons
        button_frame = tk.Frame(self.root, bg="#E0F7FA")
        button_frame.pack(pady=10)
        tk.Button(button_frame, text="Turn ON", bg="#4CAF50", fg="white", width=10,
                  command=lambda: self.send_command("ON")).grid(row=0, column=0, padx=10)
        tk.Button(button_frame, text="Turn OFF", bg="#F44336", fg="white", width=10,
                  command=lambda: self.send_command("OFF")).grid(row=0, column=1, padx=10)
        self.loop_btn = tk.Button(button_frame, text="Start Loop", bg="#FF9800", fg="white", width=15,
                                  command=self.toggle_loop)
        self.loop_btn.grid(row=0, column=2, padx=10)

        # Emoji display for torch status
        torch_frame = tk.LabelFrame(self.root, text="Status", bg="#E0F7FA", padx=10, pady=10)
        torch_frame.pack(pady=10)
        self.status_label = tk.Label(torch_frame, text="😑", font=("Arial", 60), bg="#E0F7FA")
        self.status_label.pack()

        # Serial Monitor
        output_frame = tk.LabelFrame(self.root, text="Serial Monitor", bg="#E0F7FA", padx=10, pady=10)
        output_frame.pack(fill="both", expand=True, padx=20, pady=10)
        self.serial_text = tk.Text(output_frame, height=12, bg="#F1F8E9", fg="black")
        self.serial_text.pack(fill="both", expand=True)

    def get_serial_ports(self):
        ports = serial.tools.list_ports.comports()
        return [port.device for port in ports]

    def get_arduino_pins(self):
        digital = [str(i) for i in range(2, 14)]
        analog = [str(i) for i in range(14, 20)]  # A0-A5 as 14–19
        return digital + analog

    def connect_serial(self):
        port = self.port_combo.get()
        if port:
            try:
                self.serial_connection = serial.Serial(port, 9600, timeout=1)
                self.reader_thread = SerialReader(self.serial_connection, self.serial_text)
                self.reader_thread.start()
                messagebox.showinfo("Connected", f"Connected to {port}")
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            messagebox.showwarning("Warning", "Please select a COM port")

    def send_command(self, state):
        if not self.serial_connection or not self.serial_connection.is_open:
            messagebox.showerror("Error", "Serial connection not open")
            return

        pin = self.pin_combo.get()
        if not pin.isdigit():
            messagebox.showerror("Error", "Please select a valid pin")
            return

        try:
            self.serial_connection.write(f"{pin}:{state}\n".encode())
            self.update_status_emoji(state)
        except Exception as e:
            messagebox.showerror("Error", f"Failed to send command: {e}")

    def toggle_loop(self):
        if self.looping:
            self.looping = False
            self.loop_btn.config(text="Start Loop", bg="#FF9800")
        else:
            if not self.serial_connection or not self.serial_connection.is_open:
                messagebox.showerror("Error", "Serial connection not open")
                return

            pin = self.pin_combo.get()
            if not pin.isdigit():
                messagebox.showerror("Error", "Invalid pin")
                return

            try:
                on_time = float(self.on_time_entry.get())
                off_time = float(self.off_time_entry.get())
            except ValueError:
                messagebox.showerror("Error", "Invalid ON/OFF time")
                return

            self.looping = True
            self.loop_btn.config(text="Stop Loop", bg="#9E9E9E")
            self.loop_thread = threading.Thread(target=self.loop_pin, args=(int(pin), on_time, off_time), daemon=True)
            self.loop_thread.start()

    def loop_pin(self, pin, on_time, off_time):
        while self.looping:
            try:
                self.serial_connection.write(f"{pin}:ON\n".encode())
                self.update_status_emoji("ON")
                time.sleep(on_time)
                self.serial_connection.write(f"{pin}:OFF\n".encode())
                self.update_status_emoji("OFF")
                time.sleep(off_time)
            except Exception as e:
                print(f"Loop Error: {e}")
                break

    def update_status_emoji(self, state):
        emoji = "🙂" if state == "ON" else "😑"
        self.status_label.config(text=emoji)

    def on_closing(self):
        self.looping = False
        if self.reader_thread:
            self.reader_thread.stop()
        if self.serial_connection:
            self.serial_connection.close()
        self.root.destroy()


if __name__ == "__main__":
    root = tk.Tk()
    app = ArduinoControlApp(root)
    root.protocol("WM_DELETE_WINDOW", app.on_closing)
    root.mainloop()
