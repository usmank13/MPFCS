
"""
@brief: Functionality for GUI buttons

@author: chasewhyte
"""
import time
'''
# NOTE: not sure if this commented out code is useful. Need to check


# setting up the drop down menu for is youre using tilt and pan or not
# ArduinoVar =StringVar(Tilt_Pan)
# ArduinoVar.set("No")
# arduinoPort = False
# ArduinoOpt = OptionMenu(Tilt_Pan, ArduinoVar, "No", "Yes")
# ArduinoOpt.grid(row = 0, column = 0, padx = 20, pady = 10 )

# def clicked0():
#     if ArduinoVar == "Yes":
#         arduinoPort = True
#         arduino = serial.Serial('COM53', 9600) #Com port is subjected to changee

# ArduinoButt = Button(Tilt_Pan, text= 'SEND', command = clicked0)
# ArduinoButt.grid(row = 0, column = 1)

#this line opens arduino port
#arduino = serial.Serial('COM53', 9600) #Com port is subjected to change
'''



"""
@brief: Functionality for the tilt button. Sends messages to the user upon a click and 
sends command to the tilt motor.

@param[in] tilt_txt: tilt input box from the GUI
@param[in] tilt_confm_lbl: Confirmation label after the click
@param[in] pan_txt: pan input box from the GUI
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communication (see pyserial)
"""

def tp_head_tilt(tilt_txt, tilt_confm_lbl, pan_txt, ser_rambo):
    res1 = tilt_txt.get()
    if (res1 > 90 or res1 < -90):
        tilt_confm_lbl.configure(text = "Must be -90 to 90 degrees")
    else:
        tilt_confm_lbl.configure(text = "Sent " + res1 + " Tilt Angle")
        tilt_txt.configure(state = 'disabled')
        pan_txt.configure(state = 'normal')
        servo_input = 90-res1
        ser_rambo.write(("M280"+" P1"+" S"+str(servo_input)).encode()) # Roll serial write
        ser_rambo.write(b'\n') # Anything written to the MPCNC using pyserial.write has to be in bytes

"""
@brief: Functionality for the pan button. Sends messages to the user upon a click and 
sends command to the pan motor.

@param[in] pan_txt: pan input box from the GUI
@param[in] pan_confm_lbl: Confirmation label after the click
@param[in] reset_btn: Reset button object
@param[in] ser_rambo: serial object for issuing the command to MPCNC via serial\
    communication (see pyserial)
"""
def tp_head_pan(pan_txt,pan_confm_lbl,reset_btn, ser_rambo):
    res2 = pan_txt.get()
    if (res2 < 90 or res2 < -90):
        pan_confm_lbl.configure(text = "Must be 90 or res1 < -90")
    else:
        pan_confm_lbl.configure(text = "Sent " + res2 + " Pan Angle")
        pan_txt.configure(state = 'disabled')
        reset_btn.configure(state = 'normal')
        servo_input = 90-res2
        ser_rambo.write(("M280"+" P0"+" S"+str(servo_input)).encode()) # Yaw serial write
        ser_rambo.write(b'\n') # Anything written to the MPCNC using pyserial.write has to be in bytes

"""
@brief: Resets tilt and pan buttons

@param[in] reset_btn: reset button object
@param[in] tilt_txt: tilt input box from GUI
@param[in] ser_tp_head: serial comm object (see pyserial) for communication with the motors' controller
"""
def tp_head_resets(reset_btn, tilt_txt, ser_rambo):
    reset_btn.configure(state = 'disabled')
#     arduino.write('0'.encode())
    ser_rambo.write(("R"+str(90)).encode()) # Roll serial write to return to vertical
    ser_rambo.write(b'\n') # Anything written to the MPCNC using pyserial.write has to be in bytes
    time.sleep(2)
#     arduino.write('20'.encode())
    ser_rambo.write(("Y"+str(90)).encode()) # Roll serial write to return to vertical
    ser_rambo.write(b'\n') # Anything written to the MPCNC using pyserial.write has to be in bytes
    time.sleep(2)
    
    tilt_txt.configure(state = 'normal')
    