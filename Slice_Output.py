#!c:/Python27/python.exe -u

#Program to extract slice files from fds output and save history
import subprocess, re, os, sys, csv, pickle, numpy
from pylab import imshow,show


def slice_output(file,demension,location,quantity,resolution,xyz,sim_time,dt):
	# INPUT
	#	quantity	(string) - either 'TEMPERATURE' or 'VELOCITY' - the quanity in the slice file desired
	#	demension	(string) - demension the slice is a constant value in EX
	#	location	(int) - the location of the slice in that demension
	#	resolution	(float) - how many meters per "box"
	#	file		(file path) - full file path to desired .smv document
	#	sim_time	(float) - total time of simulation - must be mulltiple of dt - ( number that comes after "&TIME T_END=" in input file to fds )
	#	dt 			(float) - time step for output ( number that comes after "DUMP DT_SLCF=" in input file to fds )

	# OUTPUT
	#	time		(pickle-list)	- pickle file of a list containing time at each measurment
	#	avgtmp		(pickle-list)	- avgerage temp across the slice at times in time
	#	slice		(pickle-list)	- the whole slice file in the demensions of original


	smv_name = file.split('\\' or '//' or '/')[-1].rstrip('.smv')
	smv_path = file.rstrip( smv_name + '.smv')
	os.chdir(smv_path) # change directory to that of .smv doc

	#----Create files----
	def mkdir(dir):
		if not os.path.exists(dir):
			os.makedirs(dir)
	
	output_file_name = demension + '_' + str(location) + '_' + quantity	
	mkdir('Slice_Output')
	mkdir('Slice_Output' + '/' + output_file_name)

	#----Get params from fds output----
	# run fds2ascii executable (using subprocess modual) and open pipe to stdin and stdout
	p = subprocess.Popen(['fds2ascii'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)

	#write input to stdin then flush buffer
	p.stdin.write('%s\n2\n1\nn\n0 0.5\n1\n1\nSlice_Output\FIRE.csv\n' % smv_name)
	p.stdin.flush()

	vars ={}

	# read info from stdout buffer and create vars and fns
	#	vars (list)	- varables of desired slices
	#	fns	 (list)	- File names for output slices
	for line in p.stdout:
		if quantity == 'TEMPERATURE':
			match = re.search(r'[0-9]+  (TEMPERATURE).*', line)
		if quantity == 'v':
			match = re.search(r'[0-9]+  ([UVW-]+VELOCITY).*', line)
		if match:
			var = int(line[0:4])
			line = p.stdout.next().split(' ') 
			
			def filter_floats(x):
				# returns True if string can be turned into float False if it can't
				try: float(x)
				except ValueError:
					return False
				else: return True
			
			def check(x):
				# Returns True if second element of x != i for all i's in vars.
				# Intended to remove duplicate slices on mesh boundaries
				for i in vars:
					if vars[i] == x:
						return False
				return True
				
			xb = map(float,filter(filter_floats,line))
			
			if demension == 'X':
				if xb[0] == xb[1] == location:
					if check(xb): 
						vars[var] = xb
			if demension == 'Y':
				if xb[2] == xb[3] == location:
					if check(xb): 
						vars[var] = xb
			if demension == 'Z':
				if xb[4] == xb[5] == location:
					if check(xb): 
						vars[var] = xb
	p.stdout.flush()
	x,y,z = numpy.array(xyz) * resolution + 1
	if demension == 'X':
		out = numpy.zeros((y,z))
	if demension == 'Y':
		out = numpy.zeros((x,z))	
	if demension == 'Z':
		out = numpy.zeros((x,y))

	#----Iterate through slices----
	if quantity == 'TEMPERATURE': Temp = True
	else: Temp = False

	time = []
	slice = []
	if Temp:
		avgtmp = []
	filename = 'Slice_Output\\fire.csv\n'
	for t in numpy.arange(0,sim_time+dt,dt):
		fdsout= []
		for i in sorted(vars):
			inpt = smv_name + '\n2\n1\nn\n' + '%g %g\n' % (t,t+dt) + '1\n' + str(i) + '\n' + filename
			p = subprocess.Popen(['fds2ascii'], shell=False, stdin=subprocess.PIPE, stdout=subprocess.PIPE)
			p.communicate(input=inpt)
			p.wait()
			
			# read csv file created by fds2ascii into list
			f = open(filename.rstrip('\n'), 'rb')
			slc = csv.reader(f)	# format of output.csv from fds2ascii is x,y,f(x,y) /n
			slc.next()	# skip first and second (non-numeric) lines in the input file 
			slc.next()
			#for row in slc:
			#	out[int(float(row[0])),int(float(row[1]))] = float(row[2])
			f.close()
		
		#imshow(out.T,origin='lower',cmap='jet',interpolation='bicubic')
		#show()
		if Temp:
			avgtmp.append( numpy.average(out) )
		slice.append(out)
		time.append(t)
		
	os.remove( filename.rstrip('\n') ) # remove the csv file created 

	#pickle me timbers
	g = lambda string: 'Slice_Output' + '\\' + output_file_name + '\\%s.pkl' % string

	output = open(g('time'), 'wb')
	pickle.dump(time, output)

	if Temp:
		output = open(g('avgtmp'), 'wb')
		pickle.dump(avgtmp, output)

	output = open(g('slice'), 'wb')
	pickle.dump(slice, output)	

	
def slices_from_metadata(file):

	a = open(file,'rb') # file iteratior object
	file_name = a.next()
	xyz = map(int, a.next().lstrip('xyz: ').split(','))
	resolution = int( a.next().lstrip('resolution: ') )
	mesh = int( a.next().lstrip('mesh: ') )
	sim_time = float( a.next().lstrip('sim time: ') )
	dt = float( a.next().lstrip('slice dt: ') )
	a.next() # pass the "slices==" line 
	file = file.rstrip('_metadata.txt') + '.smv'
	
	def read_slice(line):
		line = line.split(',')
		demension = line[0]
		location = int(line[1])
		quantity = line[2].rstrip('\n')

		slice_output(file,demension,location,quantity,resolution,xyz,sim_time,dt)
	
	for line in a:
		read_slice(line)
	
if __name__ == '__main__':	
	
	file = 'D:\\AaronStGeorge\\CreateEveryPlot\\PLOT300407754314\\PLOT300407754314_RED.smv'
	slice = ('X',5,'TEMPERATURE')
	quantity = 'TEMPERATURE'
	demension = 'Y'
	location = 20
	resolution = 1
	xyz = [40,60,35]
	sim_time = 9
	dt = .5

	slice_output(file,demension,location,quantity,resolution,xyz,sim_time,dt)
	
	#file = 'D:\AaronStGeorge\CreateEveryPlot\PLOT300407754314\PLOT300407754314_RED_metadata.txt'
	#slices_from_metadata(file)