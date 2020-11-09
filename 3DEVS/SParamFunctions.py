
"""
@brief: Defines functions for graphing the S-Parameters

@author: chasewhyte
"""


# Graphs S11 with respect to 3 dimensional position
def S11Param():
	filename_input = file_txt.get()
	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection = '3d')
	x, y, z, s11, s12, s21, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
	ax1.set_title('S11')
	ax1.set_xlabel('X Position (mm)')
	ax1.set_ylabel('Y Position (mm)')
	ax1.set_zlabel('Z Position (mm)')
	p = ax1.scatter(x, y, z, c = s11, cmap = 'jet')
	colorbar = fig.colorbar(p)
	colorbar.set_label('Decibels')
	plt.show()


# Graphs S12 with respect to 3 dimensional position    
def S12Param():
	filename_input = file_txt.get()
	# s12.configure(state = 'disabled')
	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection = '3d')
	x, y, z, s11, s12, s21, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
	ax1.set_title('S12')
	ax1.set_xlabel('X Position (mm)')
	ax1.set_ylabel('Y Position (mm)')
	ax1.set_zlabel('Z Position (mm)')
	p = ax1.scatter(x, y, z, c = s12, cmap = 'jet')
	colorbar = fig.colorbar(p)
	colorbar.set_label('Decibels')
	plt.show()

# Graphs S22 with respect to 3 dimensional position
def S22Param():
	filename_input = file_txt.get()
	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection = '3d')
	x, y, z, s11, s12, s21, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
	ax1.set_title('S22')
	ax1.set_xlabel('X Position (mm)')
	ax1.set_ylabel('Y Position (mm)')
	ax1.set_zlabel('Z Position (mm)')
	p = ax1.scatter(x, y, z, c = s22, cmap = 'jet')
	colorbar = fig.colorbar(p)
	colorbar.set_label('Decibels')
	plt.show()

# Graphs S21 with respect to 3 dimensional position    
def S21Param():
	filename_input = file_txt.get()
	fig = plt.figure()
	ax1 = fig.add_subplot(111, projection = '3d')
	x, y, z, s11, s12, s21, s22 = np.loadtxt(filename_input + '.txt', delimiter = ",", unpack = True) 
	ax1.set_title('S21')
	ax1.set_xlabel('X Position (mm)')
	ax1.set_ylabel('Y Position (mm)')
	ax1.set_zlabel('Z Position (mm)')
	p = ax1.scatter(x, y, z, c = s21, cmap = 'jet')
	colorbar = fig.colorbar(p)
	colorbar.set_label('Decibels')
	plt.show()



# NOTE: I want to delete these things, but not sure if this will break something? Please
# test on the system and if it works fine with it commented out, delete these lines 	
    
# def S11Param():
# 	##### put the funtion that will generate each point here
# 	print('temporary placement action')

# def S12Param():
# 	##### put the funtion that will generate each point here
# 	print('temporary placement action')

# def S22Param():
# 	##### put the funtion that will generate each point here
# 	print('temporary placement action')
    
# def S21Param():
# 	##### put the funtion that will generate each point here
# 	print('temporary placement action')
    
