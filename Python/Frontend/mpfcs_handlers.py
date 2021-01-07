# # from ButtonFunctions import *
# # from VNAFunctions import *
# # from tkinter import *
# # from tkinter import messagebox
# # from tkinter import ttk
# 
# import matplotlib.pyplot as plt
# from MPFCS_20201113 import 3DEVS_main_mark1.3.py
#  
# 
# def handler_tp_head_tilt():
#     tp_head_tilt(tilt_txt, tilt_confm_lbl, pan_txt)
# def def handler_tp_head_pan():():
#     tp_head_pan(pan_txt,pan_confm_lbl,reset_btn)
# def handler_run_vna():
#     run_vna(reset_VNA,start_btn,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11, MPCNC)
# def Handlerresets():
#     resets(reset_btn, tilt_txt)
# def Handlersubmit_values():
#     submit_values(submit_val,start_btn,reset_btn,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11)
# def HandlerVNAreset():
#     VNAreset(reset_VNA,submit_val,txt00,txt01,txt02,txt03,txt04,txt05,txt07,txt08,txt09,txt10,txt11)
# 
# def handler_send():
#     file_txt.configure(state = 'disabled')
# 
# def handler_reset_graph():
#     file_txt.configure(state = 'normal')
#     
# def handler_s11_plt():
#     filename_input = file_txt.get()
#     fig = plt.figure()
#     ax1 = fig.add_subplot(111, projection = '3d')
#     x, y, z, s11, _, _, _ = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
#     ax1.set_title('S11')
#     ax1.set_xlabel('X Position (mm)')
#     ax1.set_ylabel('Y Position (mm)')
#     ax1.set_zlabel('Z Position (mm)')
#     p = ax1.scatter(x, y, z, c = s11, cmap = 'jet')
#     colorbar = fig.colorbar(p)
#     colorbar.set_label('Decibels')
#     plt.show()
#     
# def handler_s12_plt():
#     filename_input = file_txt.get()
#     # s12.configure(state = 'disabled')
#     fig = plt.figure()
#     ax1 = fig.add_subplot(111, projection = '3d')
#     x, y, z, _, s12, _, _ = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
#     ax1.set_title('S12')
#     ax1.set_xlabel('X Position (mm)')
#     ax1.set_ylabel('Y Position (mm)')
#     ax1.set_zlabel('Z Position (mm)')
#     p = ax1.scatter(x, y, z, c = s12, cmap = 'jet')
#     colorbar = fig.colorbar(p)
#     colorbar.set_label('Decibels')
#     plt.show()
#     
# def handler_s22_plt():
#     filename_input = file_txt.get()
#     fig = plt.figure()
#     ax1 = fig.add_subplot(111, projection = '3d')
#     x, y, z, _, _, _, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
#     ax1.set_title('S22')
#     ax1.set_xlabel('X Position (mm)')
#     ax1.set_ylabel('Y Position (mm)')
#     ax1.set_zlabel('Z Position (mm)')
#     p = ax1.scatter(x, y, z, c = s22, cmap = 'jet')
#     colorbar = fig.colorbar(p)
#     colorbar.set_label('Decibels')
#     plt.show()
#     
#     
# def handler_s21_plt():
#     filename_input = file_txt.get()
#     fig = plt.figure()
#     ax1 = fig.add_subplot(111, projection = '3d')
#     x, y, z, _, _, s21, _ = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
#     ax1.set_title('S21')
#     ax1.set_xlabel('X Position (mm)')
#     ax1.set_ylabel('Y Position (mm)')
#     ax1.set_zlabel('Z Position (mm)')
#     p = ax1.scatter(x, y, z, c = s21, cmap = 'jet')
#     colorbar = fig.colorbar(p)
#     colorbar.set_label('Decibels')
#     plt.show()