import pyvisa
from quantiphy import Quantity
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time
import tkinter as tk
from tkinter import messagebox, filedialog, scrolledtext
import os
import threading

class FrequencyApp:
    def __init__(self, master):

        self.master = master
        self.master.title("MEASURE APP")
        self.dmm1 = ()
        # Scan for devices button
        self.scan_btn = tk.Button(master, text="SCAN FOR \nDEVICES", command=self.scan_for_devices, width= 10, height=5)
        self.scan_btn.grid(row=0, column=0, padx=10, pady=5, sticky="")

        # Listbox available devices
        self.device_listbox = tk.Listbox(master, height=5, width=65)
        self.device_listbox.grid(row=0, column=1, padx=10, pady=5, sticky="")

        # Connect to first device button
        self.connect_btn = tk.Button(master, text="CONNECT TO \n1 DEVICE", command=self.connect_device, state=tk.DISABLED,width= 10, height=5)
        self.connect_btn.grid(row=0, column=2, padx=10, pady=5, sticky="")

        # Connect to second device button
        self.connect_btn2 = tk.Button(master, text="CONNECT TO \n2 DEVICE", command=self.connect_device_2, state=tk.DISABLED,width= 10, height=5)
        self.connect_btn2.grid(row=0, column=3, padx=10, pady=5, sticky="")

        # Aperture selection button
        self.label = tk.Label(master, text="SELECT APERTURE:")
        self.label.grid(row=6, column=0, padx=10, pady=10)

        self.aperture_values = [0.0002, 0.002, 0.01, 0.1, 1]
        self.aperture_var = tk.DoubleVar(value=self.aperture_values[0])

        self.aperture_menu = tk.OptionMenu(master, self.aperture_var, *self.aperture_values)
        self.aperture_menu.grid(row=6, column=1, padx=10, pady=10)
        self.aperture_menu.config(width=2,height=2)

        self.send_btn = tk.Button(master, text="SET APERTURE", command=self.set_aperture, height=2 , width=10)
        self.send_btn.grid(row=6, column=2, columnspan=2, padx=10, pady=10)

        # Label for sample count
        self.sample_label = tk.Label(master, text="SAMPLES:")
        self.sample_label.grid(row=7, column=0, padx=10, pady=10)

        # Entry box for samples (integer only)
        self.sample_var = tk.StringVar()
        self.sample_entry = tk.Entry(master, textvariable=self.sample_var, validate="key")
        self.sample_entry['validatecommand'] = (master.register(lambda P: P.isdigit() or P == ""), '%P')
        self.sample_entry.grid(row=7, column=1, padx=10, pady=10)

        # Label for delay
        self.delay_label = tk.Label(master, text="DELAY (ms):")
        self.delay_label.grid(row=7, column=2, padx=10, pady=10)

        # Entry box for delay (integer only)
        self.delay_var = tk.StringVar()
        self.delay_entry = tk.Entry(master, textvariable=self.delay_var, validate="key")
        self.delay_entry['validatecommand'] = (master.register(lambda P: P.isdigit() or P == ""), '%P')
        self.delay_entry.grid(row=7, column=3, padx=10, pady=10)

        self.set_params_btn = tk.Button(master, text="SET", command=self.set_parameters, width=10, height=2)
        self.set_params_btn.grid(row=7, column=4, padx=10, pady=10)


        # Reset device button
        self.reset_btn = tk.Button(master, text="RESET \nDEVICE", command=self.reset_device, state=tk.DISABLED,height=3,width=10)
        self.reset_btn.grid(row=1, column=0, padx=10, pady=5, sticky="")

        # Measure button
        self.measure_btn = tk.Button(master, text="START \nMEASURE", command=self.start_measurement, state=tk.DISABLED, height=3,width=10)
        self.measure_btn.grid(row=1, column=1, padx=10, pady=5, sticky="")

        # Save button
        self.save_btn = tk.Button(master, text="SAVE TO \nFILE", command=self.save_file, state=tk.DISABLED,height=3,width=10)
        self.save_btn.grid(row=1, column=2, padx=10, pady=5, sticky="")

        # Command input frame 1
        self.input_frame = tk.Frame(master)
        self.input_frame.grid(row=2, column=1, padx=10, pady=5, sticky="")

        self.command_entry = tk.Entry(self.input_frame, width=50)
        self.command_entry.grid(row=2, column=1, padx=(0, 5))

        self.send_button = tk.Button(self.input_frame, text="SEND TO DEVICE 1", command=self.send_command, width=14, height=1)
        self.send_button.grid(row=2, column=3)

        # Command input frame 2
        self.input_frame_2 = tk.Frame(master)
        self.input_frame_2.grid(row=3, column=1, padx=10, pady=5, sticky="")

        self.command_entry_2 = tk.Entry(self.input_frame, width=50)
        self.command_entry_2.grid(row=3, column=1, padx=(0, 5))

        self.send_button_2 = tk.Button(self.input_frame, text="SEND TO DEVICE 2", command=self.send_command_2, width=14, height=1)
        self.send_button_2.grid(row=3, column=3)

        # Log window
        self.log_window = scrolledtext.ScrolledText(master, height=15, width=65, state='disabled')
        self.log_window.grid(row=4, column=1, padx=10, pady=5, sticky="")

        # Clear log button
        self.clear_log_button = tk.Button(master, text="CLEAR LOG", command=self.clear_log, height=1, width=65)
        self.clear_log_button.grid(row=5, column=1, padx=10, pady=5, sticky="")


    def scan_for_devices(self):
            try:
                rm = pyvisa.ResourceManager()
                rscs = rm.list_resources()
                self.connect_btn.config(state=tk.NORMAL)
                self.connect_btn2.config(state=tk.NORMAL)
                self.log(str(rscs))

                if not rscs:
                    messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
                    return

                self.device_listbox.delete(0, tk.END)

                for device in rscs:
                    self.device_listbox.insert(tk.END, device)

            except Exception as e:
                messagebox.showerror("ERROR", str(e))


    def connect_device(self):
        # Get the selected device from the Listbox
        selected_device_index = self.device_listbox.curselection()

        if not selected_device_index:
            messagebox.showerror("NO DEVICE SELECTED", "SELECT DEVICE FROM THE LIST")
            return

        selected_device = self.device_listbox.get(selected_device_index)

        try:
            # Connect to the selected device
            self.dmm1 = pyvisa.ResourceManager().open_resource(selected_device)
            idn = self.dmm1.query('*IDN?')
            self.log("DEVICE 1, CONNECTED TO: " + idn.strip())
            messagebox.showinfo("DEVICE 1, CONNECTED", f"CONNECTED TO: {idn.strip()}")
            self.measure_btn.config(state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def connect_device_2(self):
        # Get the selected device from the Listbox
        selected_device_index = self.device_listbox.curselection()

        if not selected_device_index:
            messagebox.showerror("NO DEVICE SELECTED", "SELECT DEVICE FROM THE LIST")
            return

        selected_device = self.device_listbox.get(selected_device_index)

        try:
            # Connect to the selected device
            self.dmm2 = pyvisa.ResourceManager().open_resource(selected_device)
            idn = self.dmm2.query('*IDN?')
            self.log("DEVICE 2, CONNECTED TO: " + idn.strip())
            messagebox.showinfo("DEVICE 2, CONNECTED", f"CONNECTED TO: {idn.strip()}")
            self.measure_btn.config(state=tk.NORMAL)
            self.reset_btn.config(state=tk.NORMAL)

        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def set_aperture(self):
        if not self.dmm1:
            messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
            return
        try:
            self.selected_aperture = self.aperture_var.get()
            self.aperture_command = str(f"VOLT:DC:APER {self.selected_aperture}")
            self.dmm1.write(self.aperture_command)
            print(self.aperture_command)
            self.log(f"SELECTED APERTURE: {self.selected_aperture}")
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def set_aperture_2(self):
        if not self.dmm1:
            messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
            return
        try:
            self.selected_aperture = self.aperture_var.get()
            self.aperture_command = str(f"VOLT:DC:APER {self.selected_aperture}")
            self.dmm2.write(self.aperture_command)
            print(self.aperture_command)
            self.log(f"SELECTED APERTURE: {self.selected_aperture}")
        except Exception as e:
            messagebox.showerror("ERROR", str(e))

    def reset_device(self):
        if not self.dmm1 and not self.dmm2:
            messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
            return
        try:
            self.dmm1.write("*RST")
            self.dmm1.write("*CLS")
            self.dmm1.timeout = 25000
            self.log("DEVICE RESET SUCCESS")
        except Exception as e:
            messagebox.showerror("RESET ERROR", str(e))

    def set_parameters(self):
        if not self.dmm1:
            messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
            return
        try:
            self.meas_number=[]
            self.meas_value=[]
            self.meas_value_2=[]
            self.i = 0

            self.sample_input = self.sample_var.get()
            self.delay_input = self.delay_var.get()

            self.N = int(self.sample_input)
            self.delay_ms = int(self.delay_input)
            
            self.set_message = str("SET" +"\n"+ "Samples set to:" + str(self.N) + "\n" + "Delay set to:" + str(self.delay_ms) + "ms")
            self.log(self.set_message)
        except Exception as e:
            messagebox.showerror("SET ERROR", str(e))

    def start_measurement_both_dev(self):
        if not self.dmm1 or not self.dmm2:
            messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
            return
        try:
 
            thread1 = threading.Thread(target=self.start_measurement)
            thread2 = threading.Thread(target=self.start_measurement_2)

            start = time.time()
            thread1.start()
            thread2.start()
            self.start_event.set()

            # Wait for both to finish
            thread1.join()
            thread2.join()
            end = time.time()
            

            self.log("\n" + str(self.meas_value))
            self.time_string = str("\n" + "Pomiar trwal: " + str(end- start) + " s" + "\n")
            self.log(self.time_string)
            messagebox.showinfo("MEASURE",f"MASURE COMPLETED")
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("MEASURE ERROR", str(e))

    def start_measurement(self):
        if not self.dmm1:
            messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
            return
        try:
            self.dmm1.write("CONF:VOLT:DC 1")
            #self.dmm1.write("MEAS:VOLT:DC? 10;MAX")
            #MEAS?
            self.dmm1.write("VOLT:DC:APER 0.001")
            #self.dmm1.write("TRIG:SOUR BUS")
            #self.dmm1.write("SAMP:COUNT 1000")
            
            self.dmm1.write("TRIG:DEL 0.001")
            #self.dmm1.write("INIT")
            #self.dmm1.write("*TRG")
            
            start = time.time()
            #self.meas_value = self.dmm1.query("FETCH?")
           
            #self.dmm1.close()
            
            for i in range(self.N):
                self.meas_number.append(i+1)
                self.meas_value.append(float(Quantity(self.dmm1.query("READ?").strip())))          
            time.sleep(self.t)
            end = time.time()

            self.log("\n" + str(self.meas_value))
            self.time_string = str("\n" + "Pomiar trwal: " + str(end- start) + " s" + "\n")
            self.log(self.time_string)
            messagebox.showinfo("MEASURE",f"MASURE COMPLETED")
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("MEASURE ERROR", str(e))
    
    def start_measurement_2(self):
        if not self.dmm2:
            messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
            return
        try:
            self.dmm2.write("CONF:VOLT:DC 1")
            #self.dmm1.write("MEAS:VOLT:DC? 10;MAX")
            #MEAS?
            self.dmm2.write("VOLT:DC:APER 0.001")
            #self.dmm1.write("TRIG:SOUR BUS")
            #self.dmm1.write("SAMP:COUNT 1000")
            
            self.dmm2.write("TRIG:DEL 0.001")
            #self.dmm1.write("INIT")
            #self.dmm1.write("*TRG")
            
            start = time.time()
            #self.meas_value = self.dmm1.query("FETCH?")
           
            #self.dmm1.close()
            
            for i in range(self.N):
                self.meas_number.append(i+1)
                self.meas_value_2.append(float(Quantity(self.dmm2.query("READ?").strip())))          
            time.sleep(self.t)
            end = time.time()
            

            self.log("\n" + str(self.meas_value_2))
            self.time_string = str("\n" + "Pomiar trwal: " + str(end- start) + " s" + "\n")
            self.log(self.time_string)
            messagebox.showinfo("MEASURE",f"MASURE COMPLETED")
            self.save_btn.config(state=tk.NORMAL)
        except Exception as e:
            messagebox.showerror("MEASURE ERROR", str(e))


    def save_file(self):
        if not self.meas_value:
            messagebox.showerror("NO DATA TO SAVE")
            return
        filepath = tk.filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if filepath:
            try:
                joined_tables = pd.DataFrame({
                    'Pomiar': self.meas_number,
                    'Wartosc': self.meas_value,
                    'Wartosc 2': self.meas_value_2
                 })
                joined_tables.to_csv(filepath, index=False, sep=';')
                messagebox.showinfo("SAVED", f"DATA SAVED SUCCESSFULLY")
                self.log(f"SAVED TO: {filepath}"+ "\n")
            except Exception as e:
                messagebox.showerror("ERROR", str(e))


    def send_command(self):
        if not self.dmm1:
            messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
            return

        command = self.command_entry.get().strip()
        if not command:
            return

        self.log(f">>> {command}")

        try:
            if command.endswith('?'):
                response = self.dmm1.query(command)
                self.log(response.strip())
            else:
                self.dmm1.write(command)
                self.log("COMMAND SET, DEVICE 1")
        except Exception as e:
            self.log(f"Error: {e}")

        self.command_entry.delete(0, tk.END)

    def send_command_2(self):
        if not self.dmm2:
            messagebox.showerror("INSTRUMENT NOT FOUND", "NO INSTRUMENT/DEVICE CONNECTED TO PC")
            return

        command = self.command_entry.get().strip()
        if not command:
            return

        self.log(f">>> {command}")

        try:
            if command.endswith('?'):
                response = self.dmm2.query(command)
                self.log(response.strip())
            else:
                self.dmm2.write(command)
                self.log("COMMAND SET, DEVICE 2")
        except Exception as e:
            self.log(f"Error: {e}")

        self.command_entry.delete(0, tk.END)

    def log(self, message):
        self.log_window.config(state='normal')
        self.log_window.insert(tk.END, message + '\n')
        self.log_window.see(tk.END) 
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
