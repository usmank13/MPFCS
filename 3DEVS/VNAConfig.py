"""
@brief: Defines the command functions for the VNA and MPCNC

@author: usmank13, chasewhyte
"""
import numpy as np
import serial
import time
import random
import visa
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

"""
@brief Commands the MPCNC to move to a given planar (x, y) position with G-code

@param[in] xVal: X coordinate to move the probe to
@param[in] yVal: Y coordinate to move the probe to
@param[in] ser1: serial object for issuing the command via serial communication (see pyserial)
"""
def g_planarWrite(xVal, yVal, ser1):
    ser1.write(("G0 X" + str(xVal) + " Y" + str(yVal)).encode())
    ser1.write(b'\n') # Anything written to the machine using ser1.write has to be in bytes


"""
@brief Writes a pause of the specified duration in seconds to the MPCNC

@param[in] PauseDur: duration of pause in seconds
@param[in] ser1: serial object for issuing the command via serial communicatoin (see pyserial)
"""
def pause(PauseDur, ser1):
    ser1.write(("G4 " + "P" + str(int(PauseDur*10))).encode())
    ser1.write(b'\n')


"""
@brief Sets the Vector Network Analyzer's (VNA) measurement settings

@param[in] num_points: Number of points for the VNA measurement, usually 801 or 1601 (VNA's convention)
@param[in] vna: VNA object (see pyvisa)
@param[in] centerF: Center Frequency of scan
"""
def vna_init(num_points,vna, centerF): # add some more calibration features
    vna.query('*IDN?')
    vna.write('poin' + str(num_points))
    vna.write('CWFREQ' + str(centerF) + 'MHZ')
    # vna.query('CWFFREQ?')
    #vna.write('POWE' + str(power_level) + 'DB')
    # calibration procedures? We added extra cable 



# TODO: RETURN THE REAL AND IMAGINARY VALS
"""
@brief Measures and returns the current S-Parameter data the VNA is reading

@param[in] num_points: Number of points for the VNA measurement, usually 801 or 1601 (VNA's convention)
@param[in] sParam: the S-Parameter to measure (given as a string in the following format, e.g. 'S21')
@param[in] vna: VNA object (see pyvisa)

@param[out] data_arr: Returns the S Parameter data
"""
def vna_record(num_points, sParam, vna):  # step length is passed to find the correct element
    vna.write(sParam)
    vna.write('mark1')
    vna.write('markbuck' + str(int((num_points-1) / 2))) # selects the point at the center frequency. 
        # Perhaps I should let the user select which frequency they want to check

 
    data = vna.query('outpmark')
    data_arr = np.fromstring(data, sep = ',')
    return data_arr[0]


"""
@brief Calculates and returns the current Q value of the device under test

@param[in] num_points: Number of points for the VNA measurement, usually 801 or 1601 (VNA's convention)
@param[in] vna: VNA object (see pyvisa)
@paramin[in] span: frequency span of the measurement

@param[out] returns Q: Q value = frequency peak / bandwidth
@param[out] returns f0: the frequency at which the max value of S21 occurs
"""
def Q(num_points, vna, span):
    vna.write('S21')
    data = vna.query('outpdata')
    data_mags = np.asarray([np.real(x) for x in data])
    max_s21 = np.max(data_mags)
    indices_f0 = np.where(data_mags = max_s21)
    indexf0 = indices_f0[0] # get the first occurrence of where this happens 
    
    indices_bw_L = np.where(data_mags[:indexf0] = (max_s21 - 3)) # find 3 db freq on left of peak
    indices_bw_R = np.where(data_mags[indexf0:] = (max_s21 - 3)) # find 3 db freq on right of peak
    indexbw_L, indexbw_R = indices_bw_L[0], indices_bw_R[0] # index of first occurrence of 3 db freq on each side

    f_step = span / (num_points - 1) # frequency per point 
    f0 = f_step*indexf0 # frequency at which the max s21 value occurs
    bw = f_step*(indexbw_R - f_step*indexbw_L)

    Q = f0 / bw 
    # BWLIMVAL returns the measured bandwidth value 

    return Q, f0