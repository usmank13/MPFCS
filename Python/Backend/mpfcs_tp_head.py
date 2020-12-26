
"""
@brief: Functionality for GUI buttons

@author: chasewhyte
"""
import time
from tkinter import ttk
import tkinter as tk
import numpy as np

"""
@brief: Functionality for the tilt button. Sends messages to the user upon a click and 
sends command to the tilt motor.

@param[in] tilt_entry_txt: tilt input box from the GUI
@param[in] tilt_confm_lbl: Confirmation label after the click
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communication (see pyserial)
"""
def tp_head_tilt(tilt_entry_txt, tilt_confm_lbl, reset_btn, ser_rambo):
    tilt_deg = int(tilt_entry_txt.get())
    emergency_stop_triggered = False
    print(tilt_deg)
    if (tilt_deg > 90 or tilt_deg < -90):
        tilt_confm_lbl.configure(text = "Must be -90 to 90 degrees")
    else:
#         servo_input_deg = 90-tilt_deg
        step_size = 1
        if tp_head_tilt.tilt_deg_static > tilt_deg:
            deg_steps = range(tp_head_tilt.tilt_deg_static, tilt_deg+1, -step_size)
        else:
            deg_steps = range(tp_head_tilt.tilt_deg_static, tilt_deg+1, step_size)
        print(tp_head_tilt.tilt_deg_static)
        print(tilt_deg)
        print(step_size)
        for step, servo_input_deg in enumerate(deg_steps):    
            if emergency_stop_triggered == False:    
                print(servo_input_deg) 
                ser_rambo.write(("M280"+" P3"+" S"+str(servo_input_deg)).encode()) # pan serial write
                ser_rambo.write(b'\n') 
                ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
                ser_rambo.write(b'\n')
                tilt_entry_txt.set(str(servo_input_deg))
                time.sleep(1)
            else:                
                break
        tp_head_tilt.tilt_deg_static = int(tilt_entry_txt.get())

"""
@brief: Functionality for the pan button. Sends messages to the user upon a click and 
sends command to the pan motor.

@param[in] pan_entry_txt: pan input box from the GUI
@param[in] pan_confm_lbl: Confirmation label after the click
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communication (see pyserial)
"""
def tp_head_pan(pan_entry_txt, pan_confm_lbl, reset_btn, ser_rambo):
    pan_deg = int(pan_entry_txt.get())
    emergency_stop_triggered = False
    if (pan_deg > 90 or pan_deg < -90):
        pan_confm_lbl.configure(text = "Must be between 90 and -90deg")
    else:
        reset_btn.configure(state = 'normal')
#         servo_input_deg = 90-pan_deg
        step_size = 1
        print(tp_head_pan.pan_deg_static)
        print(pan_deg)
        print(step_size)
        if tp_head_pan.pan_deg_static > pan_deg:
            deg_steps = range(tp_head_pan.pan_deg_static, pan_deg-1, -step_size)
        else:
            deg_steps = range(tp_head_pan.pan_deg_static, pan_deg+1, step_size)
        print(deg_steps)
        for step, servo_input_deg in enumerate(deg_steps):    
            if emergency_stop_triggered == False:     
                print(servo_input_deg)
                ser_rambo.write(("M280"+" P0"+" S"+str(servo_input_deg)).encode()) # pan serial write
                ser_rambo.write(b'\n') 
                ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
                ser_rambo.write(b'\n')
                pan_entry_txt.set(str(servo_input_deg))
                time.sleep(1)
            else:                
                break
        tp_head_pan.pan_deg_static = int(pan_entry_txt.get())

"""
@brief: Resets tilt and pan buttons

@param[in] reset_btn: reset button object
@param[in] tilt_entry_txt: tilt input box from GUI
@param[in] ser_tp_head: serial comm object (see pyserial) for communication with the motors' controller
"""
def tp_head_resets(reset_btn, tilt_entry_txt, pan_entry_txt, ser_rambo):
    reset_btn.configure(state = 'disabled')
    servo_input_deg = 0
    
    ser_rambo.write(("M280"+" P0"+" S"+str(servo_input_deg)).encode()) # Pan serial write
    ser_rambo.write(b'\n') 
    ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
    ser_rambo.write(b'\n')
    pan_entry_txt.set(str(servo_input_deg))
    tp_head_pan.pan_deg_static = int(pan_entry_txt.get())
    
    ser_rambo.write(("M280"+" P3"+" S"+str(servo_input_deg)).encode()) # tilt serial write
    ser_rambo.write(b'\n') 
    ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
    ser_rambo.write(b'\n')
    tilt_entry_txt.set(str(servo_input_deg))
    tp_head_tilt.tilt_deg_static = int(tilt_entry_txt.get())
    

# def tp_home_set(ser_rambo):
    