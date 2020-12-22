"""
@brief The system scans a 3D space with user-defined parameters to
create 3D graphs of electromagnetic fields for wireless power systems.

@authors: usmank13, chasewhyte, Tri Nguyen

"""

import numpy as np
import serial
import time
import pyvisa as visa
from tkinter import ttk
import tkinter as tk
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D

from Frontend.mpfcs_gui_button_functions import submit_values, vna_buttons_reset
from Backend.mpfcs_vna import vna_init, vna_record#, vna_q_calc
from Backend.mpfcs_tp_head import tp_head_tilt, tp_head_pan, tp_head_resets
from Backend.mpfcs_mpcnc import mpcnc_move_xyz, mpcnc_pause

# Initializing communication 
# rm = visa.ResourceManager()
# visa_vna = rm.open_resource('GPIB0::16')
# print("VNA: {}".format(visa_vna.query('*IDN?')))
# ser_rambo = serial.Serial('COM6') # name of port, this might be different because of the hub we use
# ser_rambo.baudrate = 250000
# print("RAMBo Controller for MPCNC: {}".format(ser_rambo.name))

def handler_tp_head_tilt():
    tp_head_tilt(tilt_txt, tilt_confm_lbl, pan_txt, ser_rambo)
    
def handler_tp_head_pan():
    tp_head_pan(pan_txt, pan_confm_lbl, reset_btn, ser_rambo)
    
def handler_tp_head_tilt_step():
    tp_head_tilt(tilt_txt, tilt_confm_lbl, pan_txt, ser_rambo)
    
def handler_tp_head_pan_step():
    tp_head_pan(pan_txt, pan_confm_lbl, reset_btn, ser_rambo)
    
# def handler_tp_home_set():
#     tp_home_xyz('set', ser_rambo)
    
def handler_mpfcs_run():
    mpfcs_run(reset_VNA, start_btn, mpcnc_vol_length_txt, mpcnc_vol_width_txt,\
              mpcnc_dwell_duration_txt, mpcnc_x_step_size_txt,\
              mpcnc_y_step_size_txt, mpcnc_vol_height_txt, vna_center_freq_txt,\
              vna_span_txt, vna_sweep_pts_txt, mpcnc_z_step_size_txt,\
              filename_txt, mpfcs_setup_frame)
    
def handler_manual_step_x():
    x_step = int(manual_x_step_size_txt.get())
    manual_speed = int(manual_speed_txt.get())
    y_step = 0; z_step = 0; reset = False;
    manual_set_mpcnc_xyz(x_step, y_step, z_step, manual_speed, reset, ser_rambo)
    
def handler_manual_step_y():
    y_step = int(manual_y_step_size_txt.get())
    manual_speed = int(manual_speed_txt.get())
    x_step = 0; z_step = 0; reset = False;
    manual_set_mpcnc_xyz(x_step, y_step, z_step, manual_speed, reset, ser_rambo)
    
def handler_manual_step_z():
    z_step = int(manual_z_step_size_txt.get())
    manual_speed = int(manual_speed_txt.get())
    x_step = 0; y_step = 0; reset = False;
    manual_set_mpcnc_xyz(x_step, y_step, z_step, manual_speed, reset, ser_rambo)
    
def handler_manual_loc_x():
    x_loc = int(manual_x_txt.get())
    manual_speed = int(manual_speed_txt.get())
    y_loc = 0; z_loc = 0; reset = False;
    manual_set_mpcnc_xyz(x_loc, y_loc, z_loc, manual_speed, reset, ser_rambo)
    
def handler_manual_loc_y():
    y_loc = int(manual_y_txt.get())
    manual_speed = int(manual_speed_txt.get())
    x_loc = 0; z_loc = 0; reset = False;
    manual_set_mpcnc_xyz(x_loc, y_loc, z_loc, manual_speed, reset, ser_rambo)
    
def handler_manual_loc_z():
    z_loc = int(manual_z_txt.get())
    manual_speed = int(manual_speed_txt.get())
    x_loc = 0; y_loc = 0; reset = False;
    manual_set_mpcnc_xyz(x_loc, y_loc, z_loc, manual_speed, reset, ser_rambo)

# def handler_manual_step_loc_switch():
#     if manual_loc_edit.get() == 0:
#         manual_x_step_size_btn.configure(state = 'enabled')
#         manual_y_step_size_btn.configure(state = 'enabled')
#         manual_z_step_size_btn.configure(state = 'enabled')
#         manual_x_btn.configure(state = 'disabled')
#         manual_y_btn.configure(state = 'disabled')
#         manual_z_btn.configure(state = 'disabled')
#     else:
#         manual_x_step_size_btn.configure(state = 'disabled')
#         manual_y_step_size_btn.configure(state = 'disabled')
#         manual_z_step_size_btn.configure(state = 'disabled')
#         manual_x_btn.configure(state = 'enabled')
#         manual_y_btn.configure(state = 'enabled')
#         manual_z_btn.configure(state = 'enabled')

