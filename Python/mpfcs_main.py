"""
@brief The system scans a 3D space with user-defined parameters to
create 3D graphs of electromagnetic fields for wireless power systems.

@authors: usmank13, chasewhyte, Tri Nguyen

"""
DEBUG = False
TILT_SERVO = "HS-53"
PAN_SERVO = "HS-5055MG-R"

BED_SIZE_X = 600
BED_SIZE_Y = 600
BED_SIZE_Z = 300
Z_ENDSTOP_HEIGHT_MM = 10

import os
import numpy as np
import pandas as pd
import serial
import time
import datetime
import pyvisa as visa
from tkinter import ttk, messagebox
import tkinter as tk
import matplotlib.pyplot as plt 
from mpl_toolkits.mplot3d import Axes3D

from Frontend.mpfcs_gui_button_functions import submit_values, vna_buttons_reset
from Backend.mpfcs_vna import vna_init, vna_record#, vna_q_calc
from Backend.mpfcs_tp_head import tp_head_tilt, tp_head_pan, tp_head_resets, tp_usecs_2_deg
from Backend.mpfcs_mpcnc import mpcnc_move_xyz, mpcnc_pause, mpcnc_home_xyz, mpcnc_pos_read, marlin_readline_startup

emergency_stop_triggered = False

a4982_steps_per_rev = 200.0;
a4982_u_steps_per_step = 16.0;
a4982_gear_teeth = 16.0;
belt_teeth_per_mm = 1.0/2.0; # Approximated, due to stretch of band
leadscrew_pitch = 4*2 #1.4111 # ??? 2 mm/revolution = T8

XY_MM_PER_STEP = 0.2 # 1.0/(a4982_steps_per_rev*a4982_u_steps_per_step*belt_teeth_per_mm/a4982_gear_teeth)
Z_MM_PER_STEP = 0.2 #1.0/(a4982_steps_per_rev*a4982_u_steps_per_step/leadscrew_pitch)

if DEBUG == False:
#     Initializing communication 
    rm = visa.ResourceManager()
    visa_vna = rm.open_resource('GPIB0::16')
    print("VNA: {}".format(visa_vna.query('*IDN?')))
    ser_rambo = serial.Serial('COM3', 250000, timeout=1.0) # name of port, this might be different because of the hub we use
#     ser_rambo.baudrate = 250000
    print("RAMBo Controller for MPCNC: {}".format(ser_rambo.name))
    print("\n10sec Delay for Marlin Boot-up...")
    time.sleep(10)
    marlin_readline_startup(ser_rambo)


def handler_tp_head_tilt():
    tp_head_tilt(tilt_entry_txt, ser_rambo)
    
def handler_tp_head_tilt_step_pos():
    if manual_tilt_step_entry_txt.get() == '0':
        manual_tilt_step = tp_usecs_2_deg(1, TILT_SERVO)
    else:
        manual_tilt_step = float(tilt_entry_txt.get())
    
#     print("{}, {}, {}".format(manual_tilt_step, float(tilt_entry_txt.get()), float(tilt_entry_txt.get()) + manual_tilt_step))
    tilt_entry_txt.set(str(round(float(tilt_entry_txt.get()) + manual_tilt_step,3)))
    tp_head_tilt(tilt_entry_txt, ser_rambo)
    
def handler_tp_head_tilt_step_neg():
    if manual_tilt_step_entry_txt.get() == '0':
        manual_tilt_step = -tp_usecs_2_deg(1, TILT_SERVO)
    else:
        manual_tilt_step = -float(tilt_entry_txt.get())
        
    tilt_entry_txt.set(str(round(float(tilt_entry_txt.get()) + manual_tilt_step,3)))
    tp_head_tilt(tilt_entry_txt, ser_rambo)
    
def handler_tp_head_pan():
    tp_head_pan(pan_entry_txt, ser_rambo)
    
def handler_tp_head_pan_step_pos():
    if manual_pan_step_entry_txt.get() == '0':
        manual_pan_step = tp_usecs_2_deg(1, PAN_SERVO)
    else:
        manual_pan_step = float(pan_entry_txt.get())
        
    pan_entry_txt.set(str(round(float(pan_entry_txt.get()) + manual_pan_step,3)))
    tp_head_pan(pan_entry_txt, ser_rambo)
    
def handler_tp_head_pan_step_neg():
    if manual_pan_step_entry_txt.get() == '0':
        manual_pan_step = -tp_usecs_2_deg(1, PAN_SERVO)
    else:
        manual_pan_step = -float(pan_entry_txt.get())
        
    pan_entry_txt.set(str(round(float(pan_entry_txt.get()) + manual_pan_step,3)))
    tp_head_pan(pan_entry_txt, ser_rambo)

def handler_tp_head_resets():
    tp_head_resets(tp_reset_btn, tilt_entry_txt, pan_entry_txt, ser_rambo)
    
def handler_gcode():
    cmd = gcode_entry_txt.get()
    ser_rambo.write(cmd.encode()+b'\n')
    marlin_output = ser_rambo.readline()
    while marlin_output:
        print(marlin_output)
        marlin_output = ser_rambo.readline()
    
# def handler_tp_home_set():
#     tp_home_xyz('set', ser_rambo)
    
def handler_mpfcs_run():
    mpfcs_run(reset_VNA, start_btn, mpcnc_vol_length_entry_txt, mpcnc_vol_width_entry_txt,\
              mpcnc_dwell_duration_entry_txt, mpcnc_x_step_size_entry_txt,\
              mpcnc_y_step_size_entry_txt, mpcnc_vol_height_entry_txt, vna_center_freq_entry_txt,\
              vna_span_entry_txt, vna_sweep_pts_entry_txt, mpcnc_z_step_size_entry_txt,\
              filename_entry_txt, mpfcs_setup_frame)

def handler_mpfcs_stop():
    ser_rambo.write(("M0").encode()+b'\n')
    
