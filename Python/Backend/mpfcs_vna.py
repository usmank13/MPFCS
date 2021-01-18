"""
@ file mpfcs_vna.py
@brief Defines functions for interfacing with the Vector Network Analyzer and recording data

@author: usmank13, chasewhyte
"""
import numpy as np

"""
@brief Sets the Vector Network Analyzer's (VNA) measurement settings

@param[in] num_points: Number of points for the VNA measurement, default = 1601 (VNA's Options = 3, 11, 21, 26, 51, 101, 201, 401, 801, 1601)
@param[in] visa_vna: VNA object (see pyvisa)
@param[in] centerF: Center Frequency of scan
"""
def vna_init(num_points, visa_vna, centerF, span): # add some more calibration features    
    visa_vna.query('*IDN?')
    visa_vna.write('poin' + str(num_points))
    visa_vna.write('CWFREQ' + str(centerF) + 'MHZ')
    f_start = round(float(centerF-span/2),2)
    f_stop = round(float(centerF+span/2),2)
#     print(f_start)
#     print(f_stop)
    # visa_vna.write('STAR' + str(float(centerF-span/2)) + 'MHZ')
    # visa_vna.write('STOP' + str(float(centerF+span/2)) + 'MHZ')
    visa_vna.write('HOLD')
    visa_vna.write('LINFREQ')
    visa_vna.write('SWET1.000000E-1S')
    visa_vna.write('STAR' + str(f_start) + 'MHZ')
    visa_vna.write('STOP' + str(f_stop) + 'MHZ')
    visa_vna.write('CONT')
    
    
#     print("Span: {}".format(visa_vna.query('SPAN?')))
#     print("CW Freq: {}".format(visa_vna.query('CWFREQ?')))
#     print("Num Points: {}".format(visa_vna.query('poin?')))
#     print("Power: {}".format(visa_vna.query('POWE?')))
    #visa_vna.write('POWE' + str(power_level) + 'DB')

# TODO: RETURN THE REAL AND IMAGINARY VALS
"""
@brief Measures and returns the current S-Parameter data the VNA is reading

@param[in] num_points: Number of points for the VNA measurement, usually 801 or 1601 (VNA's convention)
@param[in] s_param: the S-Parameter to measure (given as a string in the following format, e.g. 'S21')
@param[in] visa_vna: VNA object (see pyvisa)

@param[out] data_arr: Returns the S Parameter data
"""
def vna_record(num_points, s_param, measurement_format, visa_vna):  # step length is passed to find the correct element
    visa_vna.write(s_param +';')
    visa_vna.write(measurement_format)    
    visa_vna.write('mark1')
    visa_vna.write('markbuck' + str(int((num_points-1) / 2))) # selects the point at the center frequency. 
        # Perhaps I should let the user select which frequency they want to check 
    data = visa_vna.query('outpmark')
    data_arr = np.fromstring(data, sep = ',')
    
    
#     visa_vna.write('FORM4')
#     data2 = visa_vna.query('outpdata')
#     print("\n\n{}-----------------".format(s_param))
#     print(data_arr)
    
#     print('\nSMIMLOG')
#     visa_vna.write('SMIMLOG')    
#     visa_vna.write('mark1')
#     visa_vna.write('markbuck' + str(int((num_points-1) / 2))) # selects the point at the center frequency. 
#         # Perhaps I should let the user select which frequency they want to check 
#     data = visa_vna.query('outpmark')
#     data_arr = np.fromstring(data, sep = ',')
#     print(data_arr)
#     
#     print('\nSMIC')
#     visa_vna.write('SMIC')    
#     visa_vna.write('mark1')
#     visa_vna.write('markbuck' + str(int((num_points-1) / 2))) # selects the point at the center frequency. 
#         # Perhaps I should let the user select which frequency they want to check 
#     data = visa_vna.query('outpmark')
#     data_arr = np.fromstring(data, sep = ',')
#     print(data_arr)
    
#     print('\nSMIMRI')
#     visa_vna.write('SMIMRI')    
#     visa_vna.write('mark1')
#     visa_vna.write('markbuck' + str(int((num_points-1) / 2))) # selects the point at the center frequency. 
#         # Perhaps I should let the user select which frequency they want to check 
#     data = visa_vna.query('outpmark')
#     data_arr = np.fromstring(data, sep = ',')
#     print(data_arr)

    
#     print("Outpdata = {}".format(data2))
#     data3 = visa_vna.write('outpform')
#     print("Outpform = {}".format(data3))
# !!! ooutpforf seems to work!!!
#     data4 = visa_vna.query('outpforf')
#     print("{} - Outpforf = {}".format(s_param, data4))
    if measurement_format == 'LOGM':
        return data_arr[0]
    elif measurement_format == 'SMIMRI':
        return data_arr[0], data_arr[1]
#     return data4 # might return another val as well for the center freq


"""
@brief Calculates and returns the current Q value of the device under test

@param[in] num_points: Number of points for the VNA measurement, usually 801 or 1601 (VNA's convention)
@param[in] visa_vna: VNA object (see pyvisa)
@paramin[in] span: frequency span of the measurement

@param[out] returns Q: Q value = frequency peak / bandwidth
@param[out] returns f0: the frequency at which the max value of S21 occurs
"""
#TODO: Report S21 = 0, if no resonance 
def vna_q_calc(num_points, visa_vna, span):
    visa_vna.write('S21')
    data = visa_vna.query('outpdata')
    data_mags = np.asarray([np.real(x) for x in data])
    max_s21 = np.max(data_mags)
    indices_f0 = np.where(data_mags = max_s21)
    indexf0 = indices_f0[0] # get the first occurrence of where this happens 
    indices_bw_L = np.where(data_mags[:indexf0] == (max_s21 - 3)) # find 3 db freq on left of peak
    indices_bw_R = np.where(data_mags[indexf0:] == (max_s21 - 3)) # find 3 db freq on right of peak
    indexbw_L, indexbw_R = indices_bw_L[0], indices_bw_R[0] # index of first occurrence of 3 db freq on each side

    f_step = span / (num_points - 1) # frequency per point 
    f0 = f_step*indexf0 # frequency at which the max s21 value occurs
    bw = f_step*(indexbw_R - f_step*indexbw_L)

    Q = f0 / bw 
    # BWLIMVAL returns the measured bandwidth value 

    return Q, f0