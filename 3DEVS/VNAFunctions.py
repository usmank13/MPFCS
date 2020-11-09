"""
@ file VNAFunctions.py
@brief Executes the overall system behavior: probe movement and VNA measurements

@author: usmank13, chasewhyte
"""
from VNAConfig import *
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


"""
@brief Resets the system GUI

@param[in] reset_VNA: Reset button
@param[in] submit_val: Submit Values button
@param[in] txt00-txt11: System inputs
"""
def VNAreset(reset_VNA,submit_val,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11):
    reset_VNA.configure(state = 'disabled')
    submit_val.configure(state = "normal")
    txt00.configure(state = 'normal')
    txt02.configure(state = 'normal')
    txt03.configure(state = 'normal')
    txt04.configure(state = 'normal')
    txt01.configure(state = 'normal')
    txt05.configure(state = 'normal')
    # txt06.configure(state = 'normal')
    txt07.configure(state = 'normal')
    txt08.configure(state = 'normal')
    txt09.configure(state = 'normal')
    txt10.configure(state = 'normal')
    txt11.configure(state = 'normal')


"""
@brief Executes the main volumetric scanning program 

@param[in] reset_VNA: Reset button
@param[in] start_btn: Start button

@param[in] txt0-txt11: System input values
"""
def run_vna(reset_VNA,start_btn,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11, MPCNC):
    reset_VNA.configure(state = 'disabled')
    start_btn.configure(state = 'disabled')
    #getting user inputs
    length = int(txt00.get())
    print("Length: " + str(length))
    width = int(txt01.get())
    print("Width: " + str(width))
    PauseDur = int(txt02.get())
    xStep = int(txt03.get())
    yStep = int(txt04.get())
    depth = int(txt05.get())
    print("Depth: " + str(depth))
    center_freq = float(txt07.get())
    span = int(txt08.get())
    num_points = int(txt09.get())
    zStep = int(txt10.get())
    txt_fileName = txt11.get() + ".txt"
    then = time.time()

    # initializing some values
    sampling_x_coordinates = np.arange(0, width, xStep)
    sampling_z_coordinates = np.arange(0, depth, zStep)
    sampling_y_coordinates = np.arange(length, 0, -1*yStep)
    s11 = np.array([])
    s12 = np.array([])
    s21 = np.array([])
    s22 = np.array([])
    x_coords = np.array([])
    y_coords = np.array([])
    z_coords = np.array([])

    firstRun = 0;

    numSamples = len(sampling_x_coordinates)*len(sampling_y_coordinates)*len(sampling_z_coordinates)
    measurements = np.zeros((numSamples, 8))
    measurementIndex = 0

    estimatedTime = (PauseDur+1)*numSamples
    print('Estimated time to completion (hours): ' + str(estimatedTime/3600))

    # Initializing communication 
    rm = visa.ResourceManager()
    vna = rm.open_resource('GPIB0::16')
    f = open(txt_fileName, "w")
    ser1 = serial.Serial('COM49') # name of port, this might be different because of the hub we use
    ser1.baudrate = 250000
    print(ser1.name)

    time.sleep(5) # time delay to give the machine time to initialize
    vna_data = np.empty(numSamples) #array to hold a value for each sample

    #initialize VNA
    vna_init(num_points, vna, center_freq)
    g_planarWrite(0, 0, ser1) # to initialize position

    #3D plots for s12, s11, s21, s22
    sPlot=plt.figure(1)
    sPlot.tight_layout(pad=3.0)
    ax1 = sPlot.add_subplot(221, projection = '3d')
    ax1.set_title('S11')
    ax1.set_xlabel('X Position (mm)')
    ax1.set_ylabel('Y Position (mm)')
    ax1.set_zlabel('Z Position (mm)')

    ax2 = sPlot.add_subplot(222, projection = '3d')
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

    for z_coord in sampling_z_coordinates: # for each z plane 
        ser1.write(('\nG0 Z' + str(int(z_coord))).encode()) 
        for y_coord in sampling_y_coordinates: # for each row
            f.write("\n")
            for x_coord in sampling_x_coordinates: # moves the tool to each successive sampling spot in the row
                g_planarWrite(x_coord, y_coord, ser1) 
                pause(PauseDur, ser1) 
                time.sleep(3)

                value = vna_record(num_points, 's11', vna) #magnitude value
                value2 = vna_record(num_points, 's12', vna)
                value3 = vna_record(num_points, 's21', vna)
                value4 = vna_record(num_points, 's22', vna)
                
                print("s11: ", value, "\ns12: ", value2, "\ns21: ", value3, "\ns22: ", value4, "\n\n")
                x_coords = np.concatenate([x_coords, np.array([x_coord])])
                y_coords = np.concatenate([y_coords, np.array([y_coord])])
                z_coords = np.concatenate([z_coords, np.array([z_coord])])

                s11 = np.concatenate([s11, np.array([value])])
                s12 = np.concatenate([s12, np.array([value2])])
                s21 = np.concatenate([s21, np.array([value3])])
                s22 = np.concatenate([s22, np.array([value4])])
                #plotting 
                if(firstRun != 0):
                    colorbar1.remove()
                    colorbar2.remove()
                    colorbar3.remove()
                    colorbar4.remove()
            
                ps11 = ax1.scatter(x_coords, y_coords, z_coords, c = s11, cmap = 'jet')
                colorbar1 = plt.colorbar(ps11, ax = ax1, pad = 0.3)
                colorbar1.set_label('Decibels')

                ps12 = ax2.scatter(x_coords,y_coords, z_coords, c = s12, cmap = 'jet')
                colorbar2 = plt.colorbar(ps12, ax = ax2, pad = 0.3)
                colorbar2.set_label('Decibels')

                ps21 = ax3.scatter(x_coords,y_coords, z_coords, c = s21, cmap = 'jet')
                colorbar3 = plt.colorbar(ps21, ax = ax3, pad = 0.3)
                colorbar3.set_label('Decibels')
                
                ps22 = ax4.scatter(x_coords,y_coords, z_coords, c = s22, cmap = 'jet')
                colorbar4 = plt.colorbar(ps22, ax = ax4, pad = 0.3)
                colorbar4.set_label('Decibels')    

                plt.pause(0.01)

                firstRun += 1

                f.write(str(x_coord) + "," + str(y_coord) + "," + str(z_coord) + "," + str(value))
                f.write("," + str(value2) + "," + str(value3) + "," + str(value4)) 
                f.write("\n")

                #measurement matrix
                #BUGS: we are having indexing problems here
                measurements[measurementIndex][0] = measurementIndex
                measurements[measurementIndex][1] = x_coord
                measurements[measurementIndex][2] = y_coord
                measurements[measurementIndex][3] = z_coord
                measurements[measurementIndex][4] = 0 #pitch angle
                measurements[measurementIndex][5] = 0 #roll angle
                measurements[measurementIndex][6] = center_freq #frequency 
                measurements[measurementIndex][7] = value3 # this is just s21 for now; can add the others later
                measurementIndex += 1
    g_planarWrite(0, 0, ser1)
    ser1.write(('G0 Z0').encode())

    # write the numpy matrix to a file
    np.savetext(txt_fileName + '.csv', measurements, delimiter = ',')

    f.close()
    ser1.close()

    #f = open("coord-data7.txt", "r")
    #print(f.read())

    now = time.time()
    duration_took = now-then
    hours_took = duration_took / 3600
    print("Time: ", hours_took, " Hr.")

    time_disp = Label(MPCNC, text = hours_took, font = 'Helvetica 18 bold' )
    time_disp.grid( row = 15, column = 1, pady = 10, padx = 10)


