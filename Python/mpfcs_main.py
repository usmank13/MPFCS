"""
@brief The system scans a 3D space with user-defined parameters to
create 3D graphs of electromagnetic fields for wireless power systems.

@authors: usmank13, chasewhyte, Tri Nguyen

"""

import numpy as np
import serial
import time
import pyvisa as visa
from tkinter import *
import matplotlib.pyplot as plt 

from Frontend.mpfcs_gui_button_functions import submit_values, vna_buttons_reset
from Backend.mpfcs_vna import vna_init, vna_record#, vna_q_calc
from Backend.mpfcs_tp_head import tp_head_tilt, tp_head_pan, tp_head_resets
from Backend.mpfcs_mpcnc import mpcnc_move_xyz, mpcnc_pause

# Initializing communication 
rm = visa.ResourceManager()
visa_vna = rm.open_resource('GPIB0::16')
print("VNA: {}".format(visa_vna.query('*IDN?')))
ser_rambo = serial.Serial('COM49') # name of port, this might be different because of the hub we use
ser_rambo.baudrate = 250000
print("RAMBo Controller for MPCNC: {}".format(ser_rambo.name))

def handler_tp_head_tilt():
    tp_head_tilt(tilt_txt, tilt_confm_lbl, pan_txt, ser_rambo)
    
def handler_tp_head_pan():
    tp_head_pan(pan_txt, pan_confm_lbl, reset_btn, ser_rambo)
    
def handler_mpfcs_run():
    mpfcs_run(reset_VNA,start_btn,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11, mpfcs_label_frame)
    
def handler_tp_head_resets():
    tp_head_resets(reset_btn, tilt_txt, ser_rambo)
        
def handler_submit_values():
    submit_values(submit_val,start_btn,reset_btn,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11)
    
def handler_vna_reset():
    vna_buttons_reset(reset_VNA,submit_val,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11)

def handler_send():
    file_txt.configure(state = 'disabled')

def handler_reset_graph():
    file_txt.configure(state = 'normal')
    
def handler_s11_plt():
    filename_input = file_txt.get()
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection = '3d')
    x, y, z, s11, _, _, _ = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
    ax1.set_title('S11')
    ax1.set_xlabel('X Position (mm)')
    ax1.set_ylabel('Y Position (mm)')
    ax1.set_zlabel('Z Position (mm)')
    p = ax1.scatter(x, y, z, c = s11, cmap = 'jet')
    colorbar = fig.colorbar(p)
    colorbar.set_label('Decibels')
    plt.show()
    
def handler_s12_plt():
    filename_input = file_txt.get()
    # s12.configure(state = 'disabled')
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection = '3d')
    x, y, z, _, s12, _, _ = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
    ax1.set_title('S12')
    ax1.set_xlabel('X Position (mm)')
    ax1.set_ylabel('Y Position (mm)')
    ax1.set_zlabel('Z Position (mm)')
    p = ax1.scatter(x, y, z, c = s12, cmap = 'jet')
    colorbar = fig.colorbar(p)
    colorbar.set_label('Decibels')
    plt.show()
    
def handler_s22_plt():
    filename_input = file_txt.get()
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection = '3d')
    x, y, z, _, _, _, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
    ax1.set_title('S22')
    ax1.set_xlabel('X Position (mm)')
    ax1.set_ylabel('Y Position (mm)')
    ax1.set_zlabel('Z Position (mm)')
    p = ax1.scatter(x, y, z, c = s22, cmap = 'jet')
    colorbar = fig.colorbar(p)
    colorbar.set_label('Decibels')
    plt.show()
    
def handler_s21_plt():
    filename_input = file_txt.get()
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection = '3d')
    x, y, z, _, _, s21, _ = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
    ax1.set_title('S21')
    ax1.set_xlabel('X Position (mm)')
    ax1.set_ylabel('Y Position (mm)')
    ax1.set_zlabel('Z Position (mm)')
    p = ax1.scatter(x, y, z, c = s21, cmap = 'jet')
    colorbar = fig.colorbar(p)
    colorbar.set_label('Decibels')
    plt.show()
    
