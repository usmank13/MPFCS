"""
@brief: Defines the command functions for the VNA and MPCNC

@author: usmank13, chasewhyte
"""

from tkinter import ttk
import tkinter as tk
import time

BED_SIZE_X = 600
BED_SIZE_Y = 600
BED_SIZE_Z = 300

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
def mpcnc_move_xyz(x_entry_txt, y_entry_txt, z_entry_txt, speed_entry_txt, scan_running, ser_rambo):

#         if x_entry_txt.get() != "?":
#             ser_rambo.write(("G0"+" F" + speed_entry_txt.get() + " X" + x_entry_txt.get() +\
#                      " Y0 Z0").encode() + b'\n')
#         if y_entry_txt.get() != "?":
#             ser_rambo.write(("G0"+" F" + speed_entry_txt.get() + " X0" +\
#                      " Y" + y_entry_text.get() + " Z0").encode() + b'\n')
    if x_entry_txt.get() == "?" and y_entry_txt.get() == "?":
        ser_rambo.write(("G0"+" F" + str(float(speed_entry_txt.get())/4) + " X0 Y0" + " Z" + z_entry_txt.get()).encode() + b'\n')
        return
    
    x_loc_write = str(round(float(x_entry_txt.get())+ mpcnc_move_xyz.x_offset, 3))
    y_loc_write = str(round(float(y_entry_txt.get())+ mpcnc_move_xyz.y_offset, 3))
    z_loc_write = str(round(float(z_entry_txt.get())+ mpcnc_move_xyz.z_offset, 3))
    
#     print("1: x_entry, x_offset = {}, {}".format(x_entry_txt.get(), str(mpcnc_move_xyz.x_offset)))
#     print("1: y_entry, y_offset = {}, {}".format(y_entry_txt.get(), str(mpcnc_move_xyz.y_offset)))
#     print("1: z_entry, z_offset = {}, {}".format(z_entry_txt.get(), str(mpcnc_move_xyz.z_offset)))
#     
#     print("1.5: x_loc_write,x_loc {}, {}".format(x_loc_write, mpcnc_move_xyz.x_loc))
#     print("1.5: y_loc_write,y_loc {}, {}".format(y_loc_write, mpcnc_move_xyz.y_loc))
#     print("1.5: z_loc_write,z_loc {}, {}".format(z_loc_write, mpcnc_move_xyz.z_loc))
#     
#     print(mpcnc_move_xyz.x_loc == x_loc_write)
#     print(mpcnc_move_xyz.y_loc == y_loc_write)
#     print(mpcnc_move_xyz.z_loc == z_loc_write)
#     print((mpcnc_move_xyz.x_loc == x_loc_write) and (mpcnc_move_xyz.y_loc == y_loc_write) and (mpcnc_move_xyz.z_loc == z_loc_write))
    if (str(mpcnc_move_xyz.x_loc) == x_loc_write) and (str(mpcnc_move_xyz.y_loc) == y_loc_write) and (str(mpcnc_move_xyz.z_loc) == z_loc_write):
#         messagebox.showerror("Position Error", "No position change requested")
        return
