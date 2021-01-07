# Test

import serial
import visa
from Backend.VNAConfig import *
import time
import numpy as np


# set up communication
rm = visa.ResourceManager()
vna = rm.open_resource('GPIB0::16')
ser1 = serial.Serial('COM49') # name of port, this might be different because of the hub we use
ser1.baudrate = 250000
print(ser1.name)
time.sleep(5)

# dwell time at each point in seconds
pause_length = 30 

# Larger step sizes

# test motion back and forth along each axis
def test_motion(step_size, pause_length, ser):
	mpcnc_move_xyz(0, 0, 0)

	# test motion in Y direction
	mpcnc_move_xyz(0, step_size, 0)
	mpcnc_pause(pause_length, ser1)
	mpcnc_move_xyz(0, 0, 0)
	mpcnc_pause(pause_length, ser1)

	# test motion in X direction 
	mpcnc_move_xyz(step_size, 0, 0)
	mpcnc_pause(pause_length, ser1)
	mpcnc_move_xyz(0, 0, 0)
	mpcnc_pause(pause_length, ser1)

	# test motion in z direction
	mpcnc_move_xyz(0, 0, step_size)
	mpcnc_pause(pause_length, ser1)
	mpcnc_move_xyz(0, 0, 0)
	mpcnc_pause(pause_length, ser1)


# move the mpcnc head in a circle of a given radius
# at num_points evenly spcaed points
# and dwell at each point
def precision_demo(radius, num_points, pause_length):
	circles = []
	r = [radius]
	n = [num_points]
	for r, n in zip(r, n):
		t = np.linspace(0, two_pi, n)
		x = r * np.cos(t)
		y = r * np.sin(t)
		circles.append(np.c_[x, y])
	for point in circles[0]:
		x_coord = round(point[0], 2) # round points to 2 decimal places
		y_coord = round(point[1], 2)
		mpcnc_move_xyz(x_coord, y_coord)


# step size of 50, pause for 30 seconds at each point to give tester
# time to check/measure or mark the point
test_motion(50, 30) 

# step size of 0.5, sub millimeter test 
test_motion(0.5, 30)

precision_demo(3, 15, 20) # circle of radius 3, 15 points, 20 second pause