"""
@brief Executes the main volumetric scanning program 

@param[in] reset_VNA: Reset button
@param[in] start_btn: Start button

@param[in] txt0-txt11: System input values
"""
def mpfcs_run(reset_VNA,start_btn,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11, mpfcs_label_frame):
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
#     span = int(txt08.get())
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

    f = open(txt_fileName, "w")

    time.sleep(5) # time delay to give the machine time to initialize
#     vna_data = np.empty(numSamples) #array to hold a value for each sample

    #initialize VNA
    vna_init(num_points, visa_vna, center_freq)
    speed_default = 10*60 # 10mm/s*60s/1min
    xVal = 0; yVal = 0; zVal = 0; speed = speed_default;
    mpcnc_move_xyz(xVal, yVal, zVal, speed, ser_rambo) # to initialize position

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
#         ser_rambo.write(('\nG0 Z' + str(int(z_coord))).encode()) 
        for y_coord in sampling_y_coordinates: # for each row
            f.write("\n")
            for x_coord in sampling_x_coordinates: # moves the tool to each successive sampling spot in the row
                speed = 1; 
                mpcnc_move_xyz(x_coord, y_coord, z_coord, speed, ser_rambo) # to initialize position
                mpcnc_pause(PauseDur, ser_rambo) 
                time.sleep(3)

                value = vna_record(num_points, 's11', visa_vna) #magnitude value
                value2 = vna_record(num_points, 's12', visa_vna)
                value3 = vna_record(num_points, 's21', visa_vna)
                value4 = vna_record(num_points, 's22', visa_vna)
                
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
                    print("maybe remove colorbars first?")
#                     colorbar1.remove()
#                     colorbar2.remove()
#                     colorbar3.remove()
#                     colorbar4.remove()
            
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
                
    xVal = 0; yVal = 0; zVal = 0; speed = speed_default;
    mpcnc_move_xyz(xVal, yVal, zVal, speed, ser_rambo) # to initialize position
#     ser_rambo.write(('G0 Z0').encode())

    # write the numpy matrix to a file
    np.savetext(txt_fileName + '.csv', measurements, delimiter = ',')

    f.close()
    ser_rambo.close()

    #f = open("coord-data7.txt", "r")
    #print(f.read())

    now = time.time()
    duration_took = now-then
    hours_took = duration_took / 3600
    print("Time: ", hours_took, " Hr.")

    time_disp = Label(mpfcs_label_frame, text = hours_took, font = 'Helvetica 18 bold' )
    time_disp.grid( row = 15, column = 1, pady = 10, padx = 10)

# Creating a Window of the Application
window = Tk()
window.title("MPFCS V0.1")

# tabs controlling and graphing
tab_ctrl = ttk.Notebook(window)
VNATab = ttk.Frame(tab_ctrl)
GraphTab = ttk.Frame(tab_ctrl)
tab_ctrl.add(VNATab, text = 'System Control')
tab_ctrl.add(GraphTab, text = 'Graphing Data')
tab_ctrl.pack(expand= True, fill='both')

#IN the System Control Tab
#Sectionin of Tilt and Pan, mpfcs_label_frame, and Future Live Scan
tp_label_frame = ttk.LabelFrame(VNATab, text = 'Tilt and Pan')
tp_label_frame.pack(fill=BOTH, expand=True, side = 'left')
mpfcs_label_frame = ttk.LabelFrame(VNATab, text = 'VNA')
mpfcs_label_frame.pack(fill=BOTH, expand=True,side = 'left')
Live_Panel = ttk.LabelFrame(VNATab, text = 'Live View')
Live_Panel.pack(fill = BOTH, expand = True, side = 'left')

# IN the Graphing Tab
graph_tab_label_frame =  ttk.LabelFrame(GraphTab, text = 'FILE NAME')
graph_tab_label_frame.pack(fill = BOTH, expand = False)
Parameters = ttk.LabelFrame(GraphTab, text = 'PARAMETER SELECTIONS')
Parameters.pack(fill=BOTH, expand=True)

