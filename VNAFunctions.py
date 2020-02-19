#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 15:31:45 2020

@author: chasewhyte
"""
from VNAConfig import *


def VNAreset():
	submit_val.configure(state = "normal")
	txt00.configure(state = 'normal')
	txt01.configure(state = 'normal')
	txt02.configure(state = 'normal')
	txt03.configure(state = 'normal')
	txt04.configure(state = 'normal')
	txt05.configure(state = 'normal')
	# txt06.configure(state = 'normal')
	txt07.configure(state = 'normal')
	txt08.configure(state = 'normal')
	txt09.configure(state = 'normal')
	txt10.configure(state = 'normal')
	txt11.configure(state = 'normal')
	reset_VNA.configure(state = 'disabled')

def run_vna():
	#getting user inputs
	start_btn.configure(state = 'disabled')
	length = int(txt00.get())
	print("Length: " + length)
	width = int(txt01.get())
	print("Width: " + width)
	PauseDur = int(txt02.get())
	samplingF = int(txt03.get())
	yStep = int(txt04.get())
	depth = int(txt05.get())
	print("Depth: " + depth)
	# sParam = txt06.get()
	center_freq = float(txt07.get())
	span = int(txt08.get())
	num_points = int(txt09.get())
	zStep = int(txt10.get())
	txt_fileName = txt11.get() + ".txt"

	then = time.time()
	
	# initializing some values
	numPoints = (samplingF * numRows * depth)
	numRuns = 5 #number of runs 
	numMeasurements = numPoints*numRuns #number of measurements over all runs
	measurements = np.zeros((numMeasurements, 9))
	measureIndex = 1
	runNum = 1
	

	#calculating estimated time to completion
	# total time to visit all data points in seconds 
	# totalDistance = depth(width*numRows + (numRows - 1)yStep)(numRows - 1)) +(depth - 1)
	# expTime = PauseDur*numPoints + moveSpeed*(totalDistance)
	# need moveSpeed, unless time between points is negligible 


   
	
	rm = visa.ResourceManager()
	vna = rm.open_resource('GPIB0::16')
	
	f = open(txt_fileName, "w")
	# df = open("data-file.txt", "w")
	
	rows = np.zeros(int(length / yStep))   

	vna_data = np.empty(samplingF * len(rows) * depth) #array to hold a value for each sample

	ser1 = serial.Serial('COM49') # name of port, this might be different because of the hub we use
	ser1.baudrate = 250000
	print(ser1.name)

	time.sleep(5) # time delay to give the machine time to initialize

	vna_init(num_points) # intialize vna connection

	interval_length = int(width/samplingF) # Length between sampling positions 

	sampling_coordinates = np.arange(0, width, interval_length)
	g_planarWrite(0, 0) # to initialize position
	for k in range(numRuns):
	#3D plots for s12, s11, s21, s22
		sPlot=plt.figure(1)
		ax1 = sPlot.add_subplot(221, projection = '3d')
		ax1.set_title('S11')
		ax1.set_xlabel('X Position (mm)')
		ax1.set_ylabel('Y Position (mm)')
		ax1.set_zlabel('Z Position (mm)')
	
		ax2 = sPlot.add_subplot(221, projection = '3d')
		ax2.set_title('S12')
		ax2.set_xlabel('X Position (mm)')
		ax2.set_ylabel('Y Position (mm)')
		ax2.set_zlabel('Z Position (mm)')
		
		ax3 = sPlot.add_subplot(223, projection = '3d')
		ax3.set_title('S21')
		ax3.set_xlabel('X Position (mm)')
		ax3.set_ylabel('Y Position (mm)')
		ax3.set_zlabel('Z Position (mm)')
	
		ax4 = sPlot.add_subplot(224, projection = '3d')
		ax4.set_title('S22')
		ax4.set_xlabel('X Position (mm)')
		ax4.set_ylabel('Y Position (mm)')
		ax4.set_zlabel('Z Position (mm)')
		
		while j < depth:
			xVal = width
			yVal = length
			for i in range(len(rows)): # movement across each row
				f.write("\n")
				for x_coord in sampling_coordinates: # moves the tool to each successive sampling spot in the row
					g_planarWrite(x_coord, yVal) # on the first one, it takes longer for the tool to reach.. need to fix that
					pause(PauseDur) 
					time.sleep(3)
					value = vna_record(num_points, 's11') #magnitude value
					value2 = vna_record(num_points, 's12')
					value3 = vna_record(num_points, 's21')
					value4 = vna_record(num_points, 's22')
					
					##plotting 
					if(x_coord + i + j != 0):
						colorbar1.remove()
						colorbar2.remove()
						colorbar3.remove()
						colorbar4.remove()
				
					ps11 = ax1.scatter(x_coord,yVal,j, c = value, cmap = 'jet')
					colorbar1 = plt.colorbar(ps11, ax = ax1)
					colorbar1.set_label('Decibels')
					ps12 = ax1.scatter(x_coord,yVal,j, c = value2, cmap = 'jet')
					colorbar2 = plt.colorbar(ps12, ax = ax2)
					colorbar2.set_label('Decibels')
					ps21 = ax3.scatter(x_coord,yVal,j, c = value3, cmap = 'jet')
					colorbar3 = plt.colorbar(ps21, ax = ax3)
					colorbar3.set_label('Decibels')
					ps22 = ax4.scatter(x_coord,yVal,j, c = value4, cmap = 'jet')
					colorbar4 = plt.colorbar(ps22, ax = ax4)
					colorbar4.set_label('Decibels')    
					plt.pause(0.01)
					
					f.write(str(x_coord) + "," + str(yVal) + "," + str(j*zStep) + "," + str(value))
					f.write("," + str(value2) + "," + str(value3) + "," + str(value4)) 
					f.write("\n")

					#measurement matrix

					measurements[measurementIndex - 1][0] = runNum
					measurements[measurementIndex - 1][1] = measurementIndex
					measurements[measurementIndex - 1][2] = x_coord
					measurements[measurementIndex - 1][3] = yVal
					measurements[measurementIndex - 1][4] = (j - 1)*10
					measurements[measurementIndex - 1][5] = 0 #pitch angle
					measurements[measurementIndex - 1][6] = 0 #roll angle
					measurements[measurementIndex - 1][7] = center_freq #frequency 
					measurements[measurementIndex - 1][8] = value3 # this is just s21 for now; can add the others later
					measurementIndex += 1


				g_planarWrite(0, yVal - yStep)  
				yVal = yVal - yStep # update the yvalue for the next pass on the loop
			
			ser1.write(('\nG0 Z' + str(int((j+1)*zStep))).encode()) # encode this to bytes
			j += 1
			# update j to j + 1, increase j by 1
		j = 0 # counter variable to help us loop
		g_planarWrite(0, 0)
	ser1.write(('G0 Z0').encode())
	f.close()
	ser1.close()

	f = open("coord-data7.txt", "r")
	print(f.read())

	now = time.time()
	duration_took = now-then
	hours_took = duration_took / 3600
	print("Time: ", hours_took, " Hr.")

	time_disp = Label(MPCNC, text = hours_took, font = 'Helvetica 18 bold' )
	time_disp.grid( row = 15, column = 1, pady = 10, padx = 10)
