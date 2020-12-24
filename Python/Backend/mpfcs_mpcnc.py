"""
@brief: Defines the command functions for the VNA and MPCNC

@author: usmank13, chasewhyte
"""

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
def mpcnc_move_xyz(xVal, yVal, zVal, speed, ser_rambo):
    ser_rambo.write(("G0"+" F"+str(speed) + " X"+str(xVal) + " Y"+str(yVal)\
                     + " Z"+str(zVal)).encode())
    ser_rambo.write(b'\n') 
    ser_rambo.write(("M400").encode()) # Wait for "Movement Complete" response
    ser_rambo.write(b'\n')
    mpcnc_pos_read()

"""
@brief Writes a pause of the specified duration in seconds to the MPCNC

@param[in] PauseDur: duration of pause in seconds
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communicatoin (see pyserial)
"""
def mpcnc_pause(PauseDur, ser_rambo):
    ser_rambo.write(("G4 " + "P" + str(int(PauseDur*10))).encode())
    ser_rambo.write(b'\n') 
    
def mpcnc_home_xyz(home_sel, speed, ser_rambo):
    if home_sel == 'xyz':
        ser_rambo.write(("G28").encode())
        ser_rambo.write(b'\n') 
        manual_x_txt.insert(tk.END, str(0))
        manual_y_txt.insert(tk.END, str(0))
        manual_z_txt.insert(tk.END, str(0))
    elif home_sel == 'x':
        ser_rambo.write(("G28 X").encode())
        ser_rambo.write(b'\n') 
        manual_x_txt.insert(tk.END, str(0))
    elif home_sel == 'y':
        ser_rambo.write(("G28 Y").encode())
        ser_rambo.write(b'\n') 
        manual_y_txt.insert(tk.END, str(0))
    elif home_sel == 'z':
        ser_rambo.write(("G28 Z").encode())
        ser_rambo.write(b'\n') 
        manual_z_txt.insert(tk.END, str(0))
    else:
        ser_rambo.write(("G92 X0 Y0 Z0").encode())
        ser_rambo.write(b'\n') 
        
def mpcnc_pos_read():
    ser_rambo.write(("M114").encode())
    ser_rambo.write(b'\n') 
    marlin_output = ser_rambo.read()
    print(marlin_output)
        