def handler_manual_reset():
    reset = True
    x_step = 0; y_step = 0; z_step = 0;
    manual_set_mpcnc_xyz(x_step, y_step, z_step, manual_speed, reset, ser_rambo)
    
def handler_go_home_x():
    mpcnc_home_xyz('x', int(manual_speed_txt.get()), ser_rambo)
    
def handler_go_home_y():
    mpcnc_home_xyz('y', int(manual_speed_txt.get()), ser_rambo)
    
def handler_go_home_z():
    mpcnc_home_xyz('z', int(manual_speed_txt.get()), ser_rambo)
    
def handler_go_home_xyz():
    mpcnc_home_xyz('xyz', int(manual_speed_txt.get()), ser_rambo)

def handler_home_set():
    mpcnc_home_xyz('set', int(manual_speed_txt.get()), ser_rambo)    
    
    
def handler_tp_head_resets():
    tp_head_resets(reset_btn, tilt_txt, ser_rambo)
        
def handler_submit_values():
    submit_values(submit_val,start_btn,reset_btn,mpcnc_vol_length_txt,mpcnc_vol_width_txt,mpcnc_dwell_duration_txt,mpcnc_x_step_size_txt,mpcnc_y_step_size_txt,mpcnc_vol_height_txt,vna_center_freq_txt,vna_span_txt,vna_sweep_pts_txt,mpcnc_z_step_size_txt,filename_txt)
    
def handler_vna_reset():
    vna_buttons_reset(reset_VNA,submit_val,mpcnc_vol_length_txt,mpcnc_vol_width_txt,mpcnc_dwell_duration_txt,mpcnc_x_step_size_txt,mpcnc_y_step_size_txt,mpcnc_vol_height_txt,vna_center_freq_txt,vna_span_txt,vna_sweep_pts_txt,mpcnc_z_step_size_txt,filename_txt)

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

