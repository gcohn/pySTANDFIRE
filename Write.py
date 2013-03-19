from Write_Setup import WriterSetup
from Method import Method
import os,sys,glob,re
        
def write(output_file_path,method_instance,tree_function,weather,surface_fuels,simulation,slices):
        # function to handle recursive file creation/calling of writer (function that actually does the writing)
        
        # INPUT
        #       all inputs not given here are the same as writer function - look at writer function documentation below
        
        
        #       tree_function           (list or string) - if given as a list file path will be recursively created and output for each element in list
        #                                                                                       for what tree_function actually is look at writer documentation
        #       surface_fuels           (list or list of lists) - if a list is given at any index of surface_fuels file path, and output will be recursively
        #                                                                                                       created for each element. For further documentation look under writer. 
        #       weather                         (list or list of lists) - if a list is given at any index of surface_fuels file path, and output will be recursively
        #                                                                                                       created for each element. For further documentation look under writer. 
        #       method_instance         (switch case) - can be instance, string, list or a list containing any combination of all three
        #                                                               (Method instance) - instance of the Method class should hold tree_list with positions
        #                                                       OR
        #                                                               (method='csv' info) - [[x,y],inputToMethod.csv] or [[x,y],path\To\Folder\Containing\Csv\Files]
        #                                                                               - [[x,y],inputToMethod.csv]                                             (list) - x,y and .csv file given - Method instance created from input 
        #                                                                       OR 
        #                                                                               - [[x,y],path\To\Folder\Containing\Csv\Files]   (list) - x,y and file path given - Method instances created from every .csv file in file path
        #                                                       OR
        #                                                               (method='load' info) - 'Path\To\Folder\Containing\Pkl\Files' or .pkl file
        #                                                                       - 'Path\To\Folder\Containing\Pkl\Files' (str) - path to folder containing .pkl files, Method instance created using load from every .pkl file in path
        #                                                                       - .pkl file                                                             (str) - Method instance created using load from .pkl file
        #                                                       OR
        #                                                               (list) - list containing any combination of the three above
        #       output_file_path        (string) -  path to desired output root file. Files will be created in that folder.
        
        
        # OUTPUT
        #       all output created by writer function
        
        # ----note----
        #       max recursion depth is 1000 by default, if you want to create more than 1000 fds input documents
        #       you will have to reset max recursion depth (may God have mercy on your soul)

        
        bat_file = open(output_file_path + '\Run.bat', "wb")
        def list_me(x):
                if type(x) == list:
                        if len(x) == 2 and (((type(x[0]) == list) or (type(x[0]) == tuple)) and (type(x[1]) == str)): 
                                return [x] # in case method_instance input is just one list of type method='csv' info
                        else: return x
                else: return [x]        
        
        method_final = []
        for i in list_me(method_instance):
                if isinstance(i,Method):
                        method_final.append(i)
                elif type(i) == str:
                        # file path to folder containing .pkl files
                        if list(i[1])[-1] == '\\' or list(i[1])[-1] == '/':
                                i = i + '*.pkl'
                        else: i = i + '\*.pkl'
                        files = glob.glob(i)    
                        for j in files:
                                method_final.append( Method(file_name=j) )
                elif type(i) == list:
                        # list [[x,y], path to .csv file] or [[x,y], path to file containing lots of .csv files]
                        if ((type(i[0]) == list) or (type(i[0]) == tuple)) and (type(i[1]) == str): 
                                r = re.compile(r'\w+') # regular expression grabs all alpha numeric characters
                                if r.findall(i[1])[-1] == 'csv': # check to see if it is a csv file
                                        method_final.append( Method(i[0][0],i[0][1],i[1]) )
                                else:
                                        if list(i[1])[-1] == '\\' or list(i[1])[-1] == '/': 
                                                i[1] += '*.csv'
                                        else: i[1] += '\*.csv'
                                        files = glob.glob(i[1])
                                        for j in files:
                                                method_final.append( Method(i[0][0],i[0][1],j) )
                else:sys.exit('inputs to write do not match formating convention')
        
        def recursion(output_file_path,method_instance,tree_function,weather,surface_fuels,simulation,slices):
                if type(method_instance) == list:
                        for i in method_instance:
                                output_file_path += ('\\' + i.file_name)
                                if not os.path.exists(output_file_path):
                                        os.makedirs(output_file_path)
                                i.plot_tree_list(output_file_path) # place plot of tree_list in output file
                                i.plot_vertical_fuel_profile(output_file_path) # place plot of vertical fuel profile in output file
                                #i.write_full_csv(output_file_path)
                                recursion(output_file_path,i,tree_function,weather,surface_fuels,simulation,slices)
                                output_file_path = output_file_path[:-len('\\' + i.file_name)]
                elif type(tree_function) == list:
                        # tree
                        for i in tree_function:
                                output_file_path += ('\\' + i.upper())
                                recursion(output_file_path,method_instance,i,weather,surface_fuels,simulation,slices)
                                output_file_path = output_file_path[:-len('\\' + i.upper())]
                elif type(weather[0]) == list:
                        # humidity
                        for i in weather[0]:
                                output_file_path += ('\Humidity_%s_na' % str(i)) # humidity is a dimensionless ratio na = not applicable
                                recursion(output_file_path,method_instance,tree_function,[i,weather[1],weather[2]],surface_fuels,simulation,slices)
                                output_file_path = output_file_path[:-len('\Humidity_%s_na' % str(i))]
                elif type(weather[1]) == list:
                        # wind
                        for i in weather[1]:
                                output_file_path += ('\Wind_%s_ms' % str(i)) # ms = m/s
                                recursion(output_file_path,method_instance,tree_function,[weather[0],i,weather[2]],surface_fuels,simulation,slices)
                                output_file_path = output_file_path[:-len('\Wind_%s_ms' % str(i))]
                elif type(weather[2]) == list:
                        #init_temp
                        for i in weather[2]:
                                output_file_path += ('\Init_temp_%s_dC' % str(i)) # dC = degrees Celsius
                                recursion(output_file_path,method_instance,tree_function,[weather[0],weather[1],i],surface_fuels,simulation,slices)
                                output_file_path = output_file_path[:-len('\Init_temp_%s_dC' % str(i))]
                elif type(surface_fuels[0]) == list:
                        #sf_moisture
                        for i in surface_fuels[0]:
                                output_file_path += ('\Sf_moisture_%s_na' % str(i)) # moisture content is a dimensionless ratio na = not applicable
                                recursion(output_file_path,method_instance,tree_function,weather,[i,surface_fuels[1],surface_fuels[2]],simulation,slices)
                                output_file_path = output_file_path[:-len('\Sf_moisture_%s_na' % str(i))]               
                elif type(surface_fuels[1]) == list:
                        #sf_ht
                        for i in surface_fuels[1]:
                                output_file_path += ('\Sf_ht_%s_m' % str(i)) # m = meters
                                recursion(output_file_path,method_instance,tree_function,weather,[surface_fuels[0],i,surface_fuels[2]],simulation,slices)
                                output_file_path = output_file_path[:-len('\Sf_ht_%s_m' % str(i))]
                elif type(surface_fuels[2]) == list:
                        #sf_load
                        for i in surface_fuels[2]:
                                output_file_path += ('\Sf_load_%s_kgM' % str(i)) #kgM = kg per meter squared 
                                recursion(output_file_path,method_instance,tree_function,weather,[surface_fuels[0],surface_fuels[1],i],simulation,slices)
                                output_file_path = output_file_path[:-len('\Sf_load_%s_kgM' % str(i))]                          
                else: 
                        bat_file.write(output_file_path + '\n')
                        writer(output_file_path,method_instance,tree_function,weather,surface_fuels,simulation,slices)
                        
        recursion(output_file_path,method_final,list_me(tree_function),weather,surface_fuels,simulation,slices)


        
