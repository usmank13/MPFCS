
"""
@brief: Functionality for GUI buttons

@author: chasewhyte
"""
import time
from tkinter import ttk, messagebox
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
def tp_head_tilt(tilt_entry_txt, ser_rambo):
    tilt_deg_cal_offset = 2.0
    tilt_deg = float(tilt_entry_txt.get())
    emergency_stop_triggered = False
    _, _, rotation_max = tp_servo_specs(TILT_SERVO)
    if (tilt_deg > rotation_max-90 or tilt_deg < -30):
        messagebox.showerror("Bounds Error", "Must be between {} and -30deg".format(rotation_max-90)) #Note: -30deg limit due to Tilt Structure being obstructed Tilt Servo
        tilt_entry_txt.set(str(tp_usecs_2_deg(tp_head_tilt.tilt_usec_static, TILT_SERVO)))
    else:
#         reset_btn.configure(state = 'normal')
        
        tilt_usec = tp_deg_2_usecs(tilt_deg+tilt_deg_cal_offset, TILT_SERVO)
        diff = abs(tp_head_tilt.tilt_usec_static-tilt_usec)
        step_divisor = 10000
        usec_steps = np.around(np.linspace(tp_head_tilt.tilt_usec_static, tilt_usec, np.around(float(diff)/step_divisor)+2))
        print(usec_steps)
        for step, servo_input_usec in enumerate(usec_steps):    
            if emergency_stop_triggered == False:
                ser_rambo.write(("M280"+" P0"+" S"+str(servo_input_usec)).encode() + b'\n') # tilt serial write
#                 ser_rambo.write(("M400").encode() + b'\n') # Wait for "Movement Complete" response
                tilt_entry_txt.set(str(tp_usecs_2_deg(servo_input_usec, TILT_SERVO)-tilt_deg_cal_offset))
                tp_head_tilt.tilt_usec_static = servo_input_usec
                time.sleep(0.5)
            else:                
                break        

"""
@brief: Functionality for the pan button. Sends messages to the user upon a click and 
sends command to the pan motor.

@param[in] pan_entry_txt: pan input box from the GUI
@param[in] pan_confm_lbl: Confirmation label after the click
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communication (see pyserial)


"""
def tp_head_pan(pan_entry_txt, ser_rambo):
    pan_deg = float(pan_entry_txt.get())
    emergency_stop_triggered = False
    _, _, rotation_max = tp_servo_specs(PAN_SERVO)
    if (pan_deg > rotation_max-90 or pan_deg < -90):
        messagebox.showerror("Bounds Error", "Must be between {} and -90deg".format(rotation_max-90))
        pan_entry_txt.set(str(tp_usecs_2_deg(tp_head_pan.pan_usec_static, PAN_SERVO)))
    else:
#         reset_btn.configure(state = 'normal')
        pan_usec = tp_deg_2_usecs(pan_deg, PAN_SERVO)
#         print("tp_head_pan.pan_usec_static={}".format(tp_head_pan.pan_usec_static))
#         print("pan_usec={}".format(pan_usec))        
        diff = abs(tp_head_pan.pan_usec_static-pan_usec)
        step_divisor = 200
        usec_steps = np.around(np.linspace(tp_head_pan.pan_usec_static, pan_usec, np.around(diff/step_divisor)+2))
        print(usec_steps)
        for step, servo_input_usec in enumerate(usec_steps):    
            if emergency_stop_triggered == False:     
                print(servo_input_usec)
                ser_rambo.write(("M280"+" P3"+" S"+str(servo_input_usec)).encode() + b'\n') # pan serial write
#                 ser_rambo.write(("M400").encode() + b'\n') # Wait for "Movement Complete" response
                pan_entry_txt.set(str(tp_usecs_2_deg(servo_input_usec, PAN_SERVO)))
                tp_head_pan.pan_usec_static = servo_input_usec
                time.sleep(0.5)
            else:                
                break
        
"""
@brief: Resets tilt and pan buttons

@param[in] reset_btn: reset button object
@param[in] tilt_entry_txt: tilt input box from GUI
@param[in] ser_tp_head: serial comm object (see pyserial) for communication with the motors' controller
"""
def tp_head_resets(reset_btn, tilt_entry_txt, pan_entry_txt, ser_rambo):
    reset_btn.configure(state = 'disabled')
    deg_p_m_90 = -90
    servo_input_usec = tp_deg_2_usecs(deg_p_m_90, PAN_SERVO)
    ser_rambo.write(("M280"+" P3"+" S"+str(servo_input_usec)).encode() + b'\n') # Pan serial write
#     ser_rambo.write(("M400").encode() + b'\n') # Wait for "Movement Complete" response
    pan_entry_txt.set(str(tp_usecs_2_deg(servo_input_usec, PAN_SERVO)))
    tp_head_pan.pan_usec_static = int(servo_input_usec)
    
    deg_p_m_90 = 0
    servo_input_usec = tp_deg_2_usecs(deg_p_m_90, TILT_SERVO)
    ser_rambo.write(("M280"+" P0"+" S"+str(servo_input_usec)).encode() + b'\n') # tilt serial write
#     ser_rambo.write(("M400").encode() + b'\n') # Wait for "Movement Complete" response
    tilt_entry_txt.set(str(tp_usecs_2_deg(servo_input_usec, TILT_SERVO)))
    tp_head_tilt.tilt_usec_static = int(servo_input_usec)
    


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
        pwm_range_min = 750
        pwm_range_max = 2250
        deg_per_usec = 0.119
        rotation_max = 178
        deadband_width_usec = 8
    
    return pwm_range_min, deg_per_usec, rotation_max

def tp_deg_2_usecs(deg_p_m_90, servo_model):
    pwm_range_min, deg_per_usec, _ = tp_servo_specs(servo_model)
    
    deg_180 = 90 + deg_p_m_90
    
#     if deg_p_m_90 == 0:
#         servo_input_usec = 1
#     else:
    servo_input_usec = pwm_range_min + np.around(deg_180/deg_per_usec)
        
    return int(servo_input_usec)
        
def tp_usecs_2_deg(servo_input_usec, servo_model):
    pwm_range_min, deg_per_usec, _ = tp_servo_specs(servo_model)
#     print(servo_input_usec)
    if servo_input_usec == 1:
        deg_p_m_90 = deg_per_usec
    else:
        deg_180 = (servo_input_usec-pwm_range_min)*deg_per_usec
        deg_p_m_90 = deg_180-90
    return float(deg_p_m_90)
# def tp_home_set(ser_rambo):
    