#     print("1: x_entry, x_offset = {}, {}".format(x_entry_txt.get(), str(mpcnc_move_xyz.x_offset)))
#     print("1: y_entry, y_offset = {}, {}".format(y_entry_txt.get(), str(mpcnc_move_xyz.y_offset)))
#     print("1: z_entry, z_offset = {}, {}".format(z_entry_txt.get(), str(mpcnc_move_xyz.z_offset)))
    ser_rambo.write(("G0"+" F" + str(float(speed_entry_txt.get())/4) + " Z" + z_loc_write).encode() + b'\n')
    ser_rambo.write(("M400").encode() + b'\n') # Wait for "Movement Complete" response
    
    x_step = abs(mpcnc_move_xyz.x_loc-x_loc_write)
    y_step = abs(mpcnc_move_xyz.y_loc-y_loc_write)
    max_step = np.max([x_step, y_step])

    #Decreasing the Speed for small movements
    # From Configuration.h
    # * DEFAULT_MAX_FEEDRATE[X, Y, Z, E0] = { 50, 50, 15, 25 } mm/s = {3000, 3000, 900, _} mm/min
    max_xy_speed = 3000 #mm/min    
    # if x_step == y_step:
    #     speed_write =  speed_entry_txt.get()
    # else:
    #     speed_write = str(np.rint(float(speed_entry_txt.get())*max_step/float(BED_SIZE_X)))
    speed_write =  np.rint(float(speed_entry_txt.get()))
    speed_write_str = str(np.min([max_xy_speed, speed_write]))

    #Decreasing the XY acceleration for small movements
    # From Configuration.h
    #define DEFAULT_MAX_ACCELERATION      { 180, 180, 80, 180 } (mm/s^2)
    #define DEFAULT_TRAVEL_ACCELERATION   180    // X, Y, Z acceleration for travel (non printing) moves
    max_xy_travel_accel = 180
    travel_accel = np.rint(max_xy_travel_accel*max_step/float(5))
    travel_accel_str = str(np.min([max_xy_travel_accel, travel_accel]))

    ser_rambo.write(("M204"+" T" + travel_accel_str).encode() + b'\n')

    ser_rambo.write(("G0"+" F" + speed_write_str + " X" + x_loc_write +\
        " Y" + y_loc_write).encode() + b'\n')
    ser_rambo.write(("M400").encode() + b'\n') # Wait for "Movement Complete" response
   
    x_loc_read, y_loc_read, z_loc_read = mpcnc_pos_read(scan_running, ser_rambo)
    mpcnc_move_xyz.x_loc = round(x_loc_read,3)
    mpcnc_move_xyz.y_loc = round(y_loc_read,3)
    mpcnc_move_xyz.z_loc = round(z_loc_read,3)
#     print("2: x_loc, x_offset = {}, {}".format(x_loc_read, str(mpcnc_move_xyz.x_offset)))
#     print("2: y_loc, y_offset = {}, {}".format(y_loc_read, str(mpcnc_move_xyz.y_offset)))
#     print("2: z_loc, z_offset = {}, {}".format(z_loc_read, str(mpcnc_move_xyz.z_offset)))
    x_entry_txt.set(round(mpcnc_move_xyz.x_loc-mpcnc_move_xyz.x_offset,3))
    y_entry_txt.set(round(mpcnc_move_xyz.y_loc-mpcnc_move_xyz.y_offset,3))
    z_entry_txt.set(round(mpcnc_move_xyz.z_loc-mpcnc_move_xyz.z_offset,3))
    
    if scan_running == False:
        print("[X, Y, Z] = [{},{},{}]".format(x_entry_txt.get(), y_entry_txt.get(), z_entry_txt.get()))

"""
@brief Writes a pause of the specified duration in seconds to the MPCNC

@param[in] PauseDur: duration of pause in seconds
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communicatoin (see pyserial)
"""
def mpcnc_pause(PauseDur, ser_rambo):
    ser_rambo.write(("G4 " + "P" + str(int(PauseDur*10))).encode() + b'\n')
    
