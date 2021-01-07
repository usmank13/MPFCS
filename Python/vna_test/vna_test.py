import numpy as np
import serial
import time
import pyvisa as visa

num_points = 11
centerF = 13.56
span = 10.0

rm = visa.ResourceManager()
visa_vna = rm.open_resource('GPIB0::16')
print("VNA: {}".format(visa_vna.query('*IDN?')))
visa_vna.write('poin' + str(num_points))
visa_vna.write('CWFREQ' + str(centerF) + 'MHZ')
# visa_vna.write('STAR' + str(float(centerF-span/2)) + 'MHZ')
# visa_vna.write('STOP' + str(float(centerF+span/2)) + 'MHZ')
visa_vna.write('SPAN' + str(span)+'MHZ') 
print("VNA # Points: {}".format(visa_vna.query('POIN?')))
print("VNA Span: {}".format(visa_vna.query('SPAN?')))
print("VNA Start: {}".format(visa_vna.query('STAR?')))
print("VNA Stop: {}".format(visa_vna.query('STOP?')))
print("VNA Center Freq: {}".format(visa_vna.query('CWFREQ?')))

sParam = 's21'
visa_vna.write(sParam)
visa_vna.write('FORM4')
#     data2 = visa_vna.query('outpdata')
#     print("\n\n-----------------")
#     print("Outpdata = {}".format(data2))
#     data3 = visa_vna.write('outpform')
#     print("Outpform = {}".format(data3))
data4 = visa_vna.query('outpforf')
print("{} - Outpforf = {}".format(sParam, data4))

visa_vna.write(sParam)
for marker_pt in range(num_points):
    visa_vna.write('mark1')
    # visa_vna.write('markbuck' + str(int((num_points-1) / 2))) # selects the point at the center frequency. 
    visa_vna.write('markbuck' + str(int(marker_pt))) # selects the point at the center frequency.
        # Perhaps I should let the user select which frequency they want to check 
    data_marker = visa_vna.query('outpmark')    
    print("{} - Marker Point {} = {}".format(sParam, marker_pt, data_marker))