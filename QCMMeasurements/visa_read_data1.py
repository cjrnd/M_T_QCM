import pyvisa
from quantiphy import Quantity
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext

class FrequencyApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Frequency Measurement")

        self.dmm = None
        self.frequencies = []

        #conect
        self.connect_btn = tk.Button(master, text="Connect", command=self.connect_device)
        self.connect_btn.pack(pady=5)

        # measure
        self.measure_btn = tk.Button(master, text="Start Measurement", command=self.start_measurement, state=tk.DISABLED)
        self.measure_btn.pack(pady=5)

        #save
        self.save_btn = tk.Button(master, text="Save to File", command=self.save_file, state=tk.DISABLED)
        self.save_btn.pack(pady=5)

        #cmd input
        self.input_frame = tk.Frame(master)
        self.input_frame.pack(padx=10, pady=5)

        self.command_entry = tk.Entry(self.input_frame, width=50)
        self.command_entry.pack(side=tk.LEFT, padx=(0, 5))

        self.send_button = tk.Button(self.input_frame, text="Send", command=self.send_command)
        self.send_button.pack(side=tk.LEFT)

        #log window
        self.log_window = scrolledtext.ScrolledText(master, height=8, width=60, state='disabled')
        self.log_window.pack(padx=10, pady=10)

        #clc
        self.clear_log_button = tk.Button(master, text="Clear Log", command=self.clear_log)
        self.clear_log_button.pack(pady=(0, 10))

    def connect_device(self):
        try:
            #pyvisa.log_to_screen()
            rm = pyvisa.ResourceManager('@py')
            rscs = rm.list_resources('USB*')
            print(rscs)
            #dmm = rm.open_resource('USB0::10893::5121::MY57217967::0::INSTR')

            if not rscs:
                messagebox.showerror("NO INSTRUMENT/DEVICE FOUND")
                return

            self.dmm = rm.open_resource(rscs[0])
            idn = self.dmm.query('*IDN?')
            self.log("Connected to: " + idn.strip())
            messagebox.showinfo("CONNECTED", f"CONNECTED TO: {idn.strip()}")
            self.measure_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("CONNECTION ERROR", str(e))

    def start_measurement(self):
        if not self.dmm:
            messagebox.showerror("NO INSTRUMENT/DEVICE FOUND")
            return

        try:
            self.dmm.write("*RST")
            self.dmm.write("*CLS")
            self.dmm.write('CONF:FREQ')
            self.N = 5 #liczba pomiarów 
            self.t = 0.5 #odstęp czasowy pomiędzy nimi
            self.i = 0
            self.meas_number=[]
            self.meas_value=[]
            self.frequencies = []
            start = time.time()

            for i in range(self.N):
                self.meas_number.append(i+1)
                self.dmm.write("INIT")
                self.meas_value.append(float(Quantity(self.dmm.query("FETCH?").strip())))
            time.sleep(self.t)

            end = time.time()

            self.dmm.close()

            self.time_string = str("Pomiar trwal: " + str(end- start) + " s")
            print(self.time_string)
            messagebox.showinfo("CZAS",f"{self.time_string.strip()}")
            self.save_btn.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("MEAS ERROR", str(e))

    def save_file(self):
        if not self.meas_value:
            messagebox.showerror("NO DATA TO SAVE")
            return
       
        filepath = tk.filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            try:
                joined_tables = pd.DataFrame({
                    'Pomiar': self.meas_number,
                    'Wartosc': self.meas_value
                 })
                joined_tables.to_csv(filepath, index=False)
                messagebox.showinfo("Saved", f"Data saved to {filepath}")
                self.log(f"Saved to: {filepath}")
            except Exception as e:
                messagebox.showerror("Save Error", str(e))

    def send_command(self):
        if not self.dmm:
            self.log("Instrument not connected.")
            return

        command = self.command_entry.get().strip()
        if not command:
            return

        self.log(f">>> {command}")

        try:
            if command.endswith('?'):
                response = self.dmm.query(command)
                self.log(response.strip())
            else:
                self.dmm.write(command)
                self.log("Command sent.")
        except Exception as e:
            self.log(f"Error: {e}")

    def log(self, message):
        self.log_window.config(state='normal')
        self.log_window.insert(tk.END, message + '\n')
        self.log_window.see(tk.END)  # Scroll to end
        self.log_window.config(state='disabled')

    def clear_log(self):
        self.log_window.config(state='normal')
        self.log_window.delete(1.0, tk.END)
        self.log_window.config(state='disabled')



if __name__ == "__main__":
    root = tk.Tk()
    app = FrequencyApp(root)
    root.mainloop()


# plt.plot(meas_number, meas_value, linestyle='-', marker='o')

# plt.tight_layout()
# plt.grid()
# plt.show()