@param[in] txt0-filename_txt: System input values
"""
def mpfcs_run(reset_VNA,start_btn,mpcnc_vol_length_txt,mpcnc_vol_width_txt,\
              mpcnc_dwell_duration_txt,mpcnc_x_step_size_txt,\
              mpcnc_y_step_size_txt,mpcnc_vol_height_txt,vna_center_freq_txt,\
              vna_span_txt,vna_sweep_pts_txt,mpcnc_z_step_size_txt,\
              filename_txt, mpfcs_setup_frame):
    reset_VNA.configure(state = 'disabled')
    start_btn.configure(state = 'disabled')
    #getting user inputs
    length = int(mpcnc_vol_length_txt.get())
    print("Length: " + str(length))
    width = int(mpcnc_vol_width_txt.get())
    print("Width: " + str(width))
    PauseDur = int(mpcnc_dwell_duration_txt.get())
    xStep = int(mpcnc_x_step_size_txt.get())
    yStep = int(mpcnc_y_step_size_txt.get())
    depth = int(mpcnc_vol_height_txt.get())
    print("Height: " + str(depth))
    center_freq = float(vna_center_freq_txt.get())
    span = int(vna_span_txt.get())
    num_points = int(vna_sweep_pts_txt.get())
    zStep = int(mpcnc_z_step_size_txt.get())
    txt_fileName = filename_txt.get()
    then = time.time()

    # initializing some values
    sampling_x_coordinates = np.arange(0, width, xStep)
    sampling_z_coordinates = -np.arange(0, depth, zStep)
    sampling_y_coordinates = np.arange(0, length, yStep)
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

    f = open(txt_fileName+".txt", "w")

    time.sleep(5) # time delay to give the machine time to initialize
#     vna_data = np.empty(numSamples) #array to hold a value for each sample

    #initialize VNA
    vna_init(num_points, visa_vna, center_freq, span)
    speed_default = 10*60 # 10mm/s*60s/1min
    xVal = 0; yVal = 0; zVal = 0; speed = speed_default;
    mpcnc_move_xyz(xVal, yVal, zVal, speed, ser_rambo) # to initialize position

    #3D plots for s12, s11, s21, s22
#     sPlot=plt.figure(1)
#     sPlot.tight_layout(pad=3.0)
#     ax1 = sPlot.add_subplot(221, projection = '3d')
#     ax1.set_title('S11')
#     ax1.set_xlabel('X Position (mm)')
#     ax1.set_ylabel('Y Position (mm)')
#     ax1.set_zlabel('Z Position (mm)')
# 
#     ax2 = sPlot.add_subplot(222, projection = '3d')
#     ax2.set_title('S12')
#     ax2.set_xlabel('X Position (mm)')
#     ax2.set_ylabel('Y Position (mm)')
#     ax2.set_zlabel('Z Position (mm)')
#     
#     ax3 = sPlot.add_subplot(223, projection = '3d')
#     ax3.set_title('S21')
#     ax3.set_xlabel('X Position (mm)')
#     ax3.set_ylabel('Y Position (mm)')
#     ax3.set_zlabel('Z Position (mm)')
# 
#     ax4 = sPlot.add_subplot(224, projection = '3d')
#     ax4.set_title('S22')
#     ax4.set_xlabel('X Position (mm)')
#     ax4.set_ylabel('Y Position (mm)')
#     ax4.set_zlabel('Z Position (mm)')
    print("{}".format(sampling_z_coordinates))
    print("{}".format(sampling_y_coordinates))
    print("{}".format(sampling_x_coordinates))
    y_positive_direction = False
    x_positive_direction = False
    deg_range = range(60)[::5]                    
    for tilt_deg in deg_range:
#                     print("Pos Tilt3 Deg = {}".format(tilt_deg))
#                     print("Pos Pan Deg = {}".format(tilt_deg))
        ser_rambo.write(("M280"+" P0"+" S"+str(tilt_deg)).encode()) # Roll serial write
        ser_rambo.write(b'\n') # Anything written to the MPCNC using pyserial.write has to be in bytes
        ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
        ser_rambo.write(b'\n')
        time.sleep(0.2)
        ser_rambo.write(("M280"+" P3"+" S"+str(tilt_deg)).encode()) # Roll serial write
        ser_rambo.write(b'\n') # Anything written to the MPCNC using pyserial.write has to be in bytes
        ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
        ser_rambo.write(b'\n')
        time.sleep(0.2)

             
    for tilt_deg in reversed(deg_range):
#                     print("Neg Pan Deg = {}".format(tilt_deg))
        ser_rambo.write(("M280"+" P0"+" S"+str(tilt_deg)).encode()) # Roll serial write
        ser_rambo.write(b'\n')
        ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
        ser_rambo.write(b'\n')
        time.sleep(0.5)
#                     print("Neg Tilt3 Deg = {}".format(tilt_deg))                    
        ser_rambo.write(("M280"+" P3"+" S"+str(tilt_deg)).encode()) # Roll serial write
        ser_rambo.write(b'\n') # Anything written to the MPCNC using pyserial.write has to be in bytes
        ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
        ser_rambo.write(b'\n')
        time.sleep(0.5)
        
    for z_coord in sampling_z_coordinates: # for each z plane 
        print("\nz_coord = {}".format(z_coord))
        y_positive_direction = not(y_positive_direction)
#         print("y_positive_direction = {}".format(y_positive_direction))
        if y_positive_direction == True:
            _sampling_y_coordinates = sampling_y_coordinates
        else:
            _sampling_y_coordinates = reversed(sampling_y_coordinates)
             
        for y_coord in _sampling_y_coordinates: # for each row
            f.write("\n")
            print("\ny_coord = {}".format(y_coord))
            x_positive_direction = not(x_positive_direction)
#             print("x_positive_direction = {}".format(x_positive_direction))
            if x_positive_direction:
                _sampling_x_coordinates = sampling_x_coordinates
            else:
                _sampling_x_coordinates = reversed(sampling_x_coordinates)
             
            for x_coord in _sampling_x_coordinates: # moves the tool to each successive sampling spot in the row
                speed = speed_default*2;
                print("x_coord = {}".format(x_coord))
                mpcnc_move_xyz(x_coord, y_coord, z_coord, speed, ser_rambo) # to initialize position
                mpcnc_pause(PauseDur, ser_rambo) 
                time.sleep(3)
  
                value = vna_record(num_points, 's11', visa_vna) #magnitude value
                value2 = vna_record(num_points, 's12', visa_vna)
                value3 = vna_record(num_points, 's21', visa_vna)
                value4 = vna_record(num_points, 's22', visa_vna)
                  
#                 print("s11: ", value, "\ns12: ", value2, "\ns21: ", value3, "\ns22: ", value4, "\n\n")
                x_coords = np.concatenate([x_coords, np.array([x_coord])])
                y_coords = np.concatenate([y_coords, np.array([y_coord])])
                z_coords = np.concatenate([z_coords, np.array([z_coord])])
  
                s11 = np.concatenate([s11, np.array([value])])
                s12 = np.concatenate([s12, np.array([value2])])
                s21 = np.concatenate([s21, np.array([value3])])
                s22 = np.concatenate([s22, np.array([value4])])
                #plotting 
#                 if(firstRun != 0):
#                     print("maybe remove colorbars first?")
#                     colorbar1.remove()
#                     colorbar2.remove()
#                     colorbar3.remove()
#                     colorbar4.remove()
              
#                 ps11 = ax1.scatter(x_coords, y_coords, z_coords, c = s11, cmap = 'jet')
#                 colorbar1 = plt.colorbar(ps11, ax = ax1, pad = 0.3)
#                 colorbar1.set_label('Decibels')
# 
#                 ps12 = ax2.scatter(x_coords,y_coords, z_coords, c = s12, cmap = 'jet')
#                 colorbar2 = plt.colorbar(ps12, ax = ax2, pad = 0.3)
#                 colorbar2.set_label('Decibels')
# 
#                 ps21 = ax3.scatter(x_coords,y_coords, z_coords, c = s21, cmap = 'jet')
#                 colorbar3 = plt.colorbar(ps21, ax = ax3, pad = 0.3)
#                 colorbar3.set_label('Decibels')
#                 
#                 ps22 = ax4.scatter(x_coords,y_coords, z_coords, c = s22, cmap = 'jet')
#                 colorbar4 = plt.colorbar(ps22, ax = ax4, pad = 0.3)
#                 colorbar4.set_label('Decibels')    
  
#                 plt.pause(0.01)
  
                firstRun += 1
  
                f.write(str(x_coord) + "," + str(y_coord) + "," + str(z_coord) + "," + str(value))
                f.write("," + str(value2) + "," + str(value3) + "," + str(value4)) 
                f.write("\n")
  
                #measurement matrix
                #BUGS: we are having indexing problems here
                measurements[measurementIndex][0] = int(measurementIndex)
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
    np.savetxt(txt_fileName + '.csv', measurements, delimiter = ',')

    f.close()
    ser_rambo.close()

    #f = open("coord-data7.txt", "r")
    #print(f.read())

    now = time.time()
    duration_took = now-then
    hours_took = duration_took / 3600
    print("Time: ", hours_took, " Hr.")

    time_disp = tk.Label(mpfcs_setup_frame, text = hours_took, font = 'Helvetica 18 bold' )
    time_disp.grid( row = 15, column = 1, pady = 10, padx = 10)
    
def mpcnc_step_xyz(x_step, y_step, z_step, manual_speed, setting, ser_rambo):
    if setting == 0:
        mpcnc_step_xyz.x_loc = 0
        mpcnc_step_xyz.y_loc = 0
        mpcnc_step_xyz.z_loc = 0
    elif setting == 1:
    # Getting user inputs    
        mpcnc_step_xyz.x_loc += int(manual_x_step_size_txt.get())
        print("X Location: " + str(mpcnc_step_xyz.x_loc))
        mpcnc_step_xyz.y_loc += int(manual_y_step_size_txt.get())
        print("Y Location: " + str(mpcnc_step_xyz.y_loc))
        mpcnc_step_xyz.z_loc += int(manual_z_step_size_txt.get())
        print("Z Location: " + str(mpcnc_step_xyz.z_loc))
    else:
        mpcnc_step_xyz.x_loc = x_step
        mpcnc_step_xyz.y_loc = y_step
        mpcnc_step_xyz.z_loc = z_step
        
    manual_x_txt.insert(tk.END, mpcnc_step_xyz.x_loc)
    manual_y_txt.insert(tk.END, mpcnc_step_xyz.y_loc)
    manual_z_txt.insert(tk.END, mpcnc_step_xyz.z_loc)
    

    speed_default = 10*60 # 10mm/s*60s/1min
    speed = manual_speed;
    mpcnc_move_xyz(mpcnc_step_xyz.x_loc, mpcnc_step_xyz.y_loc, mpcnc_step_xyz.z_loc, speed, ser_rambo) # to initialize position

# Creating a Window of the Application
window = tk.Tk()
window.title("MPFCS V0.1")

# tabs controlling and graphing
tab_ctrl = ttk.Notebook(window)
MPFCSTab = ttk.Frame(tab_ctrl)
GraphTab = ttk.Frame(tab_ctrl)
CalibTab = ttk.Frame(tab_ctrl)
tab_ctrl.add(MPFCSTab, text = 'MPFCS Automated Scan Setup')
tab_ctrl.add(GraphTab, text = 'Data Graphing')
tab_ctrl.add(CalibTab, text = 'MPFCS Manual Control')
tab_ctrl.pack(expand= True, fill='both')

##################################### MPFCS Tab

# Live Frame -------------------------------
Live_Panel = ttk.LabelFrame(MPFCSTab, text = 'Live View')
Live_Panel.pack(fill = tk.BOTH, expand = True, side = 'left')

# Tilt/Pan Frame -------------------------------

tp_label_frame = ttk.LabelFrame(MPFCSTab, text = 'Tilt and Pan')
tp_label_frame.pack(fill=tk.BOTH, expand=True, side = 'left')

tilt_lbl = tk.Label(tp_label_frame, text = "Tilt Angle (-90 to 90deg):")
tilt_lbl.grid(row = 1, column = 0)
tilt_txt = tk.Entry(tp_label_frame, width = 10, state = 'normal')
tilt_txt.grid(row = 1, column = 1)
tilt_confm_lbl = tk.Label(tp_label_frame, text = "")
tilt_confm_lbl.grid(row = 1, column = 3)
tilt_txt.insert(tk.END, '0')

pan_lbl = tk.Label(tp_label_frame, text = "Pan Servo Angle (0-180):")
pan_lbl.grid(row = 2, column = 0)
pan_txt = tk.Entry(tp_label_frame, width = 10, state = 'normal')
pan_txt.grid(row = 2, column = 1)
pan_confm_lbl = tk.Label(tp_label_frame, text = "")
pan_confm_lbl.grid(row = 2, column = 3)
pan_txt.insert(tk.END, '0')

# tk.Button layouts
tilt_btn1 = tk.Button(tp_label_frame, text= 'Send', command = handler_tp_head_tilt)
tilt_btn1.grid(row = 1, column = 2)

pan_btn1 = tk.Button(tp_label_frame, text= 'Send', command = handler_tp_head_pan)
pan_btn1.grid(row = 2, column = 2)

# tp_home_set_btn = tk.Button(tp_label_frame, text= 'Set Tilt/Pan Home', command = handler_tp_home_set)
# tp_home_set_btn.grid(row = 3, column = 0)

reset_btn = tk.Button(tp_label_frame, text="Reset", command = vna_buttons_reset, state = 'disabled',  bg="red", fg="black", font = 'Helvetica 10')
reset_btn.grid(row = 3, column = 2, pady = 5)

# MPFCS Frame -------------------------------

mpfcs_setup_frame = ttk.LabelFrame(MPFCSTab, text = '')
mpfcs_setup_frame.pack(fill=tk.BOTH, expand=True,side = 'left')
tk.Label(mpfcs_setup_frame, text = "MPCNC Setup ------------").grid(row = 0, column = 0)

mpcnc_vol_length_lbl = tk.Label(mpfcs_setup_frame, text = "Scan Volume Length (mm): ")
mpcnc_vol_length_lbl.grid(row = 1, column = 0)
mpcnc_vol_length_txt = tk.Entry(mpfcs_setup_frame, width = 10)
mpcnc_vol_length_txt.grid(row = 1, column = 1)
mpcnc_vol_length_txt.insert(tk.END, '30')

mpcnc_vol_width_lbl = tk.Label(mpfcs_setup_frame, text = "Scan Volume Width (mm):")
mpcnc_vol_width_lbl.grid(row = 2, column = 0)
mpcnc_vol_width_txt = tk.Entry(mpfcs_setup_frame, width = 10)
mpcnc_vol_width_txt.grid(row = 2, column = 1)
mpcnc_vol_width_txt.insert(tk.END, '30')

mpcnc_vol_height_lbl = tk.Label(mpfcs_setup_frame, text = "Scan Volume Height (mm):") # used to be called depth
mpcnc_vol_height_lbl.grid(row = 3, column = 0)
mpcnc_vol_height_txt = tk.Entry(mpfcs_setup_frame, width = 10)
mpcnc_vol_height_txt.grid(row = 3, column = 1)
mpcnc_vol_height_txt.insert(tk.END, '20')

mpcnc_x_step_size_lbl = tk.Label(mpfcs_setup_frame, text = "X Step Size (mm):") ## used to be samplingF
mpcnc_x_step_size_lbl.grid(row = 4, column = 0)
mpcnc_x_step_size_txt = tk.Entry(mpfcs_setup_frame, width = 10)
mpcnc_x_step_size_txt.grid(row = 4, column = 1)
mpcnc_x_step_size_txt.insert(tk.END, '10')

mpcnc_y_step_size_lbl = tk.Label(mpfcs_setup_frame, text = "Y Step Size (mm):")
mpcnc_y_step_size_lbl.grid(row = 5, column = 0)
mpcnc_y_step_size_txt = tk.Entry(mpfcs_setup_frame, width = 10)
mpcnc_y_step_size_txt.grid(row = 5, column = 1)
mpcnc_y_step_size_txt.insert(tk.END, '10')

mpcnc_z_step_size_lbl = tk.Label(mpfcs_setup_frame, text = "Z Step Size (mm):")
mpcnc_z_step_size_lbl.grid(row = 6, column = 0)
mpcnc_z_step_size_txt = tk.Entry(mpfcs_setup_frame, width = 10)
mpcnc_z_step_size_txt.grid(row = 6, column = 1)
mpcnc_z_step_size_txt.insert(tk.END, '10')

mpcnc_dwell_duration_lbl = tk.Label(mpfcs_setup_frame, text = "Pause duration (s):")
mpcnc_dwell_duration_lbl.grid(row = 7, column = 0)
mpcnc_dwell_duration_txt = tk.Entry(mpfcs_setup_frame, width = 10)
mpcnc_dwell_duration_txt.grid(row = 7, column = 1)
mpcnc_dwell_duration_txt.insert(tk.END, '1')

# ttk.Separator(mpfcs_setup_frame,orient='horizontal').grid(row=7, columnspan=200)
tk.Label(mpfcs_setup_frame, text = "VNA Setup ------------").grid(row = 8, column = 0)

vna_center_freq_lbl = tk.Label(mpfcs_setup_frame, text = "Center Frequency (MHz):")
vna_center_freq_lbl.grid(row = 9, column = 0)
vna_center_freq_txt = tk.Entry(mpfcs_setup_frame, width = 10)
vna_center_freq_txt.grid(row = 9, column = 1)
vna_center_freq_txt.insert(tk.END, '13.56')

vna_span_lbl = tk.Label(mpfcs_setup_frame, text = "Span (MHz):")
vna_span_lbl.grid(row = 10, column = 0)
vna_span_txt = tk.Entry(mpfcs_setup_frame, width = 10)
vna_span_txt.grid(row = 10, column = 1)
vna_span_txt.insert(tk.END, '2')

vna_sweep_pts_lbl = tk.Label(mpfcs_setup_frame, text = "# Sweep Points:")
vna_sweep_pts_lbl.grid(row = 11, column = 0)
vna_sweep_pts_txt = tk.Entry(mpfcs_setup_frame, width = 10)
vna_sweep_pts_txt.grid(row = 11, column = 1)
vna_sweep_pts_txt.insert(tk.END, '11')

# s = ttk.Separator(mpfcs_setup_frame,orient='horizontal')
# s.pack(side='top', fill='x')
# ttk.Separator(mpfcs_setup_frame,orient='horizontal').grid(row=11, column=3, sticky='ns')
tk.Label(mpfcs_setup_frame, text = "Logging Setup ------------").grid(row = 12, column = 0)

filename_lbl = tk.Label(mpfcs_setup_frame, text = "Output File Name:")
filename_lbl.grid(row = 13, column = 0)
filename_txt = tk.Entry(mpfcs_setup_frame, width = 10)
filename_txt.grid(row = 13, column = 1)
filename_txt.insert(tk.END, 'vna_00')

submit_val = tk.Button(mpfcs_setup_frame, text = 'Check Inputs', command = handler_submit_values, font = 'Helvetica 10 bold')
submit_val.grid(row = 14, column = 0, padx = 5, pady = 5)

reset_VNA = tk.Button(mpfcs_setup_frame, text = 'Reset Inputs', command = handler_vna_reset, state = 'disabled', font = 'Helvetica 10 bold')
reset_VNA.grid(row = 14, column = 1, padx = 5, pady = 5)

home_set_btn = tk.Button(mpfcs_setup_frame, text= 'Set XYZ Home', command = handler_home_set)
home_set_btn.grid(row = 15, column = 0)

go_home_xyz_btn = tk.Button(mpfcs_setup_frame, text= 'Go XYZ Home', command = handler_go_home_xyz)
go_home_xyz_btn.grid(row = 15, column = 1)

start_btn = tk.Button(mpfcs_setup_frame, text= 'Start', command = handler_mpfcs_run, bg="green", fg="black", font = 'Helvetica 18 bold')
start_btn.grid(row = 16, column = 1, padx = 10, pady = 5)
start_btn.configure(state = 'disabled')

##################################### Graphing Tab
graph_tab_label_frame =  ttk.LabelFrame(GraphTab, text = 'Log File Name:')
graph_tab_label_frame.pack(fill = tk.BOTH, expand = False)
Parameters = ttk.LabelFrame(GraphTab, text = 'S-Parameter Selections')
Parameters.pack(fill=tk.BOTH, expand=True)

# Setting up layout
file_name = tk.Label(graph_tab_label_frame, text = "File Name:")
file_name.grid(row = 0, column = 0)
file_txt = tk.Entry(graph_tab_label_frame, width = 20, state = 'normal')
file_txt.grid(row = 0, column = 1)

# setting up buttons

btnSend = tk.Button(graph_tab_label_frame, text = 'Set', command = handler_send, state = 'normal', bg = 'green', fg = 'black')
btnSend.grid(row = 0, column = 2, padx = 10, pady = 5)

btnSend = tk.Button(graph_tab_label_frame, text = 'Reset', command = handler_reset_graph, state = 'normal', bg = 'red', fg = 'black')
btnSend.grid(row = 0, column = 3, padx = 10, pady = 5)

s11 = tk.Button(Parameters, text= 'S11', command = handler_s11_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s11.grid(row = 0, column = 0, padx = 10, pady = 5)

s12 = tk.Button(Parameters, text= 'S12', command = handler_s12_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s12.grid(row = 0, column = 2, padx = 10, pady = 5)

s22 = tk.Button(Parameters, text= 'S22', command = handler_s22_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s22.grid(row = 0, column = 4, padx = 10, pady = 5)

s21 = tk.Button(Parameters, text= 'S21', command = handler_s21_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s21.grid(row = 0, column = 6, padx = 10, pady = 5)

################################################# Manual Motion Tab

#-------------------------- MPFCS Manual Tilt/Pan Step

manual_tp_label_frame =  ttk.LabelFrame(CalibTab, text = 'MPCNC Tilt/Pan')
manual_tp_label_frame.pack(fill = tk.BOTH, expand=True, side = 'left')
Parameters.pack(fill=tk.BOTH, expand=True)

manual_pan_lbl = tk.Label(manual_tp_label_frame, text = "Pan Angle (-90 to 90deg):")
manual_pan_lbl.grid(row = 1, column = 0)
manual_pan_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal')
manual_pan_txt.grid(row = 1, column = 1)
manual_pan_confm_lbl = tk.Label(manual_tp_label_frame, text = "")
manual_pan_confm_lbl.grid(row = 1, column = 3)

manual_pan_btn = tk.Button(manual_tp_label_frame, text= 'Send', command = handler_tp_head_pan)
manual_pan_btn.grid(row = 1, column = 2)
manual_pan_btn_step_pos = tk.Button(manual_tp_label_frame, text= '+', command = handler_tp_head_pan_step)
manual_pan_btn_step_pos.grid(row = 1, column = 3)
manual_pan_btn_step_neg = tk.Button(manual_tp_label_frame, text= '-', command = handler_tp_head_pan_step)
manual_pan_btn_step_neg.grid(row = 1, column = 4)

manual_tilt_lbl = tk.Label(manual_tp_label_frame, text = "Tilt Angle (0 to 90deg):")
manual_tilt_lbl.grid(row = 2, column = 0)
manual_tilt_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal')
manual_tilt_txt.grid(row = 2, column = 1)
manual_tilt_confm_lbl = tk.Label(manual_tp_label_frame, text = "")
manual_tilt_confm_lbl.grid(row = 2, column = 3)

manual_tilt_btn = tk.Button(manual_tp_label_frame, text= 'Send', command = handler_tp_head_tilt)
manual_tilt_btn.grid(row = 2, column = 2)
manual_tilt_btn_step_pos = tk.Button(manual_tp_label_frame, text= '+', command = handler_tp_head_tilt_step)
manual_tilt_btn_step_pos.grid(row = 2, column = 3)
manual_tilt_btn_step_neg = tk.Button(manual_tp_label_frame, text= '-', command = handler_tp_head_tilt_step)
manual_tilt_btn_step_neg.grid(row = 2, column = 4)

manual_tp_reset_btn = tk.Button(manual_tp_label_frame, text= 'Reset', bg="red", command = handler_tp_head_resets)
manual_tp_reset_btn.grid(row = 3, column = 2)

#-------------------------- MPFCS Manual XYZ Step

manual_home_label_frame =  ttk.LabelFrame(CalibTab, text = 'Home')
manual_home_label_frame.pack(fill = tk.BOTH, expand=True, side = 'bottom')

manual_home_set_btn = tk.Button(manual_home_label_frame, text= 'Set', command = handler_home_set)
manual_home_set_btn.grid(row = 0, column = 1)

manual_go_home_x_btn = tk.Button(manual_home_label_frame, text= 'Go X Home', command = handler_go_home_x)
manual_go_home_x_btn.grid(row = 1, column = 0)

manual_go_home_y_btn = tk.Button(manual_home_label_frame, text= 'Go Y Home', command = handler_go_home_y)
manual_go_home_y_btn.grid(row = 1, column = 1)

manual_go_home_z_btn = tk.Button(manual_home_label_frame, text= 'Go Z Home', command = handler_go_home_z)
manual_go_home_z_btn.grid(row = 1, column = 2)

manual_go_home_xyz_btn = tk.Button(manual_home_label_frame, text= 'Go XYZ Home', command = handler_go_home_xyz)
manual_go_home_xyz_btn.grid(row = 2, column = 1)

#-------------------------- MPFCS Manual XYZ Set

manual_xyz_label_frame =  ttk.LabelFrame(CalibTab, text = 'MPCNC XYZ')
manual_xyz_label_frame.pack(fill = tk.BOTH, expand=True, side = 'right')

# manual_loc_edit = ttk.IntVar()
# manual_step_button = tk.Radiobutton(manual_xyz_label_frame, text="Steps", variable=manual_loc_edit,
#                             indicatoron=False, value=0, width=8, command=handler_manual_step_loc_switch)
# manual_loc_button = tk.Radiobutton(manual_xyz_label_frame, text="Location (relative to Home)", variable=manual_loc_edit,
#                             indicatoron=False, value=1, width=8, command=handler_manual_step_loc_switch)
# 
# manual_step_button.grid(row = 0, column = 0)
# manual_loc_button.grid(row = 0, column = 1)

# manual_x_step_size_lbl = tk.Label(manual_xyz_label_frame, text = "X Step Size (mm):") ## used to be samplingF
# manual_x_step_size_lbl.grid(row = 1, column = 0)
# manual_x_step_size_txt = tk.Entry(manual_xyz_label_frame, width = 10)
# manual_x_step_size_txt.grid(row = 1, column = 1)
# manual_x_step_size_txt.insert(tk.END, '10')
# manual_x_step_size_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_mpcnc_step_x)
# manual_x_step_size_btn.grid(row = 1, column = 2)
# manual_x_step_size_btn.configure(state = 'disabled')

# manual_y_step_size_lbl = tk.Label(manual_xyz_label_frame, text = "Y Step Size (mm):")
# manual_y_step_size_lbl.grid(row = 2, column = 0)
# manual_y_step_size_txt = tk.Entry(manual_xyz_label_frame, width = 10)
# manual_y_step_size_txt.grid(row = 2, column = 1)
# manual_y_step_size_txt.insert(tk.END, '10')
# manual_y_step_size_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_mpcnc_step_y)
# manual_y_step_size_btn.grid(row = 2, column = 2)
# manual_y_step_size_btn.configure(state = 'disabled')
# 
# manual_z_step_size_lbl = tk.Label(manual_xyz_label_frame, text = "Z Step Size (mm):")
# manual_z_step_size_lbl.grid(row = 3, column = 0)
# manual_z_step_size_txt = tk.Entry(manual_xyz_label_frame, width = 10)
# manual_z_step_size_txt.grid(row = 3, column = 1)
# manual_z_step_size_txt.insert(tk.END, '10')
# manual_z_step_size_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_mpcnc_step_z)
# manual_z_step_size_btn.grid(row = 3, column = 3)
# manual_z_step_size_btn.configure(state = 'disabled')

manual_x_lbl = tk.Label(manual_xyz_label_frame, text = "X Location (mm):") ## used to be samplingF
manual_x_lbl.grid(row = 0, column = 0)
manual_x_txt = tk.Entry(manual_xyz_label_frame, width = 10)
manual_x_txt.grid(row = 0, column = 1)
manual_x_txt.insert(tk.END, '10')
manual_x_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_manual_loc_x)
manual_x_btn.grid(row = 0, column = 2)

manual_x_step_pos_btn = tk.Button(manual_xyz_label_frame, text= '+', command = handler_manual_step_x)
manual_x_step_pos_btn.grid(row = 0, column = 3)
manual_x_step_neg_btn = tk.Button(manual_xyz_label_frame, text= '-', command = handler_manual_step_x)
manual_x_step_neg_btn.grid(row = 0, column = 4)

manual_y_lbl = tk.Label(manual_xyz_label_frame, text = "Y Location (mm):")
manual_y_lbl.grid(row = 1, column = 0)
manual_y_txt = tk.Entry(manual_xyz_label_frame, width = 10)
manual_y_txt.grid(row = 1, column = 1)
manual_y_txt.insert(tk.END, '10')
manual_y_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_manual_loc_y)
manual_y_btn.grid(row = 1, column = 2)
manual_y_step_pos_btn = tk.Button(manual_xyz_label_frame, text= '+', command = handler_manual_step_y)
manual_y_step_pos_btn.grid(row = 1, column = 3)
manual_y_step_neg_btn = tk.Button(manual_xyz_label_frame, text= '-', command = handler_manual_step_y)
manual_y_step_neg_btn.grid(row = 1, column = 4)

manual_z_lbl = tk.Label(manual_xyz_label_frame, text = "Z Location (mm):")
manual_z_lbl.grid(row = 2, column = 0)
manual_z_txt = tk.Entry(manual_xyz_label_frame, width = 10)
manual_z_txt.grid(row = 2, column = 1)
manual_z_txt.insert(tk.END, '10')
manual_z_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_manual_loc_z)
manual_z_btn.grid(row = 2, column = 2)
manual_z_step_pos_btn = tk.Button(manual_xyz_label_frame, text= '+', command = handler_manual_step_z)
manual_z_step_pos_btn.grid(row = 2, column = 3)
manual_z_step_neg_btn = tk.Button(manual_xyz_label_frame, text= '-', command = handler_manual_step_z)
manual_z_step_neg_btn.grid(row = 2, column = 4)

manual_speed_lbl = tk.Label(manual_xyz_label_frame, text = "Speed (mm/s???):")
manual_speed_lbl.grid(row = 3, column = 0)
manual_speed_txt = tk.Entry(manual_xyz_label_frame, width = 10)
manual_speed_txt.grid(row = 3, column = 1)
manual_speed_txt.insert(tk.END, '600')
manual_speed_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_manual_loc_z)
manual_speed_btn.grid(row = 3, column = 2)

manual_reset_btn = tk.Button(manual_xyz_label_frame, text= 'Reset', bg="red", command = handler_manual_reset)
manual_reset_btn.grid(row = 4, column = 0)

#initialize the timer
hours_took = 0

######################### end of code

window.mainloop()