def writer(output_file_path,method_instance,tree_function,weather,surface_fuels,simulation,slices):
        
        # writes .txt files for use in fds
        
        # ----Note 1----
        # each variable can be input as 
        
        # INPUT
        #       tree_function           (string) - key for "constructors" dictionary in Write_Setup.py. Defines fuel definiton and tree placement functions
        #                                                       EX: 'green' - all trees green, 'red' - all trees red, 'mpb_truth' - truth from tree_list 
        #       method_instance         (Method instance) - instance of the Method class should hold tree_list with positions                                                           
        #       output_file_path        (string) -  path to desired output file. File will be created in that folder with file name = method_instance.file_name
        #       weather                         (list) - [humidity,wind,init_temp]
        #                                                       - humidity      (mass H20/volume air+H20) - humidity of the air
        #                                                       - wind          (m/s) - wind speed from the "x" wall
        #                                                       - init_temp     (degrees C) - initial temp of the simulation, this will be the air temp as well as initial veg temp
        #       surface_fuels           (list) - [sf_moisture,sf_ht,sf_load]
        #                                                       - sf_moisture (H20/dry kg) - (fresh weight - dry weight)/dry weight
        #                                                       - sf_ht           (m) - height of surface fules
        #                                                       - sf_load         (kg/m^2) - kg per area - the standard metric.
        #       simulation                      (list) - simulation parameters - [mesh,sim_time,dt_part,dt_slice]
        #                                                       - mesh          (int) - number of meshes in simulation (see note 2)
        #                                                       - sim_time      (s) - time of simulation
        #                                                       - dt_part       (s) - dump simulation data every dt_part seconds (used in "&DUMP DT_PART" line)
        #                                                       - dt_slice      (s) - dump slice every dt_slice seconds (used in "&DUMP DT_SLCF" line)
        #       slices                          (list of tuples) - list containing tuples. Each element of list should either be(dimension,quantity,location), 
        #                                                       or (dimension ,quantity,start,stop,step); quantity = 't' for temperature or 'v' for velocity
        #                                                       EX:('x','t',1) - temperature slice in x dimension at 1m, ('z','v',1 10,1) - velocity slices in z every meter from 1 to 10.
        
        # OUTPUT
        #       metadata file           (.txt document) - contains simulation length, slice dimension/s and locations - can be input into Slice_Output.py to read out slices
        #       fds run file            (.txt document) 
        
        # ----Note 2----
        # our domain is hardcoded to have the wind blowing from the "x" wall and have mesh 
        # boundarys run along x = (1/# of meshes)*totalX, (2/# of meshes)*totalX, ..., (n/# of meshes)*totalX
        # EX: mesh = 4         Y
        #     ______________________________________
        #     |           mesh 1                    |
        #     |_____________________________________|
        #     | -> wind   mesh 2                    |
        #   X |_____________________________________|
        #     | -> wind   mesh 3                    |
        #     |_____________________________________|
        #     |           mesh 4                    |
        #     |_____________________________________|

        
        # set input arguments
        humidity,wind,init_temp = weather
        sf_moisture,sf_ht,sf_load = surface_fuels
        mesh,resolution,sim_time,dt_part,dt_slice = simulation
                
        # Check for intiger division problems creating problems in the domain
        #       this is done only in the x coordinate because this writer assumes long x slices
        if (method_instance.x/mesh)*mesh != method_instance.x:
                        sys.exit("integer division problem in meshes, (x/mesh)*mesh is not = x. Rectangular meshes are going to be created")
        
        def mkdir(dir):
                # function to make directory if it doesn't alredy exist
                if not os.path.exists(dir):
                        os.makedirs(dir)
                                
        mkdir(output_file_path) # make output folder
        f = open( output_file_path + '\\' + method_instance.file_name + '.txt' , "wb") # output file pointer
        g = open( output_file_path + '\\' + method_instance.file_name + '_metadata.txt' , "wb") # metadata file pointer
        wirter_setup = WriterSetup(tree_function,method_instance,f) # create WriterSetup instance (places trees and defines fules)

        # get dimensions 
        x = method_instance.x
        y = method_instance.y
        z = 35
        #resolution = 1
                
        # begin metadata file
        g.write( method_instance.file_name + '''
xyz: ''' + str(x) +''',''' + str(y) + ''',''' + str(z) + '''
resolution: ''' + str(resolution) + '''
mesh: ''' + str(mesh) + '''
sim time: ''' + str(sim_time) + '''
slice dt: ''' + str(dt_slice) + '''
Slices==\n''')
        # Note: NEVER EVER EVER have a space before the CHID or the TITLE, you will regret it.....
        myline = '&HEAD CHID=\'%s\', TITLE=\'%s\'/\n' % (method_instance.file_name,method_instance.file_name)
        
        f.write(myline)
        f.write(''' 
!SPATIAL AND TEMPORAL DOMAIN
!=========================
!Overall domain is ''' + str(x*resolution) + '''m x ''' + str(y*resolution) + '''m x ''' + str(z*resolution) + '''m: resolution ''' + str(resolution) + '''m
!Domain is split between ''' + str(mesh) + ''' meshes \n''')
        
        # write mesh lines
        for i in range(mesh):
                f.write('''&MESH IJK=''' + str((x/mesh)*resolution) + ''',''' + str(y*resolution) + ''',''' + str(z*resolution) + ''', XB=''' + str(i*x/mesh) + ''',''' + str((i+1)*x/mesh) + ''',0.0,''' + str(y) + ''',0.0,''' + str(z) + ''' /       \n''')
                
        f.write('''&TIME T_END=''' + str(sim_time) + ''' / sim duration in seconds 

&MISC RADIATION=.TRUE.,BAROCLINIC=.TRUE.,WIND_ONLY=.FALSE.,TMPA=''' + str(init_temp) + ''', HUMIDITY=''' + str(humidity) + '''

!Inflow Wind speed ''' + str(wind) + ''' m/s
!=========================
&SURF ID='WIND',VEL=-''' + str(wind) + ''',RAMP_V='RAMPVEL',PROFILE='ATMOSPHERIC',Z0=40,PLE=0.143 / (increasing wind vel profile)
&RAMP ID='RAMPVEL',T=0.0,F=1.0 /
&RAMP ID='RAMPVEL',T=0.5,F=1.0 /


!BOUNDARY CONDITIONS
!========================= / 
&VENT MB=XMAX, SURF_ID='OPEN' / !left wall -- wind inflow 
&VENT MB=XMIN, SURF_ID='OPEN' / !right wall -- wind inflow 
&VENT MB=YMAX, SURF_ID='OPEN' / !front wall (towards viewer)
&VENT MB=YMIN, SURF_ID='WIND' / !back wall (into screen)
&VENT MB=ZMAX, SURF_ID='OPEN' / !ceiling


!REACTION DESCRIPTION
!====================
&REAC ID='WOOD'
     FYI='Ritchie, et al., 5th IAFSS, Fuel=C_3.4 H_6.2 O_2.5'
      SOOT_YIELD = 0.02
      EDDY_DISSIPATION = .TRUE.
      O          = 2.5
      C          = 3.4
      H          = 6.2
      HEAT_OF_COMBUSTION = 17700 /
&SPEC ID='WATER VAPOR' / H2O generated from veg drying

!IGNITOR FIRE
!====================
&SURF ID='LINEFIRE',HRRPUA=500,RAMP_Q='RAMPIGN',RGB=255,0,0 /
&RAMP ID='RAMPIGN',T=0,F=0 /
&RAMP ID='RAMPIGN',T=1,F=1 /
&RAMP ID='RAMPIGN',T=32,F=1 /
&RAMP ID='RAMPIGN',T=42,F=1 /
&RAMP ID='RAMPIGN',T=43,F=0 /
&VENT XB=0,''' + str(x) + ''',0,4,0,0,SURF_ID='LINEFIRE' /

!TREE FUELS PROPERTIES
!==================================''')
 
        # write fule descriptions 
        wirter_setup.fuel_definitons(init_temp)
 
        f.write('''
&PART ID='TRUNK',TREE=.TRUE.,QUANTITIES='VEG_TEMPERATURE',
          VEG_INITIAL_TEMPERATURE=20.,
          VEG_SV=1.0,VEG_MOISTURE=1.0,VEG_CHAR_FRACTION=0.25,
          VEG_DRAG_COEFFICIENT=0.375,VEG_DENSITY=520.,VEG_BULK_DENSITY=520,
          VEG_BURNING_RATE_MAX=0.4,VEG_DEHYDRATION_RATE_MAX=0.4,
          VEG_REMOVE_CHARRED=.TRUE.,
          RGB=173,116,53 /

!UNDERSTORY FUELS PROPERTIES
!==================================''')


        sf_density = sf_load/float(sf_ht) # surface fuel (kg/m^3)

        f.write('''
&PART ID='VASC_SHRUB',TREE=.TRUE.,QUANTITIES='VEG_TEMPERATURE',
          VEG_INITIAL_TEMPERATURE=20,
          VEG_SV=8000,VEG_MOISTURE=''' + str(sf_moisture) + ''',VEG_CHAR_FRACTION=0.2,
          VEG_DRAG_COEFFICIENT=0.375,VEG_DENSITY=460,VEG_BULK_DENSITY=''' +str(sf_density)+ ''',
          VEG_BURNING_RATE_MAX=0.4,VEG_DEHYDRATION_RATE_MAX=0.4,
          VEG_REMOVE_CHARRED=.TRUE.,
          RGB=160,168,58 /
          
&PART ID='GROUND NEEDLES',TREE=.TRUE.,QUANTITIES='VEG_TEMPERATURE',
          VEG_INITIAL_TEMPERATURE=20.,
          VEG_SV=5710.,VEG_MOISTURE=0.07,VEG_CHAR_FRACTION=0.25,
          VEG_DRAG_COEFFICIENT=0.375,VEG_DENSITY=510.,VEG_BULK_DENSITY=10.,
          VEG_BURNING_RATE_MAX=0.4,VEG_DEHYDRATION_RATE_MAX=0.4,
          VEG_REMOVE_CHARRED=.TRUE. /

          



!UNDERSTORY FUELS
!====================
&TREE XB= 0,''' + str(x) + ''',0,''' + str(y) + ''',0,''' + str(sf_ht) + ''',PART_ID='VASC_SHRUB',FUEL_GEOM='RECTANGLE',OUTPUT_TREE=.TRUE.,LABEL='SURFACE_FUELS' /

!OVERSTORY FUELS
!====================\n''')
                
        # write tree list
        wirter_setup.place_trees()
        
        # write slices/metadata file
        f.write('''
        
!SLICES
!====================
&DUMP DT_PART=''' + str(dt_part) + '''/ dump simulation data every ''' + str(dt_part)  + '''seconds
&DUMP DT_SLCF=''' + str(dt_slice) + '''/ dump slice every ''' + str(dt_slice) + '''seconds
''')

        def write_slice(PB,location,quantity):
                # function to write a slice line / metadata for that slice
                # EX: slice line = " !&SLCF PBZ=2,AGL_SLICE=2,QUANTITY='VELOCITY',VECTOR=.TRUE. / "
                g.write(PB.lstrip('PB') + ''',''' + str(location) + ''',''' + quantity.lstrip('\'').rstrip('\'')  +'\n')
                if quantity == '\'TEMPERATURE\'' : vector = '''.FALSE. / '''
                if quantity == '\'VELOCITY\'': vector = '''.TRUE. / '''
                f.write('''
&SLCF ''' + PB + '''=''' + str(location) + ''',QUANTITY=''' + quantity + ''',VECTOR=''' + vector)

                                                                                                                                                                                                                                                                        #QUESTION: wtf is an AGL_SLICE?
        if slices:
                for i in slices:
                        # set slice dimension
                        PB = 'PB' + i[0].upper()
                        #set QUANTITY
                        if i[1] == ('t' or 'T' or 'temperature' or 'temp' or 'Temp' or 'Temperature' or 'TEMPERATURE'): quantity = '\'TEMPERATURE\''
                        elif i[1] == ('v' or 'V' or 'velocity' or 'Velocity' or 'VELOCITY'): quantity = '\'VELOCITY\''
                        else: print "Quanity not specified or something specified besides v or t"
                        #make slices
                        if len(i) == 3:
                                write_slice(PB,i[2],quantity) 
                        elif len(i) == 5:
                                for j in range(i[2],i[3],i[4]):
                                        write_slice(PB,j,quantity)
                        else: sys.exit('for i in slices: len(i) == 3 or 5.(dimension,quantity,location),or (dimension,quantity,start,stop,step)')
        
        # end file
        f.write('''
        
!End of file
&TAIL /
''')

        f.close()

        #print "Output file: " + output_file_path + method_instance.file_name + '.txt'


