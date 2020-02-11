# GUI & Tilt Pan - Tri Nguyen
# VNA & MPCNC - Usman Khan

# The system scans a 3D space with user-defined parameters to
# create 3D graphs of electromagnetic fields for wireless power systems.

import numpy as np
import serial
import time
import random
import visa
from tkinter import *
from tkinter import messagebox
from tkinter import ttk
from mpl_toolkits import mplot3d
import matplotlib.pyplot as plt 
from matplotlib import cm
from matplotlib import colors
from matplotlib.ticker import FuncFormatter

# Creating a Window of the Application
window = Tk()
window.title("3DEVS")

# tabs controlling and graphing
tab_ctrl = ttk.Notebook(window)
VNATab = ttk.Frame(tab_ctrl)
GraphTab = ttk.Frame(tab_ctrl)
tab_ctrl.add(VNATab, text = 'System Control')
tab_ctrl.add(GraphTab, text = 'Graphing Data')
tab_ctrl.pack(expand= True, fill='both')

#IN the System Control Tab
#Sectionin of Tilt and Pan, VNA-MPCNC, and Future Live Scan
Tilt_Pan = ttk.LabelFrame(VNATab, text = 'Tilt and Pan')
Tilt_Pan.pack(fill=BOTH, expand=True, side = 'left')
MPCNC = ttk.LabelFrame(VNATab, text = 'VNA')
MPCNC.pack(fill=BOTH, expand=True,side = 'left')
Live_Panel = ttk.LabelFrame(VNATab, text = 'Live View')
Live_Panel.pack(fill = BOTH, expand = True, side = 'left')

# IN the Graphing Tab
name =  ttk.LabelFrame(GraphTab, text = 'FILE NAME')
name.pack(fill = BOTH, expand = False)
Parameters = ttk.LabelFrame(GraphTab, text = 'PARAMETER SELECTIONS')
Parameters.pack(fill=BOTH, expand=True)

#In the Pan and Tilt Tab

# Labeling of the components
tilt_lbl = Label(Tilt_Pan, text = "Tilt Servo Angle (0-90):")
tilt_lbl.grid(row = 1, column = 0)
tilt_txt = Entry(Tilt_Pan, width = 10, state = 'normal')
tilt_txt.grid(row = 1, column = 1)
tilt_confm_lbl = Label(Tilt_Pan, text = "")
tilt_confm_lbl.grid(row = 1, column = 3)

pan_lbl = Label(Tilt_Pan, text = "Pan Servo Angle (20-160): ")
pan_lbl.grid(row = 2, column = 0)
pan_txt = Entry(Tilt_Pan, width = 10, state = 'disabled')
pan_txt.grid(row = 2, column = 1)
pan_confm_lbl = Label(Tilt_Pan, text = "")
pan_confm_lbl.grid(row = 2, column = 3)

# setting up the drop down menu for is youre using tilt and pan or not
# ArduinoVar =StringVar(Tilt_Pan)
# ArduinoVar.set("No")
# arduinoPort = False
# ArduinoOpt = OptionMenu(Tilt_Pan, ArduinoVar, "No", "Yes")
# ArduinoOpt.grid(row = 0, column = 0, padx = 20, pady = 10 )

# def clicked0():
# 	if ArduinoVar == "Yes":
# 		arduinoPort = True
# 		arduino = serial.Serial('COM53', 9600) #Com port is subjected to changee

# ArduinoButt = Button(Tilt_Pan, text= 'SEND', command = clicked0)
# ArduinoButt.grid(row = 0, column = 1)

#this line opens arduino port
#arduino = serial.Serial('COM53', 9600) #Com port is subjected to change
#Setting up buttons
def clicked1():
	res1 = tilt_txt.get()
	if (int(res1) > 89):
		tilt_confm_lbl.configure(text = "Must be 0-89 degrees")
	else:
		tilt_confm_lbl.configure(text = "Sent " + res1 + " Tilt Angle")
		tilt_txt.configure(state = 'disabled')
		pan_txt.configure(state = 'normal')
		res1 = (str(res1).encode())
		arduino.write(res1)

def clicked2():
	res2 = pan_txt.get()
	if (int(res2) < 20 and int(res2) > 160):
		pan_confm_lbl.configure(text = "Must be 20-160 degress")
	else:
		pan_confm_lbl.configure(text = "Sent " + res2 + " Pan Angle")
		pan_txt.configure(state = 'disabled')
		reset_btn.configure(state = 'normal')
		res2 = (str(res2).encode())
		arduino.write(res2)

 # Button layouts
tilt_btn1 = Button(Tilt_Pan, text= 'SEND', command = clicked1)
tilt_btn1.grid(row = 1, column = 2)

pan_btn1 = Button(Tilt_Pan, text= 'SEND', command = clicked2)
pan_btn1.grid(row = 2, column = 2)


# Reset Button
def resets():
	reset_btn.configure(state = 'disabled')
	arduino.write('0'.encode())
	time.sleep(2)
	arduino.write('20'.encode())
	time.sleep(2)
	tilt_txt.configure(state = 'normal')

