# Test

import serial
import visa
from VNAConfig import *
import time



rm = visa.ResourceManager()
vna = rm.open_resource('GPIB0::16')
ser1 = serial.Serial('COM49') # name of port, this might be different because of the hub we use
ser1.baudrate = 250000
print(ser1.name)
time.sleep(5)
g_planarWrite(0, -50, ser1)