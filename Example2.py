from Method import *
from Write import *
import os


# inputs can be .pkl file (pyton chach file) or .csv ( if .csv .pkl file will be created)
os.chdir("e:\projects\standfire\data")
x = 80
y = 80

tree_function = ['green']#['green','red','mpb_truth']

humidity = .43 # humidity of the air (mass H20/volume air+H20)
wind = 2 #[2,3,4] # wind speed from the "x" wall (m/s)
init_temp = 25 #[20,30] # initial temp of the simulation, this will be the air temp as well as initial veg temp (degrees C)

sf_moisture =  0.1 # surface fuel moisture (weight H20/weight dry)
sf_ht = .5 # [.5,.6] # surface fuel (m) 
sf_load = [.7] # surface fuel (kg/m^2)

mesh = 1 # number of meshes in simulation (see note 2 in Write.py) (int)
sim_time = 50 # time of simulation (s)
dt_part = .1 # dump simulation data every dt_part seconds (used in "&DUMP DT_PART" line)(s)
dt_slice = .5 # dump slice every dt_slice seconds (used in "&DUMP DT_SLCF" line) (s)
resolution = 0.5 # cell size (m)
weather = [humidity,wind,init_temp]
surface_fuels = [sf_moisture,sf_ht,sf_load]
simulation = [mesh,resolution,sim_time,dt_part,dt_slice]
tslice = [('y','t',10),('y','t',20),('x','t',20)]
#file_name2 = [[x,y],'E:\Projects\STANDFIRE\Data\PLOT1.csv']
print "Calling Method"
a = Method(x=x,y=y,file_name='E:\Projects\STANDFIRE\Data\PLOT300105950421_M2.csv',TreePlaceMethod='sr')
print "Calling Writer"
write('E:\Projects\STANDFIRE\Data\Sims',a,tree_function,weather,surface_fuels,simulation,tslice)