reset_btn = Button(Tilt_Pan, text="RESET", command = resets, state = 'disabled',  bg="red", fg="black", font = 'Helvetica 18 bold')
reset_btn.grid(row = 3, column = 2, pady = 30)


################################################# THE VNA-MPCNC TAB

#VNA-MPCNC tab's components set up
lbl00 = Label(MPCNC, text = "Length: ")
lbl00.grid(row = 0, column = 0)
txt00 = Entry(MPCNC, width = 10)
txt00.grid(row = 0, column = 1)

lbl01 = Label(MPCNC, text = "Width:")
lbl01.grid(row = 1, column = 0)
txt01 = Entry(MPCNC, width = 10)
txt01.grid(row = 1, column = 1)

lbl02 = Label(MPCNC, text = "Pause duration (s): ")
lbl02.grid(row = 2, column = 0)
txt02 = Entry(MPCNC, width = 10)
txt02.grid(row = 2, column = 1)

lbl03 = Label(MPCNC, text = "xStep: ") ## used to be samplingF
lbl03.grid(row = 3, column = 0)
txt03 = Entry(MPCNC, width = 10)
txt03.grid(row = 3, column = 1)

lbl04 = Label(MPCNC, text = "yStep: ")
lbl04.grid(row = 4, column = 0)
txt04 = Entry(MPCNC, width = 10)
txt04.grid(row = 4, column = 1)

lbl05 = Label(MPCNC, text = "Height: ") # used to be called depth
lbl05.grid(row = 5, column = 0)
txt05 = Entry(MPCNC, width = 10)
txt05.grid(row = 5, column = 1)

# lbl06 = Label(MPCNC, text = "Center Frequency: ")
# lbl06.grid(row = 6, column = 0)
# txt06 = Entry(MPCNC, width = 10)
# txt06.grid(row = 6, column = 1)

lbl07 = Label(MPCNC, text = "Center Frequency: ")
lbl07.grid(row = 6, column = 0)
txt07 = Entry(MPCNC, width = 10)
txt07.grid(row = 6, column = 1)

lbl08 = Label(MPCNC, text = "Span: ")
lbl08.grid(row = 7, column = 0)
txt08 = Entry(MPCNC, width = 10)
txt08.grid(row = 7, column = 1)

lbl09 = Label(MPCNC, text = "Number of Points: ")
lbl09.grid(row = 8, column = 0)
txt09 = Entry(MPCNC, width = 10)
txt09.grid(row = 8, column = 1)

lbl10 = Label(MPCNC, text = "Z-Step: ")
lbl10.grid(row = 9, column = 0)
txt10 = Entry(MPCNC, width = 10)
txt10.grid(row = 9, column = 1)

lbl11 = Label(MPCNC, text = "Name the File: ")
lbl11.grid(row = 10, column = 0)
txt11 = Entry(MPCNC, width = 10)
txt11.grid(row = 10, column = 1)

# setting up buttons
def submit_values():
	submit_val.configure(state = "disabled")
	txt00.configure(state = 'disabled')
	txt01.configure(state = 'disabled')
	txt02.configure(state = 'disabled')
	txt03.configure(state = 'disabled')
	txt04.configure(state = 'disabled')
	txt05.configure(state = 'disabled')
	# txt06.configure(state = 'disabled')
	txt07.configure(state = 'disabled')
	txt08.configure(state = 'disabled')
	txt09.configure(state = 'disabled')
	txt10.configure(state = 'disabled')
	txt11.configure(state = 'disabled')
	start_btn.configure(state = 'normal')
	reset_VNA.configure(state = 'normal')

submit_val = Button(MPCNC, text = 'SUBMIT VALUES', command = submit_values, font = 'Helvetica 10 bold')
submit_val.grid(row = 12, column = 1, padx = 5, pady = 5)

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

reset_VNA = Button(MPCNC, text = 'RESET VALUES', command = VNAreset, state = 'disabled', font = 'Helvetica 10 bold')
reset_VNA.grid(row = 13, column = 1, padx = 5, pady = 5)

#initialize the timer
hours_took = 0

# running the code
def run_vna():
	#getting user inputs
	start_btn.configure(state = 'disabled')

	length = int(txt00.get())
	print("Length: " + str(length))
	width = int(txt01.get())
	print("Width: " + str(width))
	PauseDur = int(txt02.get())
	xStep = int(txt03.get())
	yStep = int(txt04.get())
	height = int(txt05.get())
	# sParam = txt06.get()
	center_freq = float(txt07.get())
	span = int(txt08.get())
	num_points = int(txt09.get())
	zStep = int(txt10.get())
	txt_fileName = txt11.get() + ".txt"

	depth = int(height/zStep)
	print("Depth: " + str(depth))



	then = time.time()

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

	
	# initializing some values
	numRows = int(length/yStep)
	samplingF = int(width/xStep) #same thing as points per row

	numPoints = (samplingF * numRows * depth)

	numRuns = 5 #number of runs 
	numMeasurements = numPoints*numRuns #number of measurements over all runs
	measurements = np.zeros((numMeasurements, 9))
	measurementIndex = 1
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
	j = 0 # counter variable to help us loop

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
						# colorbar1.remove()
						# colorbar2.remove()
						# colorbar3.remove()
						# colorbar4.remove()
				
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


