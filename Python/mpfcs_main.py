"""
@brief The system scans a 3D space with user-defined parameters to
create 3D graphs of electromagnetic fields for wireless power systems.

@authors: usmank13, chasewhyte, Tri Nguyen

"""
DEBUG = True

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
from Backend.mpfcs_mpcnc import mpcnc_move_xyz, mpcnc_pause, mpcnc_home_xyz, mpcnc_pos_read

emergency_stop_triggered = False

a4982_steps_per_rev = 200.0;
a4982_u_steps_per_step = 16.0;
a4982_gear_teeth = 16.0;
belt_teeth_per_mm = 1.0/2.0; # Approximated, due to stretch of band
leadscrew_pitch = 1.4111 # ??? 2 mm/revolution = T8

XY_MM_PER_STEP = 1.0/(a4982_steps_per_rev*a4982_u_steps_per_step*belt_teeth_per_mm/a4982_gear_teeth)
Z_MM_PER_STEP = 1.0/(a4982_steps_per_rev*a4982_u_steps_per_step/leadscrew_pitch)

if DEBUG == False:
#     Initializing communication 
    rm = visa.ResourceManager()
    visa_vna = rm.open_resource('GPIB0::16')
    print("VNA: {}".format(visa_vna.query('*IDN?')))
    ser_rambo = serial.Serial('COM6') # name of port, this might be different because of the hub we use
    ser_rambo.baudrate = 250000
    print("RAMBo Controller for MPCNC: {}".format(ser_rambo.name))
    print("10sec Delay for Boot-up...")
    time.sleep(10)

def handler_tp_head_tilt():
    tp_head_tilt(tilt_entry_txt, ser_rambo)
    
def handler_tp_head_tilt_step_pos():
    if tilt_entry_txt.get() == '0':
        manual_tilt_step = tp_usecs_2_deg(1)
    else:
        manual_tilt_step = float(tilt_entry_txt.get())
        
    tilt_entry_txt.set(str(float(tilt_entry_txt.get()) + manual_tilt_step))
    tp_head_tilt(tilt_entry_txt, ser_rambo)
    
def handler_tp_head_tilt_step_neg():
    if tilt_entry_txt.get() == '0':
        manual_tilt_step = -tp_usecs_2_deg(1)
    else:
        manual_tilt_step = -float(tilt_entry_txt.get())
        
    tilt_entry_txt.set(str(float(tilt_entry_txt.get()) + manual_tilt_step))
    tp_head_tilt(tilt_entry_txt, ser_rambo)
    
def handler_tp_head_pan():
    tp_head_pan(pan_entry_txt, ser_rambo)
    
def handler_tp_head_pan_step_pos():
    if pan_entry_txt.get() == '0':
        manual_pan_step = tp_usecs_2_deg(1)
    else:
        manual_pan_step = float(pan_entry_txt.get())
        
    pan_entry_txt.set(str(float(pan_entry_txt.get()) + manual_pan_step))
    tp_head_pan(pan_entry_txt, ser_rambo)
    
def handler_tp_head_pan_step_neg():
    if pan_entry_txt.get() == '0':
        manual_pan_step = -tp_usecs_2_deg(1)
    else:
        manual_pan_step = -float(pan_entry_txt.get())
        
    pan_entry_txt.set(str(float(pan_entry_txt.get()) + manual_pan_step))
    tp_head_pan(pan_entry_txt, ser_rambo)

def handler_tp_head_resets():
    tp_head_resets(tp_reset_btn, tilt_entry_txt, pan_entry_txt, ser_rambo)
    
# def handler_tp_home_set():
#     tp_home_xyz('set', ser_rambo)
    
def handler_mpfcs_run():
    mpfcs_run(reset_VNA, start_btn, mpcnc_vol_length_entry_txt, mpcnc_vol_width_entry_txt,\
              mpcnc_dwell_duration_entry_txt, mpcnc_x_step_size_entry_txt,\
              mpcnc_y_step_size_entry_txt, mpcnc_vol_height_entry_txt, vna_center_freq_entry_txt,\
              vna_span_entry_txt, vna_sweep_pts_entry_txt, mpcnc_z_step_size_entry_txt,\
              filename_entry_txt, mpfcs_setup_frame)

