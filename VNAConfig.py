#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 15:33:05 2020

@author: chasewhyte
"""
import numpy as np
import serial
import time
import random
import visa
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

def g_planarWrite(xVal, yVal, ser1):
    ser1.write(("G0 X" + str(xVal) + " Y" + str(yVal)).encode())
    ser1.write(b'\n')
        # Anything written to the machine using ser1.write has to be in bytes

def pause(PauseDur, ser1):
    ser1.write(("G4 " + "P" + str(int(PauseDur*10))).encode())
    ser1.write(b'\n')

def vna_init(num_points,vna): # add some more calibration features
    vna.query('*IDN?')
    vna.write('poin' + str(num_points))

def vna_record(num_points, sParam, vna):  # step length is passed to find the correct element
    vna.write(sParam)
    vna.write('mark1')
    vna.write('markbuck' + str(int((num_points-1) / 2))) # selects the point at the center frequency. 
        # Perhaps I should let the user select which frequency they want to check
    data = vna.query('outpmark')
    data_arr = np.fromstring(data, sep = ',')
    return data_arr[0]
