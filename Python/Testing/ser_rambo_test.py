import serial
import time
    
ser_rambo = serial.Serial('COM6') # name of port, this might be different because of the hub we use
ser_rambo.baudrate = 250000
print("RAMBo Controller for MPCNC: {}".format(ser_rambo.name))
print("10sec Delay for Marlin Boot-up...")
time.sleep(10)

cmd = "M114"
ser_rambo.write(cmd.encode()+b'\n')
marlin_output = ser_rambo.readline()
while marlin_output:
	print(marlin_output)
	marlin_output = ser_rambo.readline()