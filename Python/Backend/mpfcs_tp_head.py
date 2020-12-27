
"""
@brief: Functionality for GUI buttons

@author: chasewhyte
"""
import time
from tkinter import ttk
import tkinter as tk
import numpy as np

TILT_SERVO = "HS-53"
PAN_SERVO = "HS-5055MG-R"


"""
@brief: Functionality for the tilt button. Sends messages to the user upon a click and 
sends command to the tilt motor.

@param[in] tilt_entry_txt: tilt input box from the GUI
@param[in] tilt_confm_lbl: Confirmation label after the click
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communication (see pyserial)
    

    
"""
def tp_head_tilt(tilt_entry_txt, tilt_confm_lbl, ser_rambo):
    tilt_deg = float(tilt_entry_txt.get())
    emergency_stop_triggered = False
    _, _, rotation_max = tp_servo_specs(TILT_SERVO)
    if (tilt_deg > rotation_max-90 or tilt_deg < -90):
        tilt_confm_lbl.configure(text = "Must be between {} and -90deg".format(rotation_max-90))
    else:
        reset_btn.configure(state = 'normal')
        tilt_usec = tp_deg_2_usecs(tilt_deg, TILT_SERVO)
        print(tp_head_tilt.tilt_usec_static)
        print(tilt_usec)
        if tp_head_tilt.tilt_usec_static > tilt_usec:
            usec_steps = np.linspace(tp_head_tilt.tilt_usec_static, tilt_usec-1, 30)
        else:
            usec_steps = np.linspace(tp_head_tilt.tilt_usec_static, tilt_usec+1, 30)
        print(usec_steps)
        for step, servo_input_usec in enumerate(usec_steps):    
            if emergency_stop_triggered == False:     
                print(servo_input_usec)
                ser_rambo.write(("M280"+" P0"+" S"+str(servo_input_usec)).encode()) # tilt serial write
                ser_rambo.write(b'\n') 
                ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
                ser_rambo.write(b'\n')
                tilt_entry_txt.set(str(tp_usecs_2_deg(servo_input_usec, TILT_SERVO)))
                time.sleep(1)
            else:                
                break
        tp_head_tilt.tilt_usec_static = int(tilt_entry_txt.get())

"""
@brief: Functionality for the pan button. Sends messages to the user upon a click and 
sends command to the pan motor.

@param[in] pan_entry_txt: pan input box from the GUI
@param[in] pan_confm_lbl: Confirmation label after the click
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communication (see pyserial)


"""
def tp_head_pan(pan_entry_txt, pan_confm_lbl, ser_rambo):
    pan_deg = float(pan_entry_txt.get())
    emergency_stop_triggered = False
    _, _, rotation_max = tp_servo_specs(PAN_SERVO)
    if (pan_deg > rotation_max-90 or pan_deg < -90):
        pan_confm_lbl.configure(text = "Must be between {} and -90deg".format(rotation_max-90))
    else:
        reset_btn.configure(state = 'normal')
        pan_usec = tp_deg_2_usecs(pan_deg, PAN_SERVO)
        print(tp_head_pan.pan_usec_static)
        print(pan_usec)
        if tp_head_pan.pan_usec_static > pan_usec:
            usec_steps = np.linspace(tp_head_pan.pan_usec_static, pan_usec-1, 30)
        else:
            usec_steps = np.linspace(tp_head_pan.pan_usec_static, pan_usec+1, 30)
        print(usec_steps)
        for step, servo_input_usec in enumerate(usec_steps):    
            if emergency_stop_triggered == False:     
                print(servo_input_usec)
                ser_rambo.write(("M280"+" P0"+" S"+str(servo_input_usec)).encode()) # pan serial write
                ser_rambo.write(b'\n') 
                ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
                ser_rambo.write(b'\n')
                pan_entry_txt.set(str(tp_usecs_2_deg(servo_input_usec, PAN_SERVO)))
                time.sleep(1)
            else:                
                break
        tp_head_pan.pan_usec_static = int(pan_entry_txt.get())

"""
@brief: Resets tilt and pan buttons

@param[in] reset_btn: reset button object
@param[in] tilt_entry_txt: tilt input box from GUI
@param[in] ser_tp_head: serial comm object (see pyserial) for communication with the motors' controller
"""
def tp_head_resets(reset_btn, tilt_entry_txt, pan_entry_txt, ser_rambo):
    reset_btn.configure(state = 'disabled')
    servo_input_deg = 0
    servo_input_usec = tp_deg_2_usecs(pan_deg, TILT_SERVO)
    ser_rambo.write(("M280"+" P3"+" S"+str(servo_input_usec)).encode()) # tilt serial write
    ser_rambo.write(b'\n') 
    ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
    ser_rambo.write(b'\n')
    tilt_entry_txt.set(str(tp_usecs_2_deg(servo_input_usec)))
    tp_head_tilt.pan_usec_static = servo_input_usec
    
    servo_input_usec = tp_deg_2_usecs(pan_deg, PAN_SERVO)
    ser_rambo.write(("M280"+" P0"+" S"+str(servo_input_usec)).encode()) # Pan serial write
    ser_rambo.write(b'\n') 
    ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
    ser_rambo.write(b'\n')
    pan_entry_txt.set(str(tp_usecs_2_deg(servo_input_usec)))
    tp_head_pan.pan_usec_static = servo_input_usec

"""
Hitec HS-53 Servo Specs
    > Max PWM Signal Range = 553-2270uS
    > Travel per uS = 0.105deg/uSec
    > Max Rotation = 180deg
    > Direction of Increasing PWM Signal = CW
    > Deadband Width = 8uSec
    > Voltage Range = 4.8-6.0V
    
Hitec HS-5055MG Reprogrammed Servo Specs
    > Max PWM Signal Range = 750-2250uS
    > Travel per uS = 0.119deg/uSec (Stock: 0.084deg/uSec)
    > Max Rotation = 178deg (Stock: 126deg)
    > Direction of Increasing PWM Signal = CW
    > Deadband Width = 2uSec
    > Voltage Range = 4.8-6.0V
"""
def tp_servo_specs(servo_model):
    if servo_model == "HS-53":
        pwm_range_min = 553
        pwm_range_max = 2270
        deg_per_usec = 0.105
        rotation_max = 180
        deadband_width_usec = 8
    elif servo_model == "HS-5055MG-R":
        pwm_range_min = 553
        pwm_range_max = 2270
        deg_per_usec = 0.105
        rotation_max = 178
        deadband_width_usec = 8
    
    return pwm_range_min, deg_per_usec, rotation_max

def tp_deg_2_usecs(deg_p_m_90, servo_model):
    pwm_range_min, deg_per_usec, _ = tp_servo_specs(servo_model)
    
    deg_180 = 90 + deg_p_m_90
    
    if deg_p_m_90 == 0:
        servo_input_usec = 1
    else:
        servo_input_usec = pwm_range_min + np.around(deg_180/deg_per_usec)
        
    return servo_input_usec
        
def tp_deg_2_usecs(servo_input_usec, servo_model):
    pwm_range_min, deg_per_usec, _ = tp_servo_specs(servo_model)
    
    if servo_input_usec == 1:
        deg_180 = deg_per_usec
    else:
        deg_180 = (deg_per_usec-pwm_range_min)*deg_per_usec
    
    deg_p_m_90 = deg_180-90
    return deg_p_m_90
# def tp_home_set(ser_rambo):
    