def handler_manual_step_pos_x():
    if manual_x_step_entry_txt.get() == '0':
        manual_x_step = XY_MM_PER_STEP
    else:
        manual_x_step = float(manual_x_step_entry_txt.get())
        
    manual_x_entry_txt.set(str(round(float(manual_x_entry_txt.get()) + manual_x_step,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    
def handler_manual_step_neg_x():
    if manual_x_step_entry_txt.get() == '0':
        manual_x_step = -XY_MM_PER_STEP
    else:
        manual_x_step = -float(manual_x_step_entry_txt.get())
        
    manual_x_entry_txt.set(str(round(float(manual_x_entry_txt.get()) + manual_x_step,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    
def handler_manual_step_pos_y():
    if manual_y_step_entry_txt.get() == '0':
        manual_y_step = XY_MM_PER_STEP
    else:
        manual_y_step = float(manual_y_step_entry_txt.get())
        
    manual_y_entry_txt.set(str(round(float(manual_y_entry_txt.get()) + manual_y_step,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    
def handler_manual_step_neg_y():
    if manual_y_step_entry_txt.get() == '0':
        manual_y_step = -XY_MM_PER_STEP
    else:
        manual_y_step = -float(manual_y_step_entry_txt.get())
        
    manual_y_entry_txt.set(str(round(float(manual_y_entry_txt.get()) + manual_y_step,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)

def handler_manual_step_pos_z():
    if manual_z_step_entry_txt.get() == '0':
        manual_z_step = Z_MM_PER_STEP
    else:
        manual_z_step = float(manual_z_step_entry_txt.get())
        
    manual_z_entry_txt.set(str(round(float(manual_z_entry_txt.get()) + manual_z_step,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    
def handler_manual_step_neg_z():
    if manual_z_step_entry_txt.get() == '0':
        manual_z_step = -Z_MM_PER_STEP
    else:
        manual_z_step = -float(manual_z_step_entry_txt.get())
        
    manual_z_entry_txt.set(str(round(float(manual_z_entry_txt.get()) + manual_z_step,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    
def handler_manual_loc():
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)

# def handler_manual_step_loc_switch():
#     if manual_loc_edit.get() == 0:
#         manual_x_step_size_btn.configure(state = 'normal')
#         manual_y_step_size_btn.configure(state = 'normal')
#         manual_z_step_size_btn.configure(state = 'normal')
#         manual_x_btn.configure(state = 'disabled')
#         manual_y_btn.configure(state = 'disabled')
#         manual_z_btn.configure(state = 'disabled')
#     else:
#         manual_x_step_size_btn.configure(state = 'disabled')
#         manual_y_step_size_btn.configure(state = 'disabled')
#         manual_z_step_size_btn.configure(state = 'disabled')
#         manual_x_btn.configure(state = 'normal')
#         manual_y_btn.configure(state = 'normal')
#         manual_z_btn.configure(state = 'normal')

def handler_manual_reset():
    manual_x_entry_txt.set(str(round(0,3)))
    manual_y_entry_txt.set(str(round(0,3)))
    manual_z_entry_txt.set(str(round(0,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    
def handler_manual_circle_init():
    radius = float(manual_radius_entry_txt.get())
    x_loc = mpcnc_move_xyz.x_loc
    y_loc = mpcnc_move_xyz.y_loc
    z_loc = mpcnc_move_xyz.z_loc
    if x_loc-radius <= 0 or y_loc-radius<=0 or z_loc-radius<=0:
        messagebox.showerror("Bounds Error", "Head Tip must be more than {}mm from volume edge".format(radius)) #Note: -30deg limit due to Tilt Structure being obstructed Tilt Servo
        manual_circle_init_btn.configure('disabled')
        return

    manual_circle_xy_btn.configure(state = 'normal')
    handler_manual_circle_xy.angles = np.linspace(0, 360, int(manual_circle_steps_entry_txt.get())+1)
    handler_manual_circle_xy.step = 0
    handler_manual_circle_xy.x_entry_text = manual_x_entry_txt.get()
    handler_manual_circle_xy.y_entry_text = manual_y_entry_txt.get()
    
    manual_circle_xz_btn.configure(state = 'normal')
    handler_manual_circle_xz.angles = np.linspace(0, 360, int(manual_circle_steps_entry_txt.get())+1)
    handler_manual_circle_xz.step = 0
    handler_manual_circle_xz.x_entry_text = manual_x_entry_txt.get()
    handler_manual_circle_xz.z_entry_text = manual_z_entry_txt.get()
    
    manual_circle_yz_btn.configure(state = 'normal')
    handler_manual_circle_yz.angles = np.linspace(0, 360, int(manual_circle_steps_entry_txt.get())+1)
    handler_manual_circle_yz.step = 0
    handler_manual_circle_yz.y_entry_text = manual_y_entry_txt.get()
    handler_manual_circle_yz.z_entry_text = manual_z_entry_txt.get()
    
def handler_manual_circle_xy():
    if handler_manual_circle_xy.x_entry_text != manual_x_entry_txt.get()\
        or handler_manual_circle_xy.y_entry_text != manual_y_entry_txt.get():
        manual_x_entry_txt.set(str(round(float(handler_manual_circle_xy.x_entry_text),3)))
        manual_y_entry_txt.set(str(round(float(handler_manual_circle_xy.y_entry_text),3)))
        mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    angle = handler_manual_circle_xy.angles[handler_manual_circle_xy.step]
    radius = float(manual_radius_entry_txt.get())    
    radian = angle*(2*np.pi/360)
    x_pos = radius*np.cos(radian)
    y_pos = radius*np.sin(radian)
    manual_x_entry_txt.set(str(round(x_pos,3)))
    manual_y_entry_txt.set(str(round(y_pos,3)))
    print("Step: {} - Circle Target X,Y: {},{}".format(handler_manual_circle_xy.step+1, manual_x_entry_txt.get(), manual_y_entry_txt.get()))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
#         time.sleep(30)
#     print("Circle Result X,Y:{},{}".format(manual_x_entry_txt.get(), manual_y_entry_txt.get()))
    if len(handler_manual_circle_xy.angles)-1 == handler_manual_circle_xy.step:
        handler_manual_circle_xy.step = 0;
    else:
        handler_manual_circle_xy.step += 1;
    
def handler_manual_circle_xz():
    if handler_manual_circle_xz.x_entry_text != manual_x_entry_txt.get()\
        or handler_manual_circle_xz.z_entry_text != manual_z_entry_txt.get():
        manual_x_entry_txt.set(str(round(float(handler_manual_circle_xz.x_entry_text),3)))
        manual_z_entry_txt.set(str(round(float(handler_manual_circle_xz.z_entry_text),3)))
        mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    angle = handler_manual_circle_xz.angles[handler_manual_circle_xz.step]
    radius = float(manual_radius_entry_txt.get())    
    radian = angle*(2*np.pi/360)
    x_pos = radius*np.cos(radian)
    z_pos = radius*np.sin(radian)
    manual_x_entry_txt.set(str(round(x_pos,3)))
    manual_z_entry_txt.set(str(round(z_pos,3)))
    print("Step: {} - Circle Target X,Z: {},{}".format(handler_manual_circle_xz.step+1, manual_x_entry_txt.get(), manual_z_entry_txt.get()))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
#         time.sleep(30)
#     print("Circle Result X,Z:{},{}".format(manual_x_entry_txt.get(), manual_z_entry_txt.get()))
    if len(handler_manual_circle_xz.angles)-1 == handler_manual_circle_xz.step:
        handler_manual_circle_xz.step = 0;
    else:
        handler_manual_circle_xz.step += 1;
    
def handler_manual_circle_yz():
    if handler_manual_circle_yz.z_entry_text != manual_z_entry_txt.get()\
        or handler_manual_circle_yz.y_entry_text != manual_y_entry_txt.get():
        manual_y_entry_txt.set(str(round(float(handler_manual_circle_yz.y_entry_text),3)))
        manual_z_entry_txt.set(str(round(float(handler_manual_circle_yz.z_entry_text),3)))
        mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    angle = handler_manual_circle_yz.angles[handler_manual_circle_yz.step]
    radius = float(manual_radius_entry_txt.get())    
    radian = angle*(2*np.pi/360)
    y_pos = radius*np.cos(radian)
    z_pos = radius*np.sin(radian)
    manual_y_entry_txt.set(str(round(y_pos,3)))
    manual_z_entry_txt.set(str(round(z_pos,3)))
    print("Step: {} - Circle Target: Y,Z: {},{}".format(handler_manual_circle_yz.step+1, manual_y_entry_txt.get(), manual_z_entry_txt.get()))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
#         time.sleep(30)
#     print("Circle Result Y,Z:{},{}".format(manual_y_entry_txt.get(), manual_z_entry_txt.get()))
    if len(handler_manual_circle_yz.angles)-1 == handler_manual_circle_yz.step:
        handler_manual_circle_yz.step = 0;
    else:
        handler_manual_circle_yz.step += 1;

    
def handler_go_home_x():
    mpcnc_home_xyz('x', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)
    
    
def handler_go_home_y():
    mpcnc_home_xyz('y', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)
    
def handler_go_home_z():
    mpcnc_home_xyz('z', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)
    manual_z_entry_txt.set(str(round(20.0,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    
def handler_go_home_xyz():
    mpcnc_home_xyz('xyz', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)
    manual_z_entry_txt.set(str(round(20.0,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)

def handler_set_relative_home():
    mpcnc_home_xyz('set', manual_speed_entry_txt, manual_x_entry_txt, manual_y_entry_txt, manual_z_entry_txt, ser_rambo)
    manual_circle_init_btn.configure(state = 'normal')    
    start_btn.configure(state = 'normal')   
        
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
    
def handler_od_vol_setup():
    coil_od = float(od_vol_od_entry_txt.get())
    od_vol_critical_coupling_multplier = float(od_vol_critical_coupling_multplier_entry_txt.get())
    vol_max = str(np.rint((od_vol_critical_coupling_multplier*np.sqrt(2)*coil_od)/10)*10)
    
    mpcnc_vol_length_entry_txt.set(vol_max)
    mpcnc_vol_width_entry_txt.set(vol_max)
    mpcnc_vol_height_entry_txt.set(vol_max)   
    
    mpcnc_x_step_size_entry_txt.set(od_vol_min_step_entry_txt.get())
    mpcnc_y_step_size_entry_txt.set(od_vol_min_step_entry_txt.get())
    mpcnc_z_step_size_entry_txt.set(od_vol_min_step_entry_txt.get())
    
#NOTE: should probably clean this up and make the graphing more modular,
# don't really need diff functions for each s param
def handler_s11_plt():
    filename_input = file_entry_txt.get()
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection = '3d')
    dframe = pd.read_csv(filename_input + '.csv', delimiter=',')
    x = np.asarray(dframe['X Pos'])
    y = np.asarray(dframe['Y Pos'])
    z = np.asarray(dframe['Z Pos'])
    s11 = []
    # append the middle point to s11
    for i in range(len(dframe)):
        arr =  df2['Re[S11]'][i]
        arr = arr.strip("[]")
        arr = np.fromstring(arr, dtype = np.float, sep = ' ')
        mid = int(len(arr) / 2 - 0.5)
        point = arr[mid]
        s11.append(point)
    s11 = np.asarray(s11)
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
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection = '3d')
    dframe = pd.read_csv(filename_input + '.csv', delimiter=',')
    x = np.asarray(dframe['X Pos'])
    y = np.asarray(dframe['Y Pos'])
    z = np.asarray(dframe['Z Pos'])
    s12 = []
    # append the middle point to s12
    for i in range(len(dframe)):
        arr =  df2['Re[S12]'][i]
        arr = arr.strip("[]")
        arr = np.fromstring(arr, dtype = np.float, sep = ' ')
        mid = int(len(arr) / 2 - 0.5)
        point = arr[mid]
        s12.append(point)
    s12 = np.asarray(s12)

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
    dframe = pd.read_csv(filename_input + '.csv', delimiter=',')
    x = np.asarray(dframe['X Pos'])
    y = np.asarray(dframe['Y Pos'])
    z = np.asarray(dframe['Z Pos'])
    s22 = []
    # append the middle point to s22
    for i in range(len(dframe)):
        arr =  df2['Re[S22]'][i]
        arr = arr.strip("[]")
        arr = np.fromstring(arr, dtype = np.float, sep = ' ')
        mid = int(len(arr) / 2 - 0.5)
        point = arr[mid]
        s22.append(point)
    s22 = np.asarray(s22)

    ax1.set_title('S22')
    ax1.set_xlabel('X Position (mm)')
    ax1.set_ylabel('Y Position (mm)')
    ax1.set_zlabel('Z Position (mm)')
    p = ax1.scatter(x, y, z, c = s22, cmap = 'jet')
    colorbar = fig.colorbar(p)
    colorbar.set_label('Decibels')
    plt.show()
    
# note: button should be pressed after all data is collected    
# for s21 I should use the special column maybe
def handler_s21_plt():
    filename_input = file_entry_txt.get()
    fig = plt.figure()
    ax1 = fig.add_subplot(111, projection = '3d')
    dframe = pd.read_csv(filename_input + '.csv', delimiter=',')
    x = np.asarray(dframe['X Pos'])
    y = np.asarray(dframe['Y Pos'])
    z = np.asarray(dframe['Z Pos'])
    s21 = []
    # append the middle point to s21
    for i in range(len(dframe)):
        arr =  df2['Re[S21]'][i]
        arr = arr.strip("[]")
        arr = np.fromstring(arr, dtype = np.float, sep = ' ')
        mid = int(len(arr) / 2 - 0.5)
        point = arr[mid]
        s21.append(point)
    s21 = np.asarray(s21)

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
    scan_running = False
    run_num = 0
    
    #getting user inputs
    vol_length = int(mpcnc_vol_length_entry_txt.get())
    print("Length: " + str(vol_length))
    vol_x_step = int(mpcnc_x_step_size_entry_txt.get())
    
    vol_width = int(mpcnc_vol_width_entry_txt.get())
    print("Width: " + str(vol_width))
    vol_y_step = int(mpcnc_y_step_size_entry_txt.get())
       
    vol_height = int(mpcnc_vol_height_entry_txt.get())
    print("Height: " + str(vol_height))
    vol_z_step = int(mpcnc_z_step_size_entry_txt.get())
    
    mpcnc_pause_dur = float(mpcnc_dwell_duration_entry_txt.get())
    
    vna_center_freq = float(vna_center_freq_entry_txt.get())
    vna_span = int(vna_span_entry_txt.get())
    vna_num_points = int(vna_sweep_pts_entry_txt.get())
    
    save_file_name = filename_entry_txt.get()
    
    then = time.time()
    
    sampling_x_coordinates = []
    sampling_y_coordinates = [] 
    sampling_z_coordinates = []

    if od_vol_od_entry_txt.get() == '0':
        # initializing some values
        sampling_x_coordinates = np.arange(-vol_length/2, vol_length/2+vol_x_step, vol_x_step)
        sampling_y_coordinates = np.arange(-vol_width/2, vol_width/2+vol_y_step, vol_y_step)    
        sampling_z_coordinates = np.arange(-vol_height/2, vol_height/2+vol_z_step, vol_z_step)   
    else:
        sampling_x_coordinates = []
        sampling_y_coordinates = []
        sampling_z_coordinates = [] 
        od_vol_od = np.around(float(od_vol_od_entry_txt.get(),decimals=1))
        od_vol_r = np.around(od_vol_od/2.0,decimals=1)
        
        scan_vol_to_coil_od = 3
        mpcnc_vol_length_entry_txt.set(str(scan_vol_to_coil_od*od_vol_od))
        vol_length = float(mpcnc_vol_length_entry_txt.get())
        critical_coupling_r = np.around(np.sqrt(2)*od_vol_r, decimals=1)
        print("Critical Coupling Radius (mm): {}".format(critical_coupling_r))
        
        pos = np.around(-vol_length/2.0, decimals=1)
        sampling_x_coordinates.append(pos)
        sampling_y_coordinates.append(pos)
        sampling_z_coordinates.append(pos) 
        min_step = float(od_vol_min_step_entry_txt.get())

        mult = BED_SIZE_X
        while pos < 0:     
            _pos = pos + mult*min_step
#             print("_pos: {}|mult*cc: {}".format(_pos, (mult-1)*critical_coupling_r))
        #     if _pos == 0:
        #         break;
        #     if np.abs(_pos) < (mult-1)*critical_coupling_r and mult > 1:
        #         mult -= 1
        #     else:
        #         pos += mult*min_step 
        #         sampling_x_coordinates.append(pos)
        #         sampling_y_coordinates.append(pos)
        #         sampling_z_coordinates.append(pos)     
            if _pos == 0:
                break;
            if np.abs(_pos) < (mult-1)*od_vol_r and mult > 1:
                mult -= 1
            else:
                pos += mult*min_step
                sampling_x_coordinates.append(np.around(pos, decimals=1))
                sampling_y_coordinates.append(np.around(pos, decimals=1))
                sampling_z_coordinates.append(np.around(pos, decimals=1))   
#             print(pos, mult)
            
        # print("#1:{}".format(sampling_x_coordinates))
        
        sampling_x_coordinates_rev = list(np.abs(list(reversed(sampling_x_coordinates))))
        sampling_y_coordinates_rev = list(np.abs(list(reversed(sampling_y_coordinates))))
        sampling_z_coordinates_rev = list(np.abs(list(reversed(sampling_z_coordinates))))
        
        # print("#Rev:{}".format(sampling_x_coordinates_rev))
        
        # sampling_x_coordinates = []
        sampling_y_coordinates = []
        sampling_x_coordinates.append(0.0)
        sampling_y_coordinates.append(0.0)
        sampling_z_coordinates.append(0.0)
        
        sampling_x_coordinates = sampling_x_coordinates + sampling_x_coordinates_rev
        sampling_y_coordinates = sampling_y_coordinates + sampling_y_coordinates_rev
        sampling_z_coordinates = sampling_z_coordinates + sampling_z_coordinates_rev
        
        # print("#1:{}".format(sampling_x_coordinates))
        
        print("x_coords: {}".format(sampling_x_coordinates))
        print("y_coords: {}".format(sampling_y_coordinates))
        print("z_coords: {}".format(sampling_z_coordinates))
        
#         print("Len: {}| hrs: {}".format(len(sampling_x_coordinates), 4*len(sampling_x_coordinates)*len(sampling_y_coordinates)*len(sampling_z_coordinates)/3600))
    
    s11_array = np.array([])
    s12_array = np.array([])
    s21_array = np.array([])
    s22_array = np.array([])
    x_coords = np.array([])
    y_coords = np.array([])
    z_coords = np.array([])
    
    # data_array_dimensions: 
    #    [Run #][Measurement #]
    #    [X Pos][Y Pos][Z Pos]
    #    [Tilt Angle (deg)][Pan Angle (deg)]
    #    [Center Frequency]
    #    [S11], Re[S11], Im[S11]
    #    [S12], Re[S12], Im[S12]
    #    [S21], Re[S21], Im[S21]
    #    [S22], Re[S22], Im[S22]
    data_rec = np.zeros((len(sampling_x_coordinates),len(sampling_y_coordinates),len(sampling_z_coordinates),25),dtype=np.float32)
    print("Data Shape: {}| Memory Footprint: {}kB".format(np.shape(data_rec), round(float(data_rec.size*data_rec.itemsize)/1024), 3))

    firstRun = 0;

    num_meas = len(sampling_x_coordinates)*len(sampling_y_coordinates)*len(sampling_z_coordinates)

    measurements = {'run_number': [], 'measurement_number': [], 'tilt_angle': [], 'pan_angle': [],\
                    'z_endstop_height': [], 'coil_height': [], 'x_offset': [], 'y_offset': [], 'z_offset': [],\
                    'x_pos': [], 'y_pos': [], 'z_pos': [], 's11_logm':[], 's11_re':[], 's11_im':[],\
                    's12_logm':[], 's12_re':[], 's12_im':[], 's21_logm':[], 's21_re':[], 's21_im':[],\
                    's22_logm':[], 's22_re':[], 's22_im':[], 'b_field': []}

    s_parameters_measured = 4
    record_time_avg=0.001
    move_dur_avg = 2.5 #seconds
    if mpcnc_pause_dur > move_dur_avg:
        estimated_time = ((mpcnc_pause_dur+1)+(s_parameters_measured*0.204)+ record_time_avg)*num_meas
    else:
        estimated_time = (move_dur_avg+(s_parameters_measured*0.204)+ record_time_avg)*num_meas
        
    hrs_mins_secs_remaining = datetime.timedelta(0, estimated_time)
    print('Estimated time to completion (hours): ' + str(estimated_time/3600))

#     f = open(save_file_name+".txt", "w")

    #initialize VNA
    vna_init(vna_num_points, visa_vna, vna_center_freq, vna_span)

    #3D plots for S11, S12, S21, S22
    s_param_fig=plt.figure(1)
#     plt.ion()
#     plt.show()
    s_param_fig.tight_layout(pad=3.0)
    ax1 = s_param_fig.add_subplot(221, projection = '3d')
    ax1.set_title('S11')
    ax1.set_xlabel('X Position (mm)')
    ax1.set_ylabel('Y Position (mm)')
    ax1.set_zlabel('Z Position (mm)')
    ax1.view_init(elev=30, azim=30)
 
    ax2 = s_param_fig.add_subplot(222, projection = '3d')
    ax2.set_title('S12')
    ax2.set_xlabel('X Position (mm)')
    ax2.set_ylabel('Y Position (mm)')
    ax2.set_zlabel('Z Position (mm)')
    ax2.view_init(elev=30, azim=30)
     
    ax3 = s_param_fig.add_subplot(223, projection = '3d')
    ax3.set_title('S21')
    ax3.set_xlabel('X Position (mm)')
    ax3.set_ylabel('Y Position (mm)')
    ax3.set_zlabel('Z Position (mm)')
    ax3.view_init(elev=30, azim=30)
 
    ax4 = s_param_fig.add_subplot(224, projection = '3d')
    ax4.set_title('S22')
    ax4.set_xlabel('X Position (mm)')
    ax4.set_ylabel('Y Position (mm)')
    ax4.set_zlabel('Z Position (mm)')
    ax4.view_init(elev=30, azim=30)
    
#     print("x_coords: {}".format(sampling_x_coordinates))
#     print("y_coords: {}".format(sampling_y_coordinates))
#     print("z_coords: {}".format(sampling_z_coordinates))

    # Safety extent sweep and plot extent setup
    print("\n\n--------------------------")
    print("Starting Volume Extent Sweep...")
    z_extent_array = [sampling_z_coordinates[0], sampling_z_coordinates[-1]]
    y_extent_array = [sampling_y_coordinates[0], sampling_y_coordinates[-1]]
    x_extent_array = [sampling_x_coordinates[0], sampling_x_coordinates[-1]]
    for z_count, z_coord in enumerate(z_extent_array): # for each z plane 
            manual_z_entry_txt.set(str(round(z_coord,3)))                
            for _y_count, y_coord in enumerate(y_extent_array): # for each row
                manual_y_entry_txt.set(str(round(y_coord,3)))
                for _x_count, x_coord in enumerate(x_extent_array): # moves the tool to each successive sampling spot in the row
                    manual_x_entry_txt.set(str(round(x_coord,3)))
                    
                    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                       manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
                    
                    mpcnc_pause(mpcnc_pause_dur, ser_rambo)
      
                    s11_logm = vna_record(vna_num_points, 'S11', 'LOGM', visa_vna) #magnitude value
                    s12_logm = vna_record(vna_num_points, 'S12', 'LOGM', visa_vna)
                    s21_logm = vna_record(vna_num_points, 'S21', 'LOGM', visa_vna)
                    s22_logm = vna_record(vna_num_points, 'S22', 'LOGM', visa_vna)
                    
                    s11_re, s11_im = vna_record(vna_num_points, 'S11', 'SMIMRI', visa_vna) #magnitude value
                    s12_re, s12_im = vna_record(vna_num_points, 'S12', 'SMIMRI', visa_vna)
                    s21_re, s21_im = vna_record(vna_num_points, 'S21', 'SMIMRI', visa_vna)
                    s22_re, s22_im = vna_record(vna_num_points, 'S22', 'SMIMRI', visa_vna)
                    
                    x_coords = np.concatenate([x_coords, np.array([x_coord])])
                    y_coords = np.concatenate([y_coords, np.array([y_coord])])
                    z_coords = np.concatenate([z_coords, np.array([z_coord])])
      
                    s11_array = np.concatenate([s11_array, np.array([s11_logm])])
                    s12_array = np.concatenate([s12_array, np.array([s12_logm])])
                    s21_array = np.concatenate([s21_array, np.array([s21_logm])])
                    s22_array = np.concatenate([s22_array, np.array([s22_logm])])
                    #plotting 
#                     s_param_fig.clf()

#                     ax1.cla()
                    ps11 = ax1.scatter(x_coords, y_coords, z_coords, c = s11_array, cmap = 'jet')
#                     ax1.imshow()
                    
#                     ax2.cla()
                    ps12 = ax2.scatter(x_coords,y_coords, z_coords, c = s12_array, cmap = 'jet')
#                     ax2.imshow()
                    
#                     ax3.cla()
                    ps21 = ax3.scatter(x_coords,y_coords, z_coords, c = s21_array, cmap = 'jet')
#                     ax3.imshow()
                     
#                     ax4.cla()
                    ps22 = ax4.scatter(x_coords,y_coords, z_coords, c = s22_array, cmap = 'jet') 
#                     ax4.imshow()
          
#                     plt.draw()
                    plt.pause(0.01)
    
    # Return to Relative Home
    manual_z_entry_txt.set(str(0.0))
    manual_y_entry_txt.set(str(0.0))
    manual_x_entry_txt.set(str(0.0))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
    
    print("\n\n--------------------------")
    print("Starting Volume Characterization...")
    
    # Slowing down the feedrate during the scan
    mpcnc_init_feedrate = float(manual_speed_entry_txt.get())
#     vol_step_list = [vol_x_step, vol_y_step, vol_z_step]
#     largest_step_size = 100 # units: mm
#     manual_speed_entry_txt.set(str(mpcnc_init_feedrate/(largest_step_size/max(vol_step_list)))) # Decrease the feedrate if the step size is smaller than 100mm
    
#     print("mpcnc_feedrate_str:{}|manual_speed_entry_txt:{}".format(mpcnc_feedrate_str,manual_speed_entry_txt.get()))
    scan_running = True
    meas_count = 0
    vna_read_avg_dur = 0; data_record_avg_dur = 0    
    y_positive_direction = False; x_positive_direction = False
    _z_coord = None
    for z_count, z_coord in enumerate(sampling_z_coordinates): # for each z plane 
#         print("z:{}".format(sampling_z_coordinates))
        manual_z_entry_txt.set(str(round(z_coord,3)))
        
#         print("\nz_coord = {}".format(z_coord))        
        y_positive_direction = not(y_positive_direction)
#         print("y_positive_direction = {}".format(y_positive_direction))
        if y_positive_direction == True:
            _sampling_y_coordinates = sampling_y_coordinates
        else:
            _sampling_y_coordinates = list(reversed(sampling_y_coordinates))
        
#         print("y:{}".format(_sampling_y_coordinates))
        
        for _y_count, y_coord in enumerate(_sampling_y_coordinates): # for each row
#             f.write("\n")
            manual_y_entry_txt.set(str(round(y_coord,3)))
            
            if y_positive_direction:
                y_count = _y_count
            else:
                y_count = len(_sampling_y_coordinates)-_y_count-1
        
#             print("\ny_coord = {}".format(y_coord))
            x_positive_direction = not(x_positive_direction)
#             print("x_positive_direction = {}".format(x_positive_direction))
            if x_positive_direction:
                _sampling_x_coordinates = sampling_x_coordinates
            else:
                _sampling_x_coordinates = list(reversed(sampling_x_coordinates))
            
#             print("x:{}".format(_sampling_x_coordinates))
            
            for _x_count, x_coord in enumerate(_sampling_x_coordinates): # moves the tool to each successive sampling spot in the row
                
                manual_x_entry_txt.set(str(round(x_coord,3)))
#                 print("x_coord = {}".format(x_coord))
                
                time_0 = time.time()
                mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
                   manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)
                if mpcnc_pause_dur > vna_read_avg_dur+data_record_avg_dur:
                    mpcnc_pause(mpcnc_pause_dur-(vna_read_avg_dur+data_record_avg_dur), ser_rambo) 
                time_1 = time.time()
                
                time_diff = time_1-time_0
                if meas_count == 0:
                    mpcnc_move_avg_dur = time_diff
                else:
                    mpcnc_move_avg_dur = float(mpcnc_move_avg_dur+time_diff)/2 # Running average
                
                time_0 = time.time()
                s11_logm = vna_record(vna_num_points, 'S11', 'LOGM', visa_vna) #magnitude value
                s12_logm = vna_record(vna_num_points, 'S12', 'LOGM', visa_vna)
                s21_logm = vna_record(vna_num_points, 'S21', 'LOGM', visa_vna)
                s22_logm = vna_record(vna_num_points, 'S22', 'LOGM', visa_vna)
                
                s11_re, s11_im = 0, 0
                s12_re, s12_im = 0, 0
                s21_re, s21_im = 0, 0
                s22_re, s22_im = 0, 0
                
#                 s11_re, s11_im = vna_record(vna_num_points, 'S11', 'SMIMRI', visa_vna) #magnitude value
#                 s12_re, s12_im = vna_record(vna_num_points, 'S12', 'SMIMRI', visa_vna)
#                 s21_re, s21_im = vna_record(vna_num_points, 'S21', 'SMIMRI', visa_vna)
#                 s22_re, s22_im = vna_record(vna_num_points, 'S22', 'SMIMRI', visa_vna)
                time_1 = time.time()
                time_diff = time_1-time_0
                if meas_count == 0:
                    vna_read_avg_dur = time_diff
                else:
                    vna_read_avg_dur = float(vna_read_avg_dur+time_diff)/2 # Running average
                  
                if x_positive_direction:
                    x_count = _x_count
                else:
                    x_count = len(_sampling_x_coordinates)-_x_count-1
#                 print("S11: ", value, "\nS12: ", value2, "\nS21: ", value3, "\nS22: ", value4, "\n\n")
                
                time_0 = time.time()
                
                b_field = 0.00181026*np.sqrt(10 ** (s21_logm/10))
                
                data_rec[x_count, y_count, z_count, 0] = run_num
                data_rec[x_count, y_count, z_count, 1] = meas_count
                data_rec[x_count, y_count, z_count, 2] = float(tilt_entry_txt.get())
                data_rec[x_count, y_count, z_count, 3] = float(pan_entry_txt.get())
                data_rec[x_count, y_count, z_count, 4] = Z_ENDSTOP_HEIGHT_MM
                data_rec[x_count, y_count, z_count, 5] = float(od_vol_coil_h_entry_txt.get())
                data_rec[x_count, y_count, z_count, 6] = mpcnc_move_xyz.x_offset
                data_rec[x_count, y_count, z_count, 7] = mpcnc_move_xyz.y_offset
                data_rec[x_count, y_count, z_count, 8] = mpcnc_move_xyz.z_offset                
                data_rec[x_count, y_count, z_count, 9] = x_coord
                data_rec[x_count, y_count, z_count, 10] = y_coord
                data_rec[x_count, y_count, z_count, 11] = z_coord

                data_rec[x_count, y_count, z_count, 12] = vna_center_freq
                data_rec[x_count, y_count, z_count, 13] = s11_logm
                data_rec[x_count, y_count, z_count, 14] = s11_re
                data_rec[x_count, y_count, z_count, 15] = s11_im
                data_rec[x_count, y_count, z_count, 16] = s12_logm
                data_rec[x_count, y_count, z_count, 17] = s12_re
                data_rec[x_count, y_count, z_count, 18] = s12_im
                data_rec[x_count, y_count, z_count, 19] = s21_logm
                data_rec[x_count, y_count, z_count, 20] = s21_re
                data_rec[x_count, y_count, z_count, 21] = s21_im
                data_rec[x_count, y_count, z_count, 22] = s22_logm
                data_rec[x_count, y_count, z_count, 23] = s22_re
                data_rec[x_count, y_count, z_count, 24] = s22_im
                
                data_rec[x_count, y_count, z_count, 25] = b_field
                
                x_coords = np.concatenate([x_coords, np.array([x_coord])])
                y_coords = np.concatenate([y_coords, np.array([y_coord])])
                z_coords = np.concatenate([z_coords, np.array([z_coord])])
  
                s11_array = np.concatenate([s11_array, np.array([s11_logm])])
                s12_array = np.concatenate([s12_array, np.array([s12_logm])])
                s21_array = np.concatenate([s21_array, np.array([s21_logm])])
                s22_array = np.concatenate([s22_array, np.array([s22_logm])])
                #plotting 
  
#                 f.write(str(x_coord) + "," + str(y_coord) + "," + str(z_coord) + "," + str(value))
#                 f.write("," + str(value2) + "," + str(value3) + "," + str(value4)) 
#                 f.write("\n")

                # ToDo: might need to update how things are graphed

                # currently run number is always set to 1
                measurements['run_number'].append(1)

                measurements['measurement_number'].append(meas_count + 1)
                
                measurements['tilt_angle'].append(float(tilt_entry_txt.get())) 
                measurements['pan_angle'].append(float(pan_entry_txt.get()))
                
                measurements['z_endstop_height'] = Z_ENDSTOP_HEIGHT_MM
                measurements['coil_height'] = float(od_vol_coil_h_entry_txt.get())
                measurements['x_offset'].append(mpcnc_move_xyz.x_offset)
                measurements['y_offset'].append(mpcnc_move_xyz.y_offset)
                measurements['z_offset'].append(mpcnc_move_xyz.z_offset)                
                measurements['x_pos'].append(x_coord)
                measurements['y_pos'].append(y_coord)
                measurements['z_pos'].append(z_coord)

                measurements['s11_logm'].append(s11_logm)
                measurements['s11_re'].append(s11_re)
                measurements['s11_im'].append(s11_im)
                
                measurements['s12_logm'].append(s12_logm)
                measurements['s12_re'].append(s12_re)
                measurements['s12_im'].append(s12_im)
                
                measurements['s21_logm'].append(s21_logm)
                measurements['s21_re'].append(s21_re)
                measurements['s21_im'].append(s21_im)
                
                measurements['s22_logm'].append(s22_logm)
                measurements['s22_re'].append(s22_re)
                measurements['s22_im'].append(s22_im)

                measurements['b_field'].append(b_field) # B field from S21 as recorded by the Beehive 100b

                if (z_coord != _z_coord) or (z_coord == sampling_z_coordinates[0]): # only plot when z_coord changes or during the first layer
                    if(meas_count != 0):
                        colorbar1.remove()
                        colorbar2.remove()
                        colorbar3.remove()
                        colorbar4.remove()
                    
                    ps11 = ax1.scatter(x_coords, y_coords, z_coords, c = s11_array, cmap = 'jet')
                    colorbar1 = plt.colorbar(ps11, ax = ax1, pad = 0.3)
                    colorbar1.set_label('dB')
                    
                    ps12 = ax2.scatter(x_coords,y_coords, z_coords, c = s12_array, cmap = 'jet')
                    colorbar2 = plt.colorbar(ps12, ax = ax2, pad = 0.3)
                    colorbar2.set_label('dB')
                    
                    ps21 = ax3.scatter(x_coords,y_coords, z_coords, c = s21_array, cmap = 'jet')
                    colorbar3 = plt.colorbar(ps21, ax = ax3, pad = 0.3)
                    colorbar3.set_label('dB')
                    
                    ps22 = ax4.scatter(x_coords,y_coords, z_coords, c = s22_array, cmap = 'jet')
                    colorbar4 = plt.colorbar(ps22, ax = ax4, pad = 0.3)
                    colorbar4.set_label('dB')    
                    
                    plt.pause(0.01)
                    
                    _z_coord = z_coord
                
                time_1 = time.time()
                time_diff = time_1-time_0
                if meas_count == 0:
                    data_record_avg_dur = time_diff
                else:
                    data_record_avg_dur = float(data_record_avg_dur+time_diff)/2 # Running average

                # increment 
                meas_count += 1
                
                percent_complete = round(100*float(meas_count)/num_meas,2)
                
                now = time.time()
                duration_took = now-then
                time_per_meas = duration_took/meas_count
                time_remaining = (num_meas-meas_count)*time_per_meas
                hrs_mins_secs_remaining = datetime.timedelta(0, time_remaining)
                 

                #ToDo: Running average of time to completion
            print("% Complete: {}%| Time Remaining: {}".format(percent_complete, hrs_mins_secs_remaining))
            print("Avg. Duration: Move={}s| VNA={}s| Record={}s".format(round(mpcnc_move_avg_dur,3), round(vna_read_avg_dur,3), round(data_record_avg_dur,3)))
    
    manual_x_entry_txt.set(str(round(0,3)))
    manual_y_entry_txt.set(str(round(0,3)))
    manual_z_entry_txt.set(str(round(0,3)))
    mpcnc_move_xyz(manual_x_entry_txt, manual_y_entry_txt,\
               manual_z_entry_txt, manual_speed_entry_txt, scan_running, ser_rambo)

    with open(save_file_name+'.npy', 'wb') as f:
        np.save(f, data_rec)
    
    print("Saved np.array to {}".format(save_file_name+'.npy'))
    
    # convert measurements to Pandas dataframe
    df = pd.DataFrame(measurements)

    # save to csv in current working directory 
    file_path = os.getcwd()
    
    with open(save_file_name+"_df.csv", "w") as f:
        df.to_csv(f)
        
    print("Saved DataFrame to {}".format(save_file_name+"_df.csv"))

    plt.savefig(save_file_name+'.png')
    
    print("Saved Figure to {}".format(save_file_name+'.png'))
    
    manual_speed_entry_txt.set(str(mpcnc_init_feedrate))
        
#     f.close()
#     ser_rambo.close()

#     plt.ioff()  # Make sure to make plt.show() blocking again, otherwise it'll run
#     plt.show()

    now = time.time()
    duration_took = now-then
    hrs_mins_secs_remaining = datetime.timedelta(0, duration_took)
    print("Total Time: {}".format(hrs_mins_secs_remaining))

    time_disp = tk.Label(mpfcs_setup_frame, text = hours_took, font = 'Helvetica 18 bold' )
    time_disp.grid( row = 15, column = 1, pady = 10, padx = 10)
    
    scan_running = False
    
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
#     manual_x_entry_txt.set(str(round(mpcnc_step_xyz.x_loc,3)))
#     manual_y_entry_txt.set(str(round(mpcnc_step_xyz.y_loc,3)))
#     manual_z_entry_txt.set(str(round(mpcnc_step_xyz.z_loc,3)))
# 
#     speed_default = 10*60 # 10mm/s*60s/1min
#     speed = manual_speed;
#     mpcnc_move_xyz(mpcnc_step_xyz.x_loc, mpcnc_step_xyz.y_loc, mpcnc_step_xyz.z_loc, speed, scan_running, ser_rambo) # to initialize position

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

manual_tilt_lbl = tk.Label(manual_tp_label_frame, text = "Tilt Angle (-30 to 90deg):")
manual_tilt_lbl.grid(row = 1, column = 0)
tilt_entry_txt = tk.StringVar()
manual_tilt_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=tilt_entry_txt)
tilt_entry_txt.set(str(round(0,3)))
manual_tilt_txt.grid(row = 1, column = 1, padx=(10,10))
manual_tilt_btn = tk.Button(manual_tp_label_frame, text= 'Send', command = handler_tp_head_tilt)
manual_tilt_btn.grid(row = 1, column = 2)

manual_tilt_step_entry_txt = tk.StringVar()
manual_tilt_step_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=manual_tilt_step_entry_txt)
manual_tilt_step_txt.grid(row = 1, column = 3, padx=(10,10))
manual_tilt_step_entry_txt.set(str(round(0,3)))

manual_tilt_btn_step_pos = tk.Button(manual_tp_label_frame, text= '+', command = handler_tp_head_tilt_step_pos)
manual_tilt_btn_step_pos.grid(row = 1, column = 4)
manual_tilt_btn_step_neg = tk.Button(manual_tp_label_frame, text= '-', command = handler_tp_head_tilt_step_neg)
manual_tilt_btn_step_neg.grid(row = 1, column = 5)

manual_pan_lbl = tk.Label(manual_tp_label_frame, text = "Pan Angle (-90 to 88deg):")
manual_pan_lbl.grid(row = 2, column = 0)
pan_entry_txt = tk.StringVar()
manual_pan_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=pan_entry_txt)
pan_entry_txt.set(str(round(0,3)))
manual_pan_txt.grid(row = 2, column = 1, padx=(10,10))
manual_pan_btn = tk.Button(manual_tp_label_frame, text= 'Send', command = handler_tp_head_pan)
manual_pan_btn.grid(row = 2, column = 2)
# manual_pan_confm_lbl = tk.Label(manual_tp_label_frame, text = "")
# manual_pan_confm_lbl.grid(row = 1, column = 3)

manual_pan_step_entry_txt = tk.StringVar()
manual_pan_step_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=manual_pan_step_entry_txt)
manual_pan_step_txt.grid(row = 2, column = 3, padx=(10,10))
manual_pan_step_entry_txt.set(str(round(0,3)))

manual_pan_btn_step_pos = tk.Button(manual_tp_label_frame, text= '+', command = handler_tp_head_pan_step_pos)
manual_pan_btn_step_pos.grid(row = 2, column = 4)
manual_pan_btn_step_neg = tk.Button(manual_tp_label_frame, text= '-', command = handler_tp_head_pan_step_neg)
manual_pan_btn_step_neg.grid(row = 2, column = 5)

manual_tp_reset_btn = tk.Button(manual_tp_label_frame, text= 'Reset', bg="red", command = handler_tp_head_resets)
manual_tp_reset_btn.grid(row = 3, column = 2)
tk.Label(manual_tp_label_frame, text = "").grid(row = 4, column = 0)

manual_gcode_lbl = tk.Label(manual_tp_label_frame, text = "GCode:")
manual_gcode_lbl.grid(row = 5, column = 0)
gcode_entry_txt = tk.StringVar()
gcode_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=gcode_entry_txt)
gcode_txt.grid(row = 5, column = 1, padx=(10,10))
gcode_btn = tk.Button(manual_tp_label_frame, text= 'Send', command = handler_gcode)
gcode_btn.grid(row = 5, column = 2)
tk.Label(manual_tp_label_frame, text = "").grid(row = 6, column = 0)

manual_circle_lbl = tk.Label(manual_tp_label_frame, text = "Calibration Circle Step")
manual_circle_lbl.grid(row = 7, column = 0)

manual_radius_lbl = tk.Label(manual_tp_label_frame, text = "Radius (mm):")
manual_radius_lbl.grid(row = 8, column = 0)
manual_radius_entry_txt = tk.StringVar()
manual_radius_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=manual_radius_entry_txt)
manual_radius_entry_txt.set("100")
manual_radius_txt.grid(row = 8, column = 1, padx=(10,10))
manual_circle_steps_entry_txt = tk.StringVar()
manual_circle_steps_txt = tk.Entry(manual_tp_label_frame, width = 10, state = 'normal', textvariable=manual_circle_steps_entry_txt)
manual_circle_steps_entry_txt.set("20")
manual_radius_lbl = tk.Label(manual_tp_label_frame, text = "Steps per 360deg:")
manual_radius_lbl.grid(row = 9, column = 0)
manual_circle_steps_txt.grid(row = 9, column = 1, padx=(10,10))
manual_circle_init_btn = tk.Button(manual_tp_label_frame, text= 'Init. Circle', command = handler_manual_circle_init)
manual_circle_init_btn.configure(state = 'disabled')
manual_circle_init_btn.grid(row = 10, column = 0)
manual_circle_xy_btn = tk.Button(manual_tp_label_frame, text= 'XY Step', command = handler_manual_circle_xy)
manual_circle_xy_btn.configure(state = 'disabled')
manual_circle_xy_btn.grid(row = 10, column = 1)
manual_circle_xz_btn = tk.Button(manual_tp_label_frame, text= 'XZ Step', command = handler_manual_circle_xz)
manual_circle_xz_btn.configure(state = 'disabled')
manual_circle_xz_btn.grid(row = 10, column = 2)
manual_circle_yz_btn = tk.Button(manual_tp_label_frame, text= 'YZ Step', command = handler_manual_circle_yz)
manual_circle_yz_btn.configure(state = 'disabled')
manual_circle_yz_btn.grid(row = 10, column = 3)

#-------------------------- MPFCS Manual XYZ Step

manual_home_label_frame =  ttk.LabelFrame(CalibTab, text = 'Home')
manual_home_label_frame.pack(fill = tk.BOTH, expand=True, side = 'bottom')

manual_set_relative_home_btn = tk.Button(manual_home_label_frame, width = 10, text= 'Set Relative Home', command = handler_set_relative_home)
manual_set_relative_home_btn.grid(row = 0, column = 1)

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
manual_x_step_entry_txt.set(str(round(0,3)))

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
manual_y_step_entry_txt.set(str(round(0,3)))

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
manual_z_step_entry_txt.set(str(round(0,3)))

manual_z_step_pos_btn = tk.Button(manual_xyz_label_frame, text= '+', command = handler_manual_step_pos_z)
manual_z_step_pos_btn.grid(row = 2, column = 4)
manual_z_step_neg_btn = tk.Button(manual_xyz_label_frame, text= '-', command = handler_manual_step_neg_z)
manual_z_step_neg_btn.grid(row = 2, column = 5)

manual_speed_lbl = tk.Label(manual_xyz_label_frame, text = "Speed (mm/min):")
manual_speed_lbl.grid(row = 3, column = 0)
manual_speed_entry_txt = tk.StringVar()
manual_speed_txt = tk.Entry(manual_xyz_label_frame, width = 10, textvariable=manual_speed_entry_txt)
manual_speed_entry_txt.set("1200")
manual_speed_txt.grid(row = 3, column = 1)
# manual_speed_btn = tk.Button(manual_xyz_label_frame, text= 'Send', command = handler_manual_loc)
# manual_speed_btn.grid(row = 3, column = 2)

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

tilt_lbl = tk.Label(tp_label_frame, text = "Tilt Angle (-30 to 90deg):")
tilt_lbl.grid(row = 1, column = 0)
tilt_txt = tk.Entry(tp_label_frame, width = 10, textvariable=tilt_entry_txt)
tilt_txt.grid(row = 1, column = 1)
# tilt_confm_lbl = tk.Label(tp_label_frame, text = "")
# tilt_confm_lbl.grid(row = 1, column = 3)

pan_lbl = tk.Label(tp_label_frame, text = "Pan Servo Angle (-90 to 88deg):")
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

# Coil Outer Diameter Defined Volume Setup Frame -------------------------------

od_vol_frame = ttk.LabelFrame(MPFCSTab, text = 'Radius Volume Setup')
od_vol_frame.pack(fill = tk.BOTH, expand = True, side = 'top')

od_vol_od_lbl = tk.Label(od_vol_frame, text = "Coil Outer Diameter (mm): ")
od_vol_od_lbl.grid(row = 0, column = 0)
od_vol_od_entry_txt = tk.StringVar()
od_vol_od_entry_txt.set("0")
od_vol_od_txt = tk.Entry(od_vol_frame, width = 10, textvariable=od_vol_od_entry_txt)
od_vol_od_txt.grid(row = 0, column = 1)


od_vol_coil_h_lbl = tk.Label(od_vol_frame, text = "Coil Height (mm): ")
od_vol_coil_h_lbl.grid(row = 1, column = 0)
od_vol_coil_h_entry_txt = tk.StringVar()
od_vol_coil_h_entry_txt.set("3")
od_vol_coil_h_txt = tk.Entry(od_vol_frame, width = 10, textvariable=od_vol_coil_h_entry_txt)
od_vol_coil_h_txt.grid(row = 1, column = 1)

od_vol_min_step_lbl = tk.Label(od_vol_frame, text = "Minimum Step Size: ")
od_vol_min_step_lbl.grid(row = 2, column = 0)
od_vol_min_step_entry_txt = tk.StringVar()
od_vol_min_step_entry_txt.set("2")
od_vol_min_step_txt = tk.Entry(od_vol_frame, width = 10, textvariable=od_vol_min_step_entry_txt)
od_vol_min_step_txt.grid(row = 2, column = 1)

od_vol_critical_coupling_multplier_lbl = tk.Label(od_vol_frame, text = "Critical Coupling Radius Multiplier: ")
od_vol_critical_coupling_multplier_lbl.grid(row = 3, column = 0)
od_vol_critical_coupling_multplier_entry_txt = tk.StringVar()
od_vol_critical_coupling_multplier_entry_txt.set("3")
od_vol_critical_coupling_multplier_txt = tk.Entry(od_vol_frame, width = 10, textvariable=od_vol_critical_coupling_multplier_entry_txt)
od_vol_critical_coupling_multplier_txt.grid(row = 3, column = 1)

od_vol_setup_btn = tk.Button(od_vol_frame, text= 'Setup', command = handler_od_vol_setup)
od_vol_setup_btn.grid(row = 3, column = 2)


# MPFCS Frame -------------------------------

mpfcs_setup_frame = ttk.LabelFrame(MPFCSTab, text = '')
mpfcs_setup_frame.pack(fill=tk.BOTH, expand=True,side = 'left')
tk.Label(mpfcs_setup_frame, text = "MPCNC Setup - Head XYZ(mm): "+manual_x_entry_txt.get()+","+manual_y_entry_txt.get()+","+manual_z_entry_txt.get()).grid(row = 0, column = 0)

mpcnc_vol_length_lbl = tk.Label(mpfcs_setup_frame, text = "Scan Volume Length (mm): ")
mpcnc_vol_length_lbl.grid(row = 1, column = 0)
mpcnc_vol_length_entry_txt = tk.StringVar()
mpcnc_vol_length_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_vol_length_entry_txt)
mpcnc_vol_length_entry_txt.set("100")
mpcnc_vol_length_txt.grid(row = 1, column = 1)

mpcnc_vol_width_lbl = tk.Label(mpfcs_setup_frame, text = "Scan Volume Width (mm):")
mpcnc_vol_width_lbl.grid(row = 2, column = 0)
mpcnc_vol_width_entry_txt = tk.StringVar()
mpcnc_vol_width_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_vol_width_entry_txt)
mpcnc_vol_width_entry_txt.set("50")
mpcnc_vol_width_txt.grid(row = 2, column = 1)

mpcnc_vol_height_lbl = tk.Label(mpfcs_setup_frame, text = "Scan Volume Height (mm):")
mpcnc_vol_height_lbl.grid(row = 3, column = 0)
mpcnc_vol_height_entry_txt = tk.StringVar()
mpcnc_vol_height_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_vol_height_entry_txt)
mpcnc_vol_height_entry_txt.set("40")
mpcnc_vol_height_txt.grid(row = 3, column = 1)

mpcnc_x_step_size_lbl = tk.Label(mpfcs_setup_frame, text = "X Min Step Size (mm):") ## used to be samplingF
mpcnc_x_step_size_lbl.grid(row = 4, column = 0)
mpcnc_x_step_size_entry_txt = tk.StringVar()
mpcnc_x_step_size_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_x_step_size_entry_txt)
mpcnc_x_step_size_entry_txt.set("20")
mpcnc_x_step_size_txt.grid(row = 4, column = 1)

mpcnc_y_step_size_lbl = tk.Label(mpfcs_setup_frame, text = "Y Min Step Size (mm):")
mpcnc_y_step_size_lbl.grid(row = 5, column = 0)
mpcnc_y_step_size_entry_txt = tk.StringVar()
mpcnc_y_step_size_txt = tk.Entry(mpfcs_setup_frame, width = 10, textvariable=mpcnc_y_step_size_entry_txt)
mpcnc_y_step_size_entry_txt.set("10")
mpcnc_y_step_size_txt.grid(row = 5, column = 1)

mpcnc_z_step_size_lbl = tk.Label(mpfcs_setup_frame, text = "Z Min Step Size (mm):")
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

set_relative_home_btn = tk.Button(mpfcs_setup_frame, text= 'Set Relative Home', command = handler_set_relative_home)
set_relative_home_btn.grid(row = 15, column = 0)

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

s11_btn = tk.Button(Parameters, text= 'S11', command = handler_s11_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s11_btn.grid(row = 0, column = 0, padx = 10, pady = 5)

s12_btn = tk.Button(Parameters, text= 'S12', command = handler_s12_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s12_btn.grid(row = 0, column = 2, padx = 10, pady = 5)

s22_btn = tk.Button(Parameters, text= 'S22', command = handler_s22_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s22_btn.grid(row = 0, column = 4, padx = 10, pady = 5)

s21_btn = tk.Button(Parameters, text= 'S21', command = handler_s21_plt, state = 'normal', bg="green", fg="black", font = 'Helvetica 18 bold')
s21_btn.grid(row = 0, column = 6, padx = 10, pady = 5)



#initialize the timer
hours_took = 0
scan_running = False
if DEBUG == False:
    tilt_entry_txt.set(str(round(0,3)))
    pan_entry_txt.set(str(round(0,3)))
    tp_head_resets(tp_reset_btn, tilt_entry_txt, pan_entry_txt, ser_rambo)
    mpcnc_pos_read.m114_output_static = ""
    ser_rambo.write(("M92 Z2267.72").encode() + b'\n') # Setting the Z Tower steps_per_unit

######################### end of code

window.mainloop()
