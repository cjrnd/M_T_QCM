import pyvisa
from time import sleep
from quantiphy import Quantity
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import time

#pyvisa.log_to_screen()
rm = pyvisa.ResourceManager('@py')
rscs = rm.list_resources('USB*')
print(rscs)
dmm = rm.open_resource(rscs[0])
#dmm = rm.open_resource('USB0::10893::5121::MY57217967::0::INSTR')
print(dmm.query("*IDN?"))

dmm.write("*RST")
dmm.write("*CLS")
#dmm.write(':FREQ:UNIT HZ')
#dmm.write(':FREQ:MEAS:TIME 5') 

N = 5
i = 0

meas_number=[]
meas_value=[]
start = time.time()
for i in range(N):
    #print("Pomiar", i, ":", Quantity(dmm.query("MEAS:VOLT:AC?").strip()),"VAC")
    meas_number.append(i+1)
    meas_value.append(float(Quantity(dmm.query(":MEAS:FREQ?").strip())))
    #sleep(0.1)
dmm.close()
end = time.time()
print("Pomiar trwal:", end - start, "s")

plt.plot(meas_number, meas_value, linestyle='-', marker='o')

joined_tables = pd.DataFrame({
    'Pomiar': meas_number,
    'Wartosc': meas_value
})

print(joined_tables)
joined_tables.to_csv('measures.csv', index=False)
print("CSV SAVED")

plt.tight_layout()
plt.grid()
plt.show()