start_btn = Button(MPCNC, text= 'SEND', command = run_vna, state = 'disabled', bg="green", fg="black", font = 'Helvetica 18 bold')
start_btn.grid(row = 14, column = 1, padx = 10, pady = 10)

##################################### GRAPHING

# Setting up layout
file_name = Label(name, text = "File Name:")
file_name.grid(row = 0, column = 0)
file_txt = Entry(name, width = 20, state = 'normal')
file_txt.grid(row = 0, column = 1)

# setting up buttons
def send():
	file_txt.configure(state = 'disabled')

btnSend = Button(name, text = 'SUBMIT', command = send, state = 'normal', bg = 'green', fg = 'black')
btnSend.grid(row = 0, column = 2, padx = 10, pady = 5)

def reset_graph():
	file_txt.configure(state = 'normal')

btnSend = Button(name, text = 'RESET', command = reset_graph, state = 'normal', bg = 'red', fg = 'black')
btnSend.grid(row = 0, column = 3, padx = 10, pady = 5)


def S11Param():
	filename_input = file_txt.get()
	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection = '3d')
	x, y, z, s11, s12, s21, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
	ax1.set_title('S11')
	ax1.set_xlabel('X Position (mm)')
	ax1.set_ylabel('Y Position (mm)')
	ax1.set_zlabel('Z Position (mm)')
	p = ax1.scatter(x, y, z, c = s11, cmap = 'jet')
	colorbar = fig.colorbar(p)
	colorbar.set_label('Decibels')
	plt.show()

s11 = Button(Parameters, text= 'S11', command = S11Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s11.grid(row = 0, column = 0, padx = 10, pady = 5)

def S12Param():
	filename_input = file_txt.get()
	# s12.configure(state = 'disabled')
	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection = '3d')
	x, y, z, s11, s12, s21, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
	ax1.set_title('S12')
	ax1.set_xlabel('X Position (mm)')
	ax1.set_ylabel('Y Position (mm)')
	ax1.set_zlabel('Z Position (mm)')
	p = ax1.scatter(x, y, z, c = s12, cmap = 'jet')
	colorbar = fig.colorbar(p)
	colorbar.set_label('Decibels')
	plt.show()

s12 = Button(Parameters, text= 'S12', command = S12Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s12.grid(row = 0, column = 2, padx = 10, pady = 5)

def S22Param():
	filename_input = file_txt.get()
	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection = '3d')
	x, y, z, s11, s12, s21, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
	ax1.set_title('S22')
	ax1.set_xlabel('X Position (mm)')
	ax1.set_ylabel('Y Position (mm)')
	ax1.set_zlabel('Z Position (mm)')
	p = ax1.scatter(x, y, z, c = s22, cmap = 'jet')
	colorbar = fig.colorbar(p)
	colorbar.set_label('Decibels')
	plt.show()

s22 = Button(Parameters, text= 'S22', command = S22Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s22.grid(row = 0, column = 4, padx = 10, pady = 5)

def S21Param():
	filename_input = file_txt.get()
	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection = '3d')
	x, y, z, s11, s12, s21, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
	ax1.set_title('S21')
	ax1.set_xlabel('X Position (mm)')
	ax1.set_ylabel('Y Position (mm)')
	ax1.set_zlabel('Z Position (mm)')
	p = ax1.scatter(x, y, z, c = s21, cmap = 'jet')
	colorbar = fig.colorbar(p)
	colorbar.set_label('Decibels')
	plt.show()

s21 = Button(Parameters, text= 'S21', command = S21Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s21.grid(row = 0, column = 6, padx = 10, pady = 5)

################################# Live View stuff (very simular to the graphing tab careful not to edit the wrong one)

def S11Param():
	##### put the funtion that will generate each point here
	print('temporary placement action')

s11 = Button(Live_Panel, text= 'S11', command = S11Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s11.grid(row = 0, column = 0, padx = 10, pady = 5)

def S12Param():
	##### put the funtion that will generate each point here
	print('temporary placement action')

s12 = Button(Live_Panel, text= 'S12', command = S12Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s12.grid(row = 0, column = 2, padx = 10, pady = 5)

def S22Param():
	##### put the funtion that will generate each point here
	print('temporary placement action')

s22 = Button(Live_Panel, text= 'S22', command = S22Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s22.grid(row = 0, column = 4, padx = 10, pady = 5)

def S21Param():
	##### put the funtion that will generate each point here
	print('temporary placement action')

s21 = Button(Live_Panel, text= 'S21', command = S21Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s21.grid(row = 0, column = 6, padx = 10, pady = 5)





######################### end of code

window.mainloop()