def mpcnc_home_xyz(home_sel, speed_entry_txt, x_entry_txt, y_entry_txt, z_entry_txt, ser_rambo):
#     if z_entry_txt.get() == '?':
#         ser_rambo.write(("G0"+" F" + speed_entry_txt.get() + " X0 Y0 Z50").encode() + b'\n')
    scan_running = False
    if home_sel == 'xyz':
        ser_rambo.write(("G28").encode() + b'\n')
        x_loc, y_loc, z_loc = mpcnc_pos_read(scan_running, ser_rambo)
        x_entry_txt.set(str(round(x_loc,3)))
        y_entry_txt.set(str(round(y_loc,3)))
        z_entry_txt.set(str(round(z_loc,3)))
        mpcnc_move_xyz.x_loc = float(x_loc)
        mpcnc_move_xyz.y_loc = float(y_loc)
        mpcnc_move_xyz.z_loc = float(z_loc) 
        mpcnc_move_xyz.x_offset = 0.0
        mpcnc_move_xyz.y_offset = 0.0
        mpcnc_move_xyz.z_offset = 0.0
        
    elif home_sel == 'x':
        ser_rambo.write(("G28 X").encode() + b'\n')
        x_loc, _, _ = mpcnc_pos_read(scan_running, ser_rambo)
        x_entry_txt.set(str(round(x_loc,3)))
        mpcnc_move_xyz.x_loc = round(x_loc,3)
        mpcnc_move_xyz.x_offset = 0.0
    elif home_sel == 'y':
        ser_rambo.write(("G28 Y").encode() + b'\n')
        _, y_loc, _ = mpcnc_pos_read(scan_running, ser_rambo)
        y_entry_txt.set(str(round(y_loc,3)))
        mpcnc_move_xyz.y_loc = round(y_loc,3)
        mpcnc_move_xyz.y_offset = 0.0
    elif home_sel == 'z':
        ser_rambo.write(("G28 Z").encode() + b'\n')
        _, _, z_loc = mpcnc_pos_read(scan_running, ser_rambo)
        z_entry_txt.set(str(round(z_loc,3)))
        mpcnc_move_xyz.z_loc = round(z_loc,3)
        mpcnc_move_xyz.z_offset = 0.0
    else:
        mpcnc_move_xyz.x_offset = round(float(x_entry_txt.get())+mpcnc_move_xyz.x_offset,3)
        mpcnc_move_xyz.y_offset = round(float(y_entry_txt.get())+mpcnc_move_xyz.y_offset,3)
        mpcnc_move_xyz.z_offset = round(float(z_entry_txt.get())+mpcnc_move_xyz.z_offset,3)
        x_entry_txt.set(str(round(0.0,3)))
        y_entry_txt.set(str(round(0.0,3)))
        z_entry_txt.set(str(round(0.0,3)))        
    
    print("[X, Y, Z] = [{},{},{}]".format(x_entry_txt.get(), y_entry_txt.get(), z_entry_txt.get()))

        
def mpcnc_pos_read(scan_running, ser_rambo):
    marlin_readline(scan_running, ser_rambo) # Clearing the message buffer
    m114_output = None
    while m114_output is None: # Avoiding NoneType strings
        time.sleep(1)
        ser_rambo.write(("M114").encode() + b'\n')
        m114_output = marlin_readline(scan_running, ser_rambo)
        
#     mpcnc_pos_read.m114_output_static = m114_output.decode('ascii')
#     print("m114_output 1 = {}".format(m114_output.decode('ascii')))
    start_time = time.perf_counter()
    duration = 0
    sleep_time = 1
    while (mpcnc_pos_read.m114_output_static == m114_output.decode('ascii')) and duration < 180: # Wait to update the position until the position changes or timeouts
        ser_rambo.write(("M114").encode() + b'\n')
        m114_output = marlin_readline(scan_running, ser_rambo)
#         print("m114_output 2 = {}".format(m114_output))
        time.sleep(sleep_time)
#         sleep_time += 1
        if m114_output is None:
            m114_output = (mpcnc_pos_read.m114_output_static).encode()
        duration = time.perf_counter()-start_time
    
    if duration >= 180:
        print("Timeout Error: Invalid Entry")        
    
#     print("m114_output 3 = {}".format(m114_output))
    mpcnc_pos_read.m114_output_static = m114_output.decode('ascii')
    m114_tokens = mpcnc_pos_read.m114_output_static.split(' ')
    
    x_loc = float(m114_tokens[0].split(":")[1])
    y_loc = float(m114_tokens[1].split(":")[1])
    z_loc = float(m114_tokens[2].split(":")[1])
    
    return x_loc, y_loc, z_loc
        
def marlin_readline_startup(ser_rambo):
    marlin_output = ser_rambo.readline()
    while marlin_output != ''.encode(): 
        print(marlin_output.decode('ascii'))
        marlin_output = ser_rambo.readline()
        
def marlin_readline(scan_running, ser_rambo):
    marlin_output = ser_rambo.readline()
    sleep_time = 1.0
    busy_processing_notified = False
    while marlin_output != ''.encode(): 
#         print("readline={}".format(marlin_output))
        if marlin_output == 'echo:busy: processing\n'.encode():
            if busy_processing_notified is False:
                busy_processing_notified = True
                if scan_running == False:
                    print('Busy Processing...')
            time.sleep(sleep_time)
#             sleep_time += 1
        elif marlin_output.decode('ascii')[0:2] == 'X:': # Waiting for the M114 output to be read
            return marlin_output
        marlin_output = ser_rambo.readline()       
        