def handler_mpfcs_stop():
    ser_rambo.write(("M0").encode())
    ser_rambo.write(b'\n') 
    
def handler_manual_step_pos_x():
    if manual_x_step_entry_txt.get() == '0':
        manual_x_step = XY_MM_PER_STEP
    else:
        manual_x_step = float(manual_x_step_entry_txt.get())
        
    manual_x_entry_txt.set(str(float(manual_x_entry_txt.get()) + manual_x_step))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)
    
def handler_manual_step_neg_x():
    if manual_x_step_entry_txt.get() == '0':
        manual_x_step = -XY_MM_PER_STEP
    else:
        manual_x_step = -float(manual_x_step_entry_txt.get())
        
    manual_x_entry_txt.set(str(float(manual_x_entry_txt.get()) + manual_x_step))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)
    
def handler_manual_step_pos_y():
    if manual_y_step_entry_txt.get() == '0':
        manual_y_step = XY_MM_PER_STEP
    else:
        manual_y_step = float(manual_y_step_entry_txt.get())
        
    manual_y_entry_txt.set(str(float(manual_y_entry_txt.get()) + manual_y_step))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)
    
def handler_manual_step_neg_y():
    if manual_y_step_entry_txt.get() == '0':
        manual_y_step = -XY_MM_PER_STEP
    else:
        manual_y_step = -float(manual_y_step_entry_txt.get())
        
    manual_y_entry_txt.set(str(float(manual_y_entry_txt.get()) + manual_y_step))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)

def handler_manual_step_pos_z():
    if manual_z_step_entry_txt.get() == '0':
        manual_z_step = Z_MM_PER_STEP
    else:
        manual_z_step = float(manual_z_step_entry_txt.get())
        
    manual_z_entry_txt.set(str(float(manual_z_entry_txt.get()) + manual_z_step))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)
    
def handler_manual_step_neg_z():
    if manual_z_step_entry_txt.get() == '0':
        manual_z_step = -Z_MM_PER_STEP
    else:
        manual_z_step = -float(manual_z_step_entry_txt.get())
        
    manual_z_entry_txt.set(str(float(manual_z_entry_txt.get()) + manual_z_step))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)
    
def handler_manual_loc():
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)

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
    manual_x_entry_txt.set(str(0))
    manual_y_entry_txt.set(str(0))
    manual_z_entry_txt.set(str(0))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)
    
def handler_go_home_x():
    mpcnc_home_xyz('x', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)
    
def handler_go_home_y():
    mpcnc_home_xyz('y', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)
    
def handler_go_home_z():
    mpcnc_home_xyz('z', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)
    
def handler_go_home_xyz():
    mpcnc_home_xyz('xyz', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)

def handler_home_set():
    mpcnc_home_xyz('set', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)    
        
def handler_submit_values():
    submit_values(submit_val, start_btn, tp_reset_btn, mpcnc_vol_length_entry_txt, mpcnc_vol_width_entry_txt,\
                  mpcnc_dwell_duration_entry_txt, mpcnc_x_step_size_entry_txt, mpcnc_y_step_size_entry_txt,\
                  mpcnc_vol_height_entry_txt, vna_center_freq_entry_txt, vna_span_entry_txt, vna_sweep_pts_entry_txt,\
                  mpcnc_z_step_size_entry_txt, filename_entry_txt)
    
def handler_vna_reset():
    vna_buttons_reset(reset_VNA, submit_val, mpcnc_vol_length_entry_txt, mpcnc_vol_width_entry_txt, \
                      mpcnc_dwell_duration_entry_txt, mpcnc_x_step_size_entry_txt, mpcnc_y_step_size_entry_txt,\
                      mpcnc_vol_height_entry_txt, vna_center_freq_entry_txt, vna_span_entry_txt,vna_sweep_pts_entry_txt,\
                      mpcnc_z_step_size_entry_txt, filename_entry_txt)

def handler_send():
    file_txt.configure(state = 'disabled')

def handler_reset_graph():
    file_txt.configure(state = 'normal')
    
def handler_s11_plt():
    filename_input = file_entry_txt.get()
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
    filename_input = file_entry_txt.get()
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
    filename_input = file_entry_txt.get()
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
    filename_input = file_entry_txt.get()
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

