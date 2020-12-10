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
@param[in] ser_mpcnc: serial object for issuing the command to MPCNC via serial\
    communication (see pyserial)
"""
def mpcnc_move_xyz(xVal, yVal, zVal, speed, ser_mpcnc):
    ser_mpcnc.write(("G0"+" F"+str(speed) + " X"+str(xVal) + " Y"+str(yVal)\
                     + " Z"+str(zVal)).encode())
    ser_mpcnc.write(b'\n') # Anything written to the machine using visa_vna.write has to be in bytes

"""
@brief Writes a pause of the specified duration in seconds to the MPCNC

@param[in] PauseDur: duration of pause in seconds
@param[in] ser_mpcnc: serial object for issuing the command to MPCNC via serial\
    communicatoin (see pyserial)
"""
def mpcnc_pause(PauseDur, ser_mpcnc):
    ser_mpcnc.write(("G4 " + "P" + str(int(PauseDur*10))).encode())
    ser_mpcnc.write(b'\n')