if __name__ == '__main__':
        x = 30
        y = 30
        
        tree_function = ['green']#['green','red','mpb_truth']
        
        humidity = .43 # humidity of the air (mass H20/volume air+H20)
        wind = 2 #[2,3,4] # wind speed from the "x" wall (m/s)
        init_temp = 25 #[20,30] # initial temp of the simulation, this will be the air temp as well as initial veg temp (degrees C)
        
        sf_moisture =  0.3 # surface fuel moisture (weight H20/weight dry)
        sf_ht = .5 # [.5,.6] # surface fuel (m) 
        sf_load = [7.] # surface fuel (kg/m^2)
        
        mesh = 5 # number of meshes in simulation (see note 2 in Write.py) (int)
        sim_time = 5 # time of simulation (s)
        dt_part = .1 # dump simulation data every dt_part seconds (used in "&DUMP DT_PART" line)(s)
        dt_slice = .5 # dump slice every dt_slice seconds (used in "&DUMP DT_SLCF" line) (s)
        
        weather = [humidity,wind,init_temp]
        surface_fuels = [sf_moisture,sf_ht,sf_load]
        simulation = [mesh,sim_time,dt_part,dt_slice]

        #file_name2 = [[x,y],'E:\Projects\STANDFIRE\Data\PLOT1.csv']
        #a = Method(x=50,y=50,file_name='E:\Projects\STANDFIRE\Data\PLOT1621331010602.csv',TreePlaceMethod='sr')
        a = Method(x=50,y=50,file_name='E:\Projects\STANDFIRE\Data\PLOT1.csv',TreePlaceMethod='sr')
        #print a.canopy_bulk_density_rein()
        
        write('E:\Projects\STANDFIRE\Data',a,tree_function,weather,surface_fuels,simulation,None)
