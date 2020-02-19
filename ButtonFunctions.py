#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Feb 11 15:26:04 2020

@author: chasewhyte
"""

#Button functions
#Setting up buttons
def clicked1():
	res1 = tilt_txt.get()
	if (int(res1) > 89):
		tilt_confm_lbl.configure(text = "Must be 0-89 degrees")
	else:
		tilt_confm_lbl.configure(text = "Sent " + res1 + " Tilt Angle")
		tilt_txt.configure(state = 'disabled')
		pan_txt.configure(state = 'normal')
		res1 = (str(res1).encode())
		arduino.write(res1)

def clicked2():
	res2 = pan_txt.get()
	if (int(res2) < 20 and int(res2) > 160):
		pan_confm_lbl.configure(text = "Must be 20-160 degress")
	else:
		pan_confm_lbl.configure(text = "Sent " + res2 + " Pan Angle")
		pan_txt.configure(state = 'disabled')
		reset_btn.configure(state = 'normal')
		res2 = (str(res2).encode())
		arduino.write(res2)

# Reset Button
def resets():
	reset_btn.configure(state = 'disabled')
	arduino.write('0'.encode())
	time.sleep(2)
	arduino.write('20'.encode())
	time.sleep(2)
	tilt_txt.configure(state = 'normal')
    
# setting up buttons
def submit_values():
	submit_val.configure(state = "disabled")
	txt00.configure(state = 'disabled')
	txt01.configure(state = 'disabled')
	txt02.configure(state = 'disabled')
	txt03.configure(state = 'disabled')
	txt04.configure(state = 'disabled')
	txt05.configure(state = 'disabled')
	# txt06.configure(state = 'disabled')
	txt07.configure(state = 'disabled')
	txt08.configure(state = 'disabled')
	txt09.configure(state = 'disabled')
	txt10.configure(state = 'disabled')
	txt11.configure(state = 'disabled')
	start_btn.configure(state = 'normal')
	reset_VNA.configure(state = 'normal')