#In the Pan and Tilt Tab

# Labeling of the components
tilt_lbl = Label(tp_label_frame, text = "Tilt Servo Angle (0-90):")
tilt_lbl.grid(row = 1, column = 0)
tilt_txt = Entry(tp_label_frame, width = 10, state = 'normal')
tilt_txt.grid(row = 1, column = 1)
tilt_confm_lbl = Label(tp_label_frame, text = "")
tilt_confm_lbl.grid(row = 1, column = 3)

pan_lbl = Label(tp_label_frame, text = "Pan Servo Angle (20-160): ")
pan_lbl.grid(row = 2, column = 0)
pan_txt = Entry(tp_label_frame, width = 10, state = 'disabled')
pan_txt.grid(row = 2, column = 1)
pan_confm_lbl = Label(tp_label_frame, text = "")
pan_confm_lbl.grid(row = 2, column = 3)

################################################# THE mpfcs_label_frame TAB

#mpfcs_label_frame tab's components set up
lbl00 = Label(mpfcs_label_frame, text = "Length: ")
lbl00.grid(row = 0, column = 0)
txt00 = Entry(mpfcs_label_frame, width = 10)
txt00.grid(row = 0, column = 1)

lbl01 = Label(mpfcs_label_frame, text = "Width:")
lbl01.grid(row = 1, column = 0)
txt01 = Entry(mpfcs_label_frame, width = 10)
txt01.grid(row = 1, column = 1)

lbl02 = Label(mpfcs_label_frame, text = "Pause duration (s): ")
lbl02.grid(row = 2, column = 0)
txt02 = Entry(mpfcs_label_frame, width = 10)
txt02.grid(row = 2, column = 1)

lbl03 = Label(mpfcs_label_frame, text = "xStep: ") ## used to be samplingF
lbl03.grid(row = 3, column = 0)
txt03 = Entry(mpfcs_label_frame, width = 10)
txt03.grid(row = 3, column = 1)

lbl04 = Label(mpfcs_label_frame, text = "yStep: ")
lbl04.grid(row = 4, column = 0)
txt04 = Entry(mpfcs_label_frame, width = 10)
txt04.grid(row = 4, column = 1)

lbl05 = Label(mpfcs_label_frame, text = "Height: ") # used to be called depth
lbl05.grid(row = 5, column = 0)
txt05 = Entry(mpfcs_label_frame, width = 10)
txt05.grid(row = 5, column = 1)

# lbl06 = Label(mpfcs_label_frame, text = "Center Frequency: ")
# lbl06.grid(row = 6, column = 0)
# txt06 = Entry(mpfcs_label_frame, width = 10)
# txt06.grid(row = 6, column = 1)

lbl07 = Label(mpfcs_label_frame, text = "Center Frequency: ")
lbl07.grid(row = 6, column = 0)
txt07 = Entry(mpfcs_label_frame, width = 10)
txt07.grid(row = 6, column = 1)

lbl08 = Label(mpfcs_label_frame, text = "Span: ")
lbl08.grid(row = 7, column = 0)
txt08 = Entry(mpfcs_label_frame, width = 10)
txt08.grid(row = 7, column = 1)

lbl09 = Label(mpfcs_label_frame, text = "Number of Points: ")
lbl09.grid(row = 8, column = 0)
txt09 = Entry(mpfcs_label_frame, width = 10)
txt09.grid(row = 8, column = 1)

lbl10 = Label(mpfcs_label_frame, text = "Z-Step: ")
lbl10.grid(row = 9, column = 0)
txt10 = Entry(mpfcs_label_frame, width = 10)
txt10.grid(row = 9, column = 1)

lbl11 = Label(mpfcs_label_frame, text = "Name the File: ")
lbl11.grid(row = 10, column = 0)
txt11 = Entry(mpfcs_label_frame, width = 10)
txt11.grid(row = 10, column = 1)

