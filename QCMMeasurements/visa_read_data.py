import pyvisa
from time import sleep
from quantiphy import Quantity
import matplotlib.pyplot as plt
import numpy as np
import csv

#pyvisa.log_to_screen()
rm = pyvisa.ResourceManager('@py')
print(rm.list_resources())
dmm = rm.open_resource('USB0::10893::5121::MY57217967::0::INSTR')
print(dmm.query("*IDN?"))



N = 5
i = 0

meas_number=[]
meas_value=[]

while i < N:
    #print("Pomiar", i, ":", Quantity(dmm.query("MEAS:VOLT:AC?").strip()),"VAC")
    meas_number.append(i+1)
    meas_value.append(float(Quantity(dmm.query(":MEAS:VOLT:AC? 10").strip())))
    plt.plot(meas_number, meas_value, linestyle='-', marker='o')
    #plt.scatter(meas_number, meas_value)
    plt.pause(0.01)
    sleep(0.01)
    i += 1

print(meas_number)
print(meas_value)

#with open('pomiary.csv', 'w', newline='') as file:
 #   writer = csv.writer(file)
  #  header = ["Numer pomiaru", "Wartość zmierzona"]
   # writer.writerow(header)

plt.tight_layout()
plt.grid()
plt.show()