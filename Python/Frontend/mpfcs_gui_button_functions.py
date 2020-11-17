
"""
@brief: Functionality for GUI buttons

@author: chasewhyte
"""
    
"""
@brief Functionality for when the submit button is clicked. Disables the submit button, grays out
input boxes so they can no longer be edited, and resets the start and reset button states. 

@param[in] submit_val: submit button
@param[in] start_btn, reset_btn: start and reset buttons
@param[in] txt00-txt11: Input boxes
"""
def submit_values(submit_val, start_btn, reset_btn, txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11):
    submit_val.configure(state = 'disabled')
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
    reset_btn.configure(state = 'normal')
    
"""
@brief Resets the system GUI

@param[in] reset_VNA: Reset button
@param[in] submit_val: Submit Values button
@param[in] txt00-txt11: System inputs
"""
def vna_buttons_reset(reset_VNA,submit_val,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11):
    reset_VNA.configure(state = 'disabled')
    submit_val.configure(state = "normal")
    txt00.configure(state = 'normal')
    txt02.configure(state = 'normal')
    txt03.configure(state = 'normal')
    txt04.configure(state = 'normal')
    txt01.configure(state = 'normal')
    txt05.configure(state = 'normal')
    # txt06.configure(state = 'normal')
    txt07.configure(state = 'normal')
    txt08.configure(state = 'normal')
    txt09.configure(state = 'normal')
    txt10.configure(state = 'normal')
    txt11.configure(state = 'normal')