"""
@brief: Defines the command functions for the VNA and MPCNC

@author: usmank13, chasewhyte
"""

from tkinter import ttk
import tkinter as tk

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
#     if is_step == True:
#         mpcnc_move_xyz.x_loc +=  float(x_entry_txt.get())
#         mpcnc_move_xyz.y_loc +=  float(y_entry_txt.get())
#         mpcnc_move_xyz.z_loc +=  float(z_entry_txt.get())
#     else: 
#         mpcnc_move_xyz.x_loc = float(x_entry_txt.get())
#         mpcnc_move_xyz.y_loc = float(y_entry_txt.get())
#         mpcnc_move_xyz.z_loc = float(z_entry_txt.get())
        
    ser_rambo.write(("G0"+" F" + speed_entry_txt.get() + " X" + x_entry_txt.get() +\
                     " Y" + y_entry_txt.get() + " Z" + z_entry_txt.get()).encode())
    ser_rambo.write(b'\n') 
    ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
    ser_rambo.write(b'\n')
#     mpcnc_pos_read(x_entry_txt, y_entry_txt, z_entry_txt)

"""
@brief Writes a pause of the specified duration in seconds to the MPCNC

@param[in] PauseDur: duration of pause in seconds
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communicatoin (see pyserial)
"""
def mpcnc_pause(PauseDur, ser_rambo):
    ser_rambo.write(("G4 " + "P" + str(int(PauseDur*10))).encode())
    ser_rambo.write(b'\n') 
    
def mpcnc_home_xyz(home_sel, speed, manual_x_txt, manual_y_txt, manual_z_txt, ser_rambo):
    if home_sel == 'xyz':
        ser_rambo.write(("G28").encode())
        ser_rambo.write(b'\n') 
        manual_x_txt.set(str(0))
        manual_y_txt.set(str(0))
        manual_z_txt.set(str(0))
        mpcnc_move_xyz.x_loc = float(0)
        mpcnc_move_xyz.y_loc = float(0)
        mpcnc_move_xyz.z_loc = float(0)
    elif home_sel == 'x':
        ser_rambo.write(("G28 X").encode())
        ser_rambo.write(b'\n') 
        manual_x_txt.set(str(0))
        mpcnc_move_xyz.x_loc = float(0)
    elif home_sel == 'y':
        ser_rambo.write(("G28 Y").encode())
        ser_rambo.write(b'\n') 
        manual_y_txt.set(str(0))
        mpcnc_move_xyz.y_loc = float(0)
    elif home_sel == 'z':
        ser_rambo.write(("G28 Z").encode())
        ser_rambo.write(b'\n') 
        manual_z_txt.set(str(0))
        mpcnc_move_xyz.z_loc = float(0)
    else:
        ser_rambo.write(("G92 X0 Y0 Z0").encode())
        ser_rambo.write(b'\n') 
        
def mpcnc_pos_read(x_entry_txt, y_entry_txt, z_entry_txt):
    ser_rambo.write(("M114").encode())
    ser_rambo.write(b'\n') 
    marlin_output = ser_rambo.read()
    print(marlin_output)
#     manual_x_txt.set(str(0))
#     manual_y_txt.set(str(0))
#     manual_z_txt.set(str(0))
        