@param[in] txt0-filename_entry_txt: System input values
"""
def mpfcs_run(reset_VNA,start_btn,mpcnc_vol_length_entry_txt,mpcnc_vol_width_entry_txt,\
              mpcnc_dwell_duration_entry_txt,mpcnc_x_step_size_entry_txt,\
              mpcnc_y_step_size_entry_txt,mpcnc_vol_height_entry_txt,vna_center_freq_entry_txt,\
              vna_span_entry_txt,vna_sweep_pts_entry_txt,mpcnc_z_step_size_entry_txt,\
              filename_entry_txt, mpfcs_setup_frame):
    reset_VNA.configure(state = 'disabled')
    start_btn.configure(state = 'disabled')
    #getting user inputs
    length = int(mpcnc_vol_length_entry_txt.get())
    print("Length: " + str(length))
    width = int(mpcnc_vol_width_entry_txt.get())
    print("Width: " + str(width))
    PauseDur = int(mpcnc_dwell_duration_entry_txt.get())
    xStep = int(mpcnc_x_step_size_entry_txt.get())
    yStep = int(mpcnc_y_step_size_entry_txt.get())
    depth = int(mpcnc_vol_height_entry_txt.get())
    print("Height: " + str(depth))
    center_freq = float(vna_center_freq_entry_txt.get())
    span = int(vna_span_entry_txt.get())
    num_points = int(vna_sweep_pts_entry_txt.get())
    zStep = int(mpcnc_z_step_size_entry_txt.get())
    txt_fileName = filename_entry_txt.get()
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
    manual_x_entry_txt.set(str(0))
    manual_y_entry_txt.set(str(0))
    manual_z_entry_txt.set(str(0))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)

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
        ser_rambo.write(b'\n') 
        ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
        ser_rambo.write(b'\n')
        time.sleep(0.2)
        ser_rambo.write(("M280"+" P3"+" S"+str(tilt_deg)).encode()) # Roll serial write
        ser_rambo.write(b'\n') 
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
        ser_rambo.write(b'\n') 
        ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
        ser_rambo.write(b'\n')
        time.sleep(0.5)
        
    for z_coord in sampling_z_coordinates: # for each z plane 
        manual_z_entry_txt.set(str(z_coord))
        print("\nz_coord = {}".format(z_coord))        
        y_positive_direction = not(y_positive_direction)
#         print("y_positive_direction = {}".format(y_positive_direction))
        if y_positive_direction == True:
            _sampling_y_coordinates = sampling_y_coordinates
        else:
            _sampling_y_coordinates = reversed(sampling_y_coordinates)
             
        for y_coord in _sampling_y_coordinates: # for each row
            f.write("\n")
            manual_y_entry_txt.set(str(y_coord))
            print("\ny_coord = {}".format(y_coord))
            x_positive_direction = not(x_positive_direction)
#             print("x_positive_direction = {}".format(x_positive_direction))
            if x_positive_direction:
                _sampling_x_coordinates = sampling_x_coordinates
            else:
                _sampling_x_coordinates = reversed(sampling_x_coordinates)
             
            for x_coord in _sampling_x_coordinates: # moves the tool to each successive sampling spot in the row
                speed = speed_default*2;
                manual_x_entry_txt.set(str(x_coord))
                print("x_coord = {}".format(x_coord))
                mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, ser_rambo)
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
                 
    
    home_sel = 'x'
    mpcnc_home_xyz(home_sel, manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)

    home_sel = 'y'
    mpcnc_home_xyz(home_sel, manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)
    
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
    
# def mpcnc_step_xyz(x_step, y_step, z_step, manual_speed, setting, ser_rambo):
#     if setting == 0:
#         mpcnc_step_xyz.x_loc = 0
#         mpcnc_step_xyz.y_loc = 0
#         mpcnc_step_xyz.z_loc = 0
#     elif setting == 1:
#     # Getting user inputs    
#         mpcnc_step_xyz.x_loc += float(manual_x_step_size_entry_txt.get())
#         print("X Location: " + str(mpcnc_step_xyz.x_loc))
#         mpcnc_step_xyz.y_loc += float(manual_y_step_size_entry_txt.get())
#         print("Y Location: " + str(mpcnc_step_xyz.y_loc))
#         mpcnc_step_xyz.z_loc += float(manual_z_step_size_entry_txt.get())
#         print("Z Location: " + str(mpcnc_step_xyz.z_loc))
#     else:
#         mpcnc_step_xyz.x_loc = float(x_step)
#         mpcnc_step_xyz.y_loc = float(y_step)
#         mpcnc_step_xyz.z_loc = float(z_step)
#         
#     manual_x_entry_txt.set(str(mpcnc_step_xyz.x_loc))
#     manual_y_entry_txt.set(str(mpcnc_step_xyz.y_loc))
#     manual_z_entry_txt.set(str(mpcnc_step_xyz.z_loc))
# 
#     speed_default = 10*60 # 10mm/s*60s/1min
#     speed = manual_speed;
#     mpcnc_move_xyz(mpcnc_step_xyz.x_loc, mpcnc_step_xyz.y_loc, mpcnc_step_xyz.z_loc, speed, ser_rambo) # to initialize position

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

################################################# Manual Motion Tab

#-------------------------- MPFCS Manual Tilt/Pan Step

manual_tp_label_frame =  ttk.LabelFrame(CalibTab, text = 'MPCNC Tilt/Pan')
manual_tp_label_frame.pack(fill = tk.BOTH, expand=True, side = 'left')
# Parameters.pack(fill=tk.BOTH, expand=True)

manual_tilt_lbl = tk.Label(manual_tp_label_frame, text = "Tilt Angle (0 to 90deg):")
manual_tilt_lbl.grid(row = 1, column = 0)
tilt_entry_txt = tk.StringVar()
manual_tilt_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=tilt_entry_txt)
tilt_entry_txt.set("0")
manual_tilt_txt.grid(row = 1, column = 1, padx=(10,10))
# manual_tilt_confm_lbl = tk.Label(manual_tp_label_frame, text = "")
# manual_tilt_confm_lbl.grid(row = 2, column = 3)
manual_tilt_btn = tk.Button(manual_tp_label_frame, text= 'Send', command = handler_tp_head_tilt)
manual_tilt_btn.grid(row = 1, column = 2)

manual_tilt_step_entry_txt = tk.StringVar()
manual_tilt_step_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=manual_tilt_step_entry_txt)
manual_tilt_step_txt.grid(row = 1, column = 3, padx=(10,10))
manual_tilt_step_entry_txt.set("0")

manual_tilt_btn_step_pos = tk.Button(manual_tp_label_frame, text= '+', command = handler_tp_head_tilt_step_pos)
manual_tilt_btn_step_pos.grid(row = 1, column = 4)
manual_tilt_btn_step_neg = tk.Button(manual_tp_label_frame, text= '-', command = handler_tp_head_tilt_step_neg)
manual_tilt_btn_step_neg.grid(row = 1, column = 5)

manual_pan_lbl = tk.Label(manual_tp_label_frame, text = "Pan Angle (-90 to 90deg):")
manual_pan_lbl.grid(row = 2, column = 0)
pan_entry_txt = tk.StringVar()
manual_pan_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=pan_entry_txt)
pan_entry_txt.set("0")
manual_pan_txt.grid(row = 2, column = 1, padx=(10,10))
manual_pan_btn = tk.Button(manual_tp_label_frame, text= 'Send', command = handler_tp_head_pan)
manual_pan_btn.grid(row = 2, column = 2)
# manual_pan_confm_lbl = tk.Label(manual_tp_label_frame, text = "")
# manual_pan_confm_lbl.grid(row = 1, column = 3)

manual_pan_step_entry_txt = tk.StringVar()
manual_pan_step_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=manual_pan_step_entry_txt)
manual_pan_step_txt.grid(row = 2, column = 3, padx=(10,10))
manual_pan_step_entry_txt.set("0")

manual_pan_btn_step_pos = tk.Button(manual_tp_label_frame, text= '+', command = handler_tp_head_pan_step_pos)
manual_pan_btn_step_pos.grid(row = 2, column = 4)
manual_pan_btn_step_neg = tk.Button(manual_tp_label_frame, text= '-', command = handler_tp_head_pan_step_neg)
manual_pan_btn_step_neg.grid(row = 2, column = 5)

manual_tp_reset_btn = tk.Button(manual_tp_label_frame, text= 'Reset', bg="red", command = handler_tp_head_resets)
manual_tp_reset_btn.grid(row = 3, column = 2)

#-------------------------- MPFCS Manual XYZ Step

manual_home_label_frame =  ttk.LabelFrame(CalibTab, text = 'Home')
manual_home_label_frame.pack(fill = tk.BOTH, expand=True, side = 'bottom')

manual_home_set_btn = tk.Button(manual_home_label_frame, width = 10, text= 'Set', command = handler_home_set)
manual_home_set_btn.grid(row = 0, column = 1)

manual_go_home_x_btn = tk.Button(manual_home_label_frame, width = 10, text= 'Go X Home', command = handler_go_home_x)
manual_go_home_x_btn.grid(row = 1, column = 0)

manual_go_home_y_btn = tk.Button(manual_home_label_frame, width = 10, text= 'Go Y Home', command = handler_go_home_y)
manual_go_home_y_btn.grid(row = 1, column = 1)

manual_go_home_z_btn = tk.Button(manual_home_label_frame, width = 10, text= 'Go Z Home', command = handler_go_home_z)
manual_go_home_z_btn.grid(row = 1, column = 2)

manual_go_home_xyz_btn = tk.Button(manual_home_label_frame, width = 10, text= 'Go XYZ Home', command = handler_go_home_xyz)
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
# manual_x_step_size_txt.insert(0, '10')
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
manual_x_entry_txt = tk.StringVar()
manual_x_txt = tk.Entry(manual_xyz_label_frame, width = 10, textvariable=manual_x_entry_txt)
manual_x_entry_txt.set("?")
manual_x_txt.grid(row = 0, column = 1, padx=(10,10))
manual_x_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_manual_loc)
manual_x_btn.grid(row = 0, column = 2)

manual_x_step_entry_txt = tk.StringVar()
manual_x_step_txt = tk.Entry(manual_xyz_label_frame, width = 10, textvariable=manual_x_step_entry_txt)
manual_x_step_txt.grid(row = 0, column = 3, padx=(10,10))
manual_x_step_entry_txt.set("0")

manual_x_step_pos_btn = tk.Button(manual_xyz_label_frame, text= '+', command = handler_manual_step_pos_x)
manual_x_step_pos_btn.grid(row = 0, column = 4)
manual_x_step_neg_btn = tk.Button(manual_xyz_label_frame, text= '-', command = handler_manual_step_neg_x)
manual_x_step_neg_btn.grid(row = 0, column = 5)

manual_y_lbl = tk.Label(manual_xyz_label_frame, text = "Y Location (mm):")
manual_y_lbl.grid(row = 1, column = 0)
manual_y_entry_txt = tk.StringVar()
manual_y_txt = tk.Entry(manual_xyz_label_frame, width = 10, textvariable=manual_y_entry_txt)
manual_y_entry_txt.set("?")
manual_y_txt.grid(row = 1, column = 1, padx=(10,10))
manual_y_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_manual_loc)
manual_y_btn.grid(row = 1, column = 2)

manual_y_step_entry_txt = tk.StringVar()
manual_y_step_txt = tk.Entry(manual_xyz_label_frame, width = 10, textvariable=manual_y_step_entry_txt)
manual_y_step_txt.grid(row = 1, column = 3, padx=(10,10))
manual_y_step_entry_txt.set("0")

manual_y_step_pos_btn = tk.Button(manual_xyz_label_frame, text= '+', command = handler_manual_step_pos_y)
manual_y_step_pos_btn.grid(row = 1, column = 4)
manual_y_step_neg_btn = tk.Button(manual_xyz_label_frame, text= '-', command = handler_manual_step_neg_y)
manual_y_step_neg_btn.grid(row = 1, column = 5)

manual_z_lbl = tk.Label(manual_xyz_label_frame, text = "Z Location (mm):")
manual_z_lbl.grid(row = 2, column = 0)
manual_z_entry_txt = tk.StringVar()
manual_z_txt = tk.Entry(manual_xyz_label_frame, width = 10, textvariable=manual_z_entry_txt)
manual_z_entry_txt.set("?")
manual_z_txt.grid(row = 2, column = 1, padx=(10,10))
manual_z_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_manual_loc)
manual_z_btn.grid(row = 2, column = 2)

manual_z_step_entry_txt = tk.StringVar()
manual_z_step_txt = tk.Entry(manual_xyz_label_frame, width = 10, textvariable=manual_z_step_entry_txt)
manual_z_step_txt.grid(row = 2, column = 3, padx=(10,10))
manual_z_step_entry_txt.set("0")

manual_z_step_pos_btn = tk.Button(manual_xyz_label_frame, text= '+', command = handler_manual_step_pos_z)
manual_z_step_pos_btn.grid(row = 2, column = 4)
manual_z_step_neg_btn = tk.Button(manual_xyz_label_frame, text= '-', command = handler_manual_step_neg_z)
manual_z_step_neg_btn.grid(row = 2, column = 5)

manual_speed_lbl = tk.Label(manual_xyz_label_frame, text = "Speed (mm/s???):")
manual_speed_lbl.grid(row = 3, column = 0)
manual_speed_entry_txt = tk.StringVar()
manual_speed_txt = tk.Entry(manual_xyz_label_frame, width = 10, textvariable=manual_speed_entry_txt)
manual_speed_entry_txt.set("600")
manual_speed_txt.grid(row = 3, column = 1)
manual_speed_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_manual_loc)
manual_speed_btn.grid(row = 3, column = 2)

manual_reset_btn = tk.Button(manual_xyz_label_frame, text= 'Reset', bg="red", command = handler_manual_reset)
manual_reset_btn.grid(row = 4, column = 0)

manual_stop_btn = tk.Button(manual_xyz_label_frame, text= 'Stop', command = handler_mpfcs_stop, bg="red", fg="black", font = 'Helvetica 18 bold')
manual_stop_btn.grid(row = 4, column = 1, padx = 10, pady = 5)
manual_stop_btn.configure(state = 'normal')

##################################### MPFCS Tab

# Live Frame -------------------------------
Live_Panel = ttk.LabelFrame(MPFCSTab, text = 'Live View')
Live_Panel.pack(fill = tk.BOTH, expand = True, side = 'left')

# Tilt/Pan Frame -------------------------------

tp_label_frame = ttk.LabelFrame(MPFCSTab, text = 'Tilt and Pan')
tp_label_frame.pack(fill=tk.BOTH, expand=True, side = 'left')

tilt_lbl = tk.Label(tp_label_frame, text = "Tilt Angle (-90 to 90deg):")
tilt_lbl.grid(row = 1, column = 0)
tilt_txt = tk.Entry(tp_label_frame, width = 10, textvariable=tilt_entry_txt)
tilt_txt.grid(row = 1, column = 1)
# tilt_confm_lbl = tk.Label(tp_label_frame, text = "")
# tilt_confm_lbl.grid(row = 1, column = 3)

pan_lbl = tk.Label(tp_label_frame, text = "Pan Servo Angle (0-180):")
pan_lbl.grid(row = 2, column = 0)
pan_txt = tk.Entry(tp_label_frame, width = 10, textvariable=pan_entry_txt)
pan_txt.grid(row = 2, column = 1)
# pan_confm_lbl = tk.Label(tp_label_frame, text = "")
# pan_confm_lbl.grid(row = 2, column = 3)

# tk.Button layouts
tilt_btn1 = tk.Button(tp_label_frame, text= 'Send', command = handler_tp_head_tilt)
tilt_btn1.grid(row = 1, column = 2)

pan_btn1 = tk.Button(tp_label_frame, text= 'Send', command = handler_tp_head_pan)
pan_btn1.grid(row = 2, column = 2)

# tp_home_set_btn = tk.Button(tp_label_frame, text= 'Set Tilt/Pan Home', command = handler_tp_home_set)
# tp_home_set_btn.grid(row = 3, column = 0)

tp_reset_btn = tk.Button(tp_label_frame, text="Reset to 0deg", command = handler_tp_head_resets,\
                         state = 'normal',  bg="red", fg="black", font = 'Helvetica 10')
tp_reset_btn.grid(row = 3, column = 2, pady = 5)

# MPFCS Frame -------------------------------

mpfcs_setup_frame = ttk.LabelFrame(MPFCSTab, text = '')
mpfcs_setup_frame.pack(fill=tk.BOTH, expand=True,side = 'left')
tk.Label(mpfcs_setup_frame, text = "MPCNC Setup - Head XYZ(mm): "+manual_x_entry_txt.get()+","+manual_y_entry_txt.get()+","+manual_z_entry_txt.get()).grid(row = 0, column = 0)

mpcnc_vol_length_lbl = tk.Label(mpfcs_setup_frame, text = "Scan Volume Length (mm): ")
mpcnc_vol_length_lbl.grid(row = 1, column = 0)
mpcnc_vol_length_entry_txt = tk.StringVar()
mpcnc_vol_length_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_vol_length_entry_txt)
mpcnc_vol_length_entry_txt.set("30")
mpcnc_vol_length_txt.grid(row = 1, column = 1)

mpcnc_vol_width_lbl = tk.Label(mpfcs_setup_frame, text = "Scan Volume Width (mm):")
mpcnc_vol_width_lbl.grid(row = 2, column = 0)
mpcnc_vol_width_entry_txt = tk.StringVar()
mpcnc_vol_width_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_vol_width_entry_txt)
mpcnc_vol_width_entry_txt.set("30")
mpcnc_vol_width_txt.grid(row = 2, column = 1)

mpcnc_vol_height_lbl = tk.Label(mpfcs_setup_frame, text = "Scan Volume Height (mm):") # used to be called depth
mpcnc_vol_height_lbl.grid(row = 3, column = 0)
mpcnc_vol_height_entry_txt = tk.StringVar()
mpcnc_vol_height_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_vol_height_entry_txt)
mpcnc_vol_height_entry_txt.set("20")
mpcnc_vol_height_txt.grid(row = 3, column = 1)

mpcnc_x_step_size_lbl = tk.Label(mpfcs_setup_frame, text = "X Step Size (mm):") ## used to be samplingF
mpcnc_x_step_size_lbl.grid(row = 4, column = 0)
mpcnc_x_step_size_entry_txt = tk.StringVar()
mpcnc_x_step_size_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_x_step_size_entry_txt)
mpcnc_x_step_size_entry_txt.set("10")
mpcnc_x_step_size_txt.grid(row = 4, column = 1)

mpcnc_y_step_size_lbl = tk.Label(mpfcs_setup_frame, text = "Y Step Size (mm):")
mpcnc_y_step_size_lbl.grid(row = 5, column = 0)
mpcnc_y_step_size_entry_txt = tk.StringVar()
mpcnc_y_step_size_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_y_step_size_entry_txt)
mpcnc_y_step_size_entry_txt.set("10")
mpcnc_y_step_size_txt.grid(row = 5, column = 1)

mpcnc_z_step_size_lbl = tk.Label(mpfcs_setup_frame, text = "Z Step Size (mm):")
mpcnc_z_step_size_lbl.grid(row = 6, column = 0)
mpcnc_z_step_size_entry_txt = tk.StringVar()
mpcnc_z_step_size_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_z_step_size_entry_txt)
mpcnc_z_step_size_entry_txt.set("5")
mpcnc_z_step_size_txt.grid(row = 6, column = 1)

mpcnc_dwell_duration_lbl = tk.Label(mpfcs_setup_frame, text = "Pause duration (s):")
mpcnc_dwell_duration_lbl.grid(row = 7, column = 0)
mpcnc_dwell_duration_entry_txt = tk.StringVar()
mpcnc_dwell_duration_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_dwell_duration_entry_txt)
mpcnc_dwell_duration_entry_txt.set("1")
mpcnc_dwell_duration_txt.grid(row = 7, column = 1)

# ttk.Separator(mpfcs_setup_frame,orient='horizontal').grid(row=7, columnspan=200)
tk.Label(mpfcs_setup_frame, text = "VNA Setup ------------").grid(row = 8, column = 0)

vna_center_freq_lbl = tk.Label(mpfcs_setup_frame, text = "Center Frequency (MHz):")
vna_center_freq_lbl.grid(row = 9, column = 0)
vna_center_freq_entry_txt = tk.StringVar()
vna_center_freq_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=vna_center_freq_entry_txt)
vna_center_freq_entry_txt.set("13.56")
vna_center_freq_txt.grid(row = 9, column = 1)

vna_span_lbl = tk.Label(mpfcs_setup_frame, text = "Span (MHz):")
vna_span_lbl.grid(row = 10, column = 0)
vna_span_entry_txt = tk.StringVar()
vna_span_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=vna_span_entry_txt)
vna_span_entry_txt.set("2")
vna_span_txt.grid(row = 10, column = 1)

vna_sweep_pts_lbl = tk.Label(mpfcs_setup_frame, text = "# Sweep Points:")
vna_sweep_pts_lbl.grid(row = 11, column = 0)
vna_sweep_pts_entry_txt = tk.StringVar()
vna_sweep_pts_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=vna_sweep_pts_entry_txt)
vna_sweep_pts_entry_txt.set("11")
vna_sweep_pts_txt.grid(row = 11, column = 1)

# s = ttk.Separator(mpfcs_setup_frame,orient='horizontal')
# s.pack(side='top', fill='x')
# ttk.Separator(mpfcs_setup_frame,orient='horizontal').grid(row=11, column=3, sticky='ns')
tk.Label(mpfcs_setup_frame, text = "Logging Setup ------------").grid(row = 12, column = 0)

filename_lbl = tk.Label(mpfcs_setup_frame, text = "Output File Name:")
filename_lbl.grid(row = 13, column = 0)
filename_entry_txt = tk.StringVar()
filename_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=filename_entry_txt)
filename_entry_txt.set("vna_00")
filename_txt.grid(row = 13, column = 1)

submit_val = tk.Button(mpfcs_setup_frame, text = 'Check Inputs', command = handler_submit_values, font = 'Helvetica 10 bold')
submit_val.grid(row = 14, column = 0, padx = 5, pady = 5)

reset_VNA = tk.Button(mpfcs_setup_frame, text = 'Reset Inputs', command = handler_vna_reset, state = 'disabled', font = 'Helvetica 10 bold')
reset_VNA.grid(row = 14, column = 1, padx = 5, pady = 5)

home_set_btn = tk.Button(mpfcs_setup_frame, text= 'Set XYZ Home', command = handler_home_set)
home_set_btn.grid(row = 15, column = 0)

go_home_xyz_btn = tk.Button(mpfcs_setup_frame, text= 'Go XYZ Home', command = handler_go_home_xyz)
go_home_xyz_btn.grid(row = 15, column = 1)

start_btn = tk.Button(mpfcs_setup_frame, text= 'Start', command = handler_mpfcs_run, bg="green", fg="black", font = 'Helvetica 18 bold')
start_btn.grid(row = 16, column = 0, padx = 10, pady = 5)
start_btn.configure(state = 'disabled')

stop_btn = tk.Button(mpfcs_setup_frame, text= 'Stop', command = handler_mpfcs_stop, bg="red", fg="black", font = 'Helvetica 18 bold')
stop_btn.grid(row = 16, column = 1, padx = 10, pady = 5)
stop_btn.configure(state = 'disabled')

##################################### Graphing Tab
graph_tab_label_frame =  ttk.LabelFrame(GraphTab, text = 'Log File Name:')
graph_tab_label_frame.pack(fill = tk.BOTH, expand = False)
Parameters = ttk.LabelFrame(GraphTab, text = 'S-Parameter Selections')
Parameters.pack(fill=tk.BOTH, expand=True)

# Setting up layout
graph_file_name = tk.Label(graph_tab_label_frame, text = "File Name:")
graph_file_name.grid(row = 0, column = 0)
graph_filename_entry_txt = tk.StringVar()
graph_filename_txt = tk.Entry(graph_tab_label_frame, width = 10, textvariable=filename_entry_txt)
graph_filename_entry_txt.set("vna_00")
graph_file_entry_txt = tk.StringVar()
graph_file_txt = tk.Entry(graph_tab_label_frame, width = 20, textvariable=graph_file_entry_txt)
graph_file_entry_txt.set("vna_01")
graph_file_txt.grid(row = 0, column = 1)

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

#initialize the timer
hours_took = 0
if DEBUG == False:
#     manual_x_entry_txt.set(str(0))
#     manual_y_entry_txt.set(str(0))
#     manual_z_entry_txt.set(str(0))
#     mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
#                manual_z_entry_txt, manual_speed_entry_txt,\
#                is_step, ser_rambo)
    tilt_entry_txt.set("0")
    pan_entry_txt.set("0")
    tp_head_resets(tp_reset_btn, tilt_entry_txt, pan_entry_txt, ser_rambo)
#     mpcnc_home_xyz('xyz', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)

######################### end of code

window.mainloop()
