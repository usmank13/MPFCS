#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 15:33:05 2020

@author: chasewhyte
"""

def g_planarWrite(xVal, yVal):
	ser1.write(("G0 X" + str(xVal) + " Y" + str(yVal)).encode())
	ser1.write(b'\n')
		# Anything written to the machine using ser1.write has to be in bytes

def pause(duration):
	ser1.write(("G4 " + "P" + str(int(PauseDur*10))).encode())
	ser1.write(b'\n')

def vna_init(num_points): # add some more calibration features
	rm = visa.ResourceManager()
	vna = rm.open_resource('GPIB0::16')
	vna.query('*IDN?')
	vna.write('poin' + str(num_points))

def vna_record(num_points, sParam):  # step length is passed to find the correct element
	vna.write(sParam)
	vna.write('mark1')
	vna.write('markbuck' + str(int((num_points-1) / 2))) # selects the point at the center frequency. 
		# Perhaps I should let the user select which frequency they want to check
	data = vna.query('outpmark')
	data_arr = np.fromstring(data, sep = ',')
	return data_arr[0]