# Button layouts
tilt_btn1 = Button(tp_label_frame, text= 'SEND', command = handler_tp_head_tilt)
tilt_btn1.grid(row = 1, column = 2)

pan_btn1 = Button(tp_label_frame, text= 'SEND', command = handler_tp_head_pan)
pan_btn1.grid(row = 2, column = 2)

reset_btn = Button(tp_label_frame, text="RESET", command = vna_buttons_reset, state = 'disabled',  bg="red", fg="black", font = 'Helvetica 18 bold')
reset_btn.grid(row = 3, column = 2, pady = 30)


submit_val = Button(mpfcs_label_frame, text = 'SUBMIT VALUES', command = handler_submit_values, font = 'Helvetica 10 bold')
submit_val.grid(row = 12, column = 1, padx = 5, pady = 5)

reset_VNA = Button(mpfcs_label_frame, text = 'RESET VALUES', command = handler_vna_reset, state = 'disabled', font = 'Helvetica 10 bold')
reset_VNA.grid(row = 13, column = 1, padx = 5, pady = 5)

#initialize the timer
hours_took = 0

"""
VNA FUNCTION CALL HERE
"""
start_btn = Button(mpfcs_label_frame, text= 'SEND', command = handler_mpfcs_run, bg="green", fg="black", font = 'Helvetica 18 bold')
start_btn.grid(row = 14, column = 1, padx = 10, pady = 10)

##################################### GRAPHING

# Setting up layout
file_name = Label(graph_tab_label_frame, text = "File Name:")
file_name.grid(row = 0, column = 0)
file_txt = Entry(graph_tab_label_frame, width = 20, state = 'normal')
file_txt.grid(row = 0, column = 1)

# setting up buttons

btnSend = Button(graph_tab_label_frame, text = 'SUBMIT', command = handler_send, state = 'normal', bg = 'green', fg = 'black')
btnSend.grid(row = 0, column = 2, padx = 10, pady = 5)

btnSend = Button(graph_tab_label_frame, text = 'RESET', command = handler_reset_graph, state = 'normal', bg = 'red', fg = 'black')
btnSend.grid(row = 0, column = 3, padx = 10, pady = 5)

s11 = Button(Parameters, text= 'S11', command = handler_s11_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s11.grid(row = 0, column = 0, padx = 10, pady = 5)

s12 = Button(Parameters, text= 'S12', command = handler_s12_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s12.grid(row = 0, column = 2, padx = 10, pady = 5)

s22 = Button(Parameters, text= 'S22', command = handler_s22_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s22.grid(row = 0, column = 4, padx = 10, pady = 5)

s21 = Button(Parameters, text= 'S21', command = handler_s21_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s21.grid(row = 0, column = 6, padx = 10, pady = 5)


# NOTE: I think some of this is redundant, will need to test removing it and seeing if everything works okay. 
################################# Live View stuff (very similar to the graphing tab careful not to edit the wrong one)

# def S11Param():
#     ##### put the funtion that will generate each point here
#     print('temporary placement action')
# 
# s11 = Button(Live_Panel, text= 'S11', command = S11Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
# s11.grid(row = 0, column = 0, padx = 10, pady = 5)
# 
# def S12Param():
#     ##### put the funtion that will generate each point here
#     print('temporary placement action')
# 
# s12 = Button(Live_Panel, text= 'S12', command = S12Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
# s12.grid(row = 0, column = 2, padx = 10, pady = 5)
# 
# def S22Param():
#     ##### put the funtion that will generate each point here
#     print('temporary placement action')
# 
# s22 = Button(Live_Panel, text= 'S22', command = S22Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
# s22.grid(row = 0, column = 4, padx = 10, pady = 5)
# 
# def S21Param():
#     ##### put the funtion that will generate each point here
#     print('temporary placement action')
# 
# s21 = Button(Live_Panel, text= 'S21', command = S21Param, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
# s21.grid(row = 0, column = 6, padx = 10, pady = 5)


######################### end of code

window.mainloop()
