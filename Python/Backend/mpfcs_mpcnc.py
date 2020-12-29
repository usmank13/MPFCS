"""
@brief: Defines the command functions for the VNA and MPCNC

@author: usmank13, chasewhyte
"""

from tkinter import ttk
import tkinter as tk
import time

"""
@brief Commands the MPCNC to move to a given (x, y, z) position with G-code

@param[in] xVal: X coordinate to move the probe to
@param[in] yVal: Y coordinate to move the probe to
@param[in] zVal: Z coordinate to move the probe to
@param[in] speed: Rate of the move between the start and end point (mm/min)\
    Note: From Marlin Configuration.h DEFAULT_MAX_FEEDRATE { 120, 120, 30, 25 }
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communication (see pyserial)
"""
def mpcnc_move_xyz(x_entry_txt, y_entry_txt, z_entry_txt, speed_entry_txt, ser_rambo):
        
    ser_rambo.write(("G0"+" F" + speed_entry_txt.get() + " X" + x_entry_txt.get() +\
                     " Y" + y_entry_txt.get() + " Z" + z_entry_txt.get()).encode() + b'\n')
#     time.sleep(10)
    ser_rambo.write(("M400").encode() + b'\n') # Wait for "Movement Complete" response
    
    x_loc, y_loc, z_loc = mpcnc_pos_read(ser_rambo)
    x_entry_txt.set(x_loc)
    y_entry_txt.set(y_loc)
    z_entry_txt.set(z_loc)
    print("[X, Y, Z] = [{},{},{}]".format(x_entry_txt.get(), y_entry_txt.get(), z_entry_txt.get()))


"""
@brief Writes a pause of the specified duration in seconds to the MPCNC

@param[in] PauseDur: duration of pause in seconds
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communicatoin (see pyserial)
"""
def mpcnc_pause(PauseDur, ser_rambo):
    ser_rambo.write(("G4 " + "P" + str(int(PauseDur*10))).encode() + b'\n')
    
def mpcnc_home_xyz(home_sel, speed, x_entry_txt, y_entry_txt, z_entry_txt, ser_rambo):
    if home_sel == 'xyz':
        ser_rambo.write(("G28").encode() + b'\n')
        mpcnc_move_xyz.x_loc = float(0)
        mpcnc_move_xyz.y_loc = float(0)
        mpcnc_move_xyz.z_loc = float(0)
        x_loc, y_loc, z_loc = mpcnc_pos_read(ser_rambo)
        x_entry_txt.set(x_loc)
        y_entry_txt.set(y_loc)
        z_entry_txt.set(z_loc)
        
    elif home_sel == 'x':
        ser_rambo.write(("G28 X").encode() + b'\n')
        mpcnc_move_xyz.x_loc = float(0)
        x_loc, _, _ = mpcnc_pos_read(ser_rambo)
        x_entry_txt.set(x_loc)
        
    elif home_sel == 'y':
        ser_rambo.write(("G28 Y").encode() + b'\n')
        mpcnc_move_xyz.y_loc = float(0)
        _, y_loc, _ = mpcnc_pos_read(ser_rambo)
        y_entry_txt.set(y_loc)
    elif home_sel == 'z':
        ser_rambo.write(("G28 Z").encode() + b'\n')
        mpcnc_move_xyz.z_loc = float(0)
        _, _, z_loc = mpcnc_pos_read(ser_rambo)
        z_entry_txt.set(z_loc)
    else:
        ser_rambo.write(("G92 X0 Y0 Z0").encode() + b'\n')
    
    print("[X, Y, Z] = [{},{},{}]".format(x_entry_txt.get(), y_entry_txt.get(), z_entry_txt.get()))

        
def mpcnc_pos_read(ser_rambo):
    marlin_readline(ser_rambo) # Clearing the message buffer
    m114_output = None
    while m114_output is None: # Avoiding NoneType strings
        time.sleep(1)
        ser_rambo.write(("M114").encode() + b'\n')
        m114_output = marlin_readline(ser_rambo)

#     print("m114_output 1 = {}".format(m114_output.decode('ascii')))
    start_time = time.perf_counter()
    duration = 0
    while mpcnc_pos_read.m114_output_static == m114_output.decode('ascii') and duration < 10: # Wait to update the position until the position changes or timeouts
        time.sleep(1)
        ser_rambo.write(("M114").encode() + b'\n')
        m114_output = marlin_readline(ser_rambo)
#         print("m114_output 2 = {}".format(m114_output))
        duration = time.perf_counter()-start_time
    
    if duration >= 30:
        print("Timeout Error: Invalid Entry")        
    
#     print("m114_output 3 = {}".format(m114_output))
    mpcnc_pos_read.m114_output_static = m114_output.decode('ascii')
    m114_tokens = mpcnc_pos_read.m114_output_static.split(' ')
    
    x_loc = m114_tokens[0].split(":")[1]
    y_loc = m114_tokens[1].split(":")[1]
    z_loc = m114_tokens[2].split(":")[1]
    
    return x_loc, y_loc, z_loc
        
def marlin_readline_startup(ser_rambo):
    marlin_output = ser_rambo.readline()
    while marlin_output != ''.encode(): 
        print(marlin_output.decode('ascii'))
        marlin_output = ser_rambo.readline()
        
def marlin_readline(ser_rambo):
    marlin_output = ser_rambo.readline()
    while marlin_output != ''.encode(): 
#         print("readline={}".format(marlin_output))
        if marlin_output == 'echo:busy: processing\n'.encode():
            print('Busy Processing...')
            time.sleep(1)
        elif marlin_output.decode('ascii')[0:2] == 'X:': # Waiting for the M114 output to be read
            return marlin_output
        marlin_output = ser_rambo.readline()       
        