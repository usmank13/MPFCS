
"""
@brief: Functionality for GUI buttons

@author: chasewhyte
"""
    
"""
@brief Functionality for when the check values button is clicked. Checks if inputs
are valid and throws an error if they are not. If valid, disables the button and resets the start and reset button states. 

@param[in] submit_val: submit button
@param[in] start_btn, reset_btn: start and reset buttons
@param[in] txt00-txt11: Input boxes
"""
def submit_values(submit_val, start_btn, tp_reset_btn, mpcnc_vol_length_entry_txt, mpcnc_vol_width_entry_txt,
                  mpcnc_dwell_duration_entry_txt, mpcnc_x_step_size_entry_txt, mpcnc_y_step_size_entry_txt,
                  mpcnc_vol_height_entry_txt, vna_center_freq_entry_txt, vna_span_entry_txt, vna_sweep_pts_entry_txt,
                  mpcnc_z_step_size_entry_txt, filename_entry_txt):
    length = int(mpcnc_vol_length_entry_txt.get())
    width = int(mpcnc_vol_width_entry_txt.get())
    height = int(mpcnc_vol_height_entry_txt.get())
    xstep = int(mpcnc_x_step_size_entry_txt.get())
    ystep = int(mpcnc_y_step_size_entry_txt.get())
    zstep = int(mpcnc_z_step_size_entry_txt.get())
    min_step = 0.01
    length_valid = (length >= 0) and (length <= 610)
    width_valid = (width >= 0) and (width <= 610)
    height_valid = height >= 0 and (height <= 305)
    steps_valid = (xstep >= min_step) and (ystep >= min_step) and (zstep >= min_step)
    possible_points = [3, 11, 21, 26, 51, 101, 201, 401, 801, 1601]
    poin_valid = num_points in possible_points
    valids = [length_valid, width_valid, height_valid, steps_valid, poin_valid]
    if False in valids:
        raise Exception("One or more invalid inputs. " +
        "Please check documentation for additional guidance on acceptable inputs.")
    submit_val.configure(state = 'disabled')
#     txt00.configure(state = 'disabled')
#     txt01.configure(state = 'disabled')
#     txt02.configure(state = 'disabled')
#     txt03.configure(state = 'disabled')
#     txt04.configure(state = 'disabled')
#     txt05.configure(state = 'disabled')
#     # txt06.configure(state = 'disabled')
#     txt07.configure(state = 'disabled')
#     txt08.configure(state = 'disabled')
#     txt09.configure(state = 'disabled')
#     txt10.configure(state = 'disabled')
#     txt11.configure(state = 'disabled')
    start_btn.configure(state = 'normal')
    tp_reset_btn.configure(state = 'normal')
    
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