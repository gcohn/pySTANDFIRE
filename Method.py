import csv,sys,re,pickle,pylab,scipy.stats,subprocess,os,time,numpy
from math import pi, ceil, floor
from Method_Helper import spp_nums
import PlaceTrees as PT

## Class For holding Trees
#
# Holds trees 'n shit
class Method():
        def __init__(self,x=None, y=None, file_name=None, method=None, TreePlaceMethod='vp'):
                # method is the process for creating and placing trees in tee_list
                # 'csv' flag to create tree list from csv docuument
                # file_name is filename and jobID of output FDS run document
                # --if 'csv' method file_name = filepath to csv document 
                #       FDS filename will taken from from filepath passed as "file_name" argument
                #       G:/somefilepath/"file_name".csv
                
                self.x = x # distance in the x direction of simulation (meters)
                self.y = y # distance in the x direction of simulation (meters)
                self.columns = 'SPP, DBH_Cm, HT_M, CBH_M, FOLLIAGE_KG, ONEHR_KG,CRWNWDT_M,LIVE_DEAD,TPA_EQUIV'
                self.TreePlaceMethod = TreePlaceMethod
                # call function to create tree_list
                
                if method == None and file_name == None:
                        print "test stand, no method specified"
                        self.file_name = "test"
                
                elif (method == 'csv') or (method == None and file_name[-3:] == 'csv'):
                        if file_name == None or file_name[-3:] != 'csv':
                                sys.exit('"csv" mode specified, required input parmam ''file_name'' not specified or incorrect (ex.  method(method=''csv'', file_name =''G:/somefilepath/PLOT32562893.csv'') must be a .csv file)')
                        else:
                                self.csv(file_name)
                elif (method == 'load') or (method == None and file_name[-3:] == 'pkl'):
                        if file_name == None or file_name[-3:] != 'pkl':
                                sys.exit('"load" mode specified, requred input param file_name not specified or incorrect (ex. method(method=''load'', file_name =''G:/somefilepath/PLOT32562893.pkl'') must be a .pk1 (pickle) file)')
                        else:
                                self.load(file_name)
                else:
                        print "no method specified"
                        
        def run(self):
                raise NotImplementedError('__call__ missing in %s' % self.__class__.__name__)
                
        def csv(self,file_name):
                # INPUT
                #       name    (str) - output name for .csv doc
                #       trees   (csv file) - columns SPP, DBH, HT, CBH, LIVE_DEAD, TPA_EQUIV
                #               SPP             (int or str) - integer species identifier or 4 letter species code 
                #                                                               (see http://plants.usda.gov/java/ or spp_nums two way dictionary below for more info)
                #               DBH                     (inches) -      Diameter at breast height
                #               HT                      (feet) - ht in feet
                #               CBH                     (feet) - Crown base height
                #               LIVE_DEAD       (L,D or 1,0) - D or 0 if dead, L or 1 if alive  
                #               TPA_EQUIV       (trees/acer)
                # OUTPUT
                #       (.csv) - name.csv file with columns SPP, DBH_CM, HT_M, CBH_M, FOLLIAGE_KG, ONEHR_KG, CRWNWDT_M, LIVE_DEAD, TPA_EQUIV
                #               - SPP                   (int) - integer species identifier (look below at spp_nums two way dictionary)
                #               - DBH_CM                (cm) - Diameter at breast height
                #               - HT_M                  (m) - height in meters 
                #               - CBH_M                 (m) - crown base height
                #               - FOLLIAGE_KG   (kg) - kg of foliage on tree output from exe
                #               - ONEHR_KG              (kg) - kg of one hours on tree output from exe
                #               - CRWNWDT_M             (m) - crown width output from exe 
                #               - LIVE_DEAD             (0 or 1) - 0 if dead 1 if alive
                #               - TPA_EQUIV             (trees/acer) - copy of input collum
                
                if self.x == None or self.y == None:
                        sys.exit("no x or y coordinates given")
                else: print "Reading csv..."
                
                def check(x,type_func):
                        # checks if x can be converted into type_func (type_func should be one of int(), float(), str())
                        try: type_func(x)
                        except ValueError:
                                return False
                        else: return True
                
                # Open a file that will hold the inputs to the biomass calculator
                b = open('fire.csv',"wb")
                print "fire.csv openend"
                tree_list = []
                # Create the fire.csv file that used as an input to the Biomass calculations
                for line in csv.reader(open(file_name,'rb')):
                        # 0 - SPP_NUM
                        # 1 - DBH
                        # 2 - Tree Height
                        # 3 - Crown Base Height
                        # 4 - FOLLIAGE_KG
                        # 5 - ONEHR_KG
                        # 6 - CRWNWDT_M   
                        # 7 - Live/Dead
                        tree_i = [None,None,None,None,None,None,None,None,None]
                        if not check(line[1],float):
                                # pass title line
                                continue
                        if check(line[0],int):
                                spp = spp_nums[int(line[0])]
                                tree_i[0] = int(line[0])
                        else:
                                spp = line[0]
                                tree_i[0] = spp_nums[line[0]]
                                
                        dbh = float(line[1])*2.54 # convert in to cm
                        tree_i[1] = dbh
                        ht = float(line[2])*.3048 # convert ft to m
                        tree_i[2] = ht
                        cbh = float(line[3])*.3048 # convert ft to m

                        tree_i[3] = cbh
                        if check(line[4],int): # LIVE_DEAD
                                tree_i[7] = int(line[4])
                        else:
                                if line[4] == 'L':
                                        tree_i[7] = 1
                                if line[4] == 'D':
                                        tree_i[7] = 0
                        tree_i[8] = float(line[5]) # TPA_EQUIV
                        tree_list.append(tree_i)
                        outline = '%s,%s,%s,%s\n' % (spp,dbh,ht,cbh)
                        
                        b.write(outline)
                b.close()

                # Estimate biomass using the external calculator
                BiomassExe = 'biomassv2_2'
                batcmd = '%s fire.csv metric metric .1 "[5000 45 -117]" r.csv' % BiomassExe
                
                print "calling biomass created by Greg Cohn..."
                print "---------------------------------------"
                os.system(batcmd)
                #os.remove('run.bat')
                #os.remove('fire.csv')

                inr = open('r.csv','r')
                inr.readline()
                inr.readline()
                inr.readline()
                #r = csv.reader(open('r.csv',"rb"),delimiter=' ')
                #r.next() # skip "['-----------TREE BIOMASS----------------']"
                #r.next() # skip "['13-Jan-2013-----metric Units---brown equations----Developed by Greg Cohn Jan 2013']"
                #r.next() # skip "['Fol', '1Hr', 'CrnWdth', 'CrnLgth', 'AvlFl', 'CBD']"
                #r = list(r) # convert iterator object into list
                #for i in range(len(r)):
                i = 0
                for line in inr:
                        lsplit = line.split("\t")
                        tree_list[i][4] = float(lsplit[0]) #float(r[i][0]) # FOLLIAGE_KG
                        tree_list[i][5] = float(lsplit[1]) #float(r[i][1]) # ONEHR_KG
                        tree_list[i][6] = float(lsplit[2]) #float(r[i][2]) # CRWNWDT_M
                        i = i + 1
                
                #os.remove('r.csv')
                r = re.compile(r'\w+') # regular expression grabs all alpha numeric characters
                self.file_name =  r.findall(file_name)[-2]
                
                print "Placing trees..."
                #print self.columns
                A = PT.PlaceTrees(self.x,self.y,tree_list)
                if self.TreePlaceMethod == 'vp':
                        self.tree_list = A.variable_poisson()
                if self.TreePlaceMethod == 'rwc':
                        self.tree_list = A.rand_with_check()
                if self.TreePlaceMethod == 'sr':
                        self.tree_list = A.simple_random()
                # create file path for pickle file
                pkl_path = file_name.rstrip('.csv')
                pkl_path += '.pkl'
                print "Writing pickle file..."
                pkl_file = open(pkl_path,'wb')
                self.tree_list.append((self.x,self.y))
                pickle.dump(self.tree_list, pkl_file)
                self.tree_list = self.tree_list[:-1]
                pkl_file.close()
                
                #for line in self.tree_list:
                #        for j in line:
                #                if j < 0:
                #                        print line
                
        def test(self,file_name):
        
                print "Reading csv..."
                reader = csv.reader(open(file_name, "rb"))
                header = reader.next()
                tree_list = list(reader)
                for i in range(len(tree_list)): 
                                for j in range(len(tree_list[i])):
                                                tree_list[i][j] = float(tree_list[i][j])

                
                print "Placing trees..."
                A = PT.PlaceTrees(self.x,self.y,tree_list)
                self.tree_list = A.variable_poisson()
                
                # create file path for pickle file
                pkl_path = file_name.rstrip('.csv')
                pkl_path += '.pkl'
                print "Writing pickle file..."
                pkl_file = open(pkl_path,'wb')
                self.tree_list.append((self.x,self.y))
                pickle.dump(self.tree_list, pkl_file)
                self.tree_list = self.tree_list[:-1]
                pkl_file.close()
        
        def load(self,file):
                # loads tree_list from pkl file created earler using a different method
                print "reading pickle file..."
                pkl_file = open(file,'rb')
                pickle_list = pickle.load(pkl_file)
                self.x = pickle_list[-1][0]
                self.y = pickle_list[-1][1]
                self.tree_list = pickle_list[:-1]
                r = re.compile(r'\w+') # regular expression grabs all alpha numeric characters
                self.file_name =  r.findall(file)[-2]
                
        def write_full_csv(self,file_path):
                # write full csv file to output file
                if list(file_path)[-1] == '\\' or list(file_path)[-1] == '/':
                        fname = file_path + self.file_name + '_FULL.csv'
                else: fname = file_path + '\\' + self.file_name + '_FULL.csv'
                
                g = open(fname)
                g.write(self.columns +'\n')
                for line in self.tree_list:
                        g.write('%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (line[0],line[1],line[2],line[3],line[4],line[5],line[6],line[7],line[8]))
                g.close()
                
        def update(self,new_list,ind = None):
                # Does one of two things:
                #       1.if "ind" specified: updates single collum of tree_list,(previously existing within the class namespace) with new_list (input param) at specified index
                #               INPUT
                #                       new_list        (list) - length(tree_list) vector to update tree_list at specified index
                #                       ind                     (integer) - specified index to update 
                #
                #       2.if "ind" == None: updates non-positional elemnts of tree list (everything but the list in the last collumn that specifies where the tree's are) with 
                #               differences in new_list and tree_list (note: new_list must be same demensions as tree_list without position collumn)
                #               INPUT
                #                       new_list        (list) - same demensions as tree_list with desired updates
                print len(new_list)
                print len(self.tree_list)
                if ( ( len(new_list) != len(self.tree_list) ) or ( ind == None and (len(new_list[1]) != len(self.tree_list[1][:-1])) ) ):
                        sys.exit("either 'ind' must specified and length of new_list must be = length of tree_list,or 'ind' == None and len(new_list[0 through n]) == len(self.tree_list[0 through n][:-1])")
                
                if ind == None:
                        new_list = map(list,zip(*new_list)) # transpose new_list
                        tree_list = map(list,zip(*self.tree_list))      # transpose self.tree_list
                        for i in range(len(new_list)):
                                if tree_list[i] != new_list[i]: self.update(new_list[i],i)
                        
                else:
                        print "updating column %s..." % ind

                        for i in range(len(self.tree_list)):
                                self.tree_list[i][ind] = new_list[i]
                                
        def plot_vertical_fuel_profile(self,file_path,test=None):
                # produces vertical fuel profile, asumes cone geometry for trees
                # if program is running in meters for example the value at 1 meter will be all the mass from 0 to 1 meter
                max_height = 0
                x = []
                if len(self.tree_list[0]) != 10: sys.exit("Requres positions to be loaded into tree list")
                length_units = 1 # 3.28084 # conversion factor from m to units desired in this case feet
                
                if test == 'test':
                        vol_check = 0
                        vol_truth = 0
                        mass_truth = 0 
                        
                for i in self.tree_list:
                        if i[3] >i[2]:
                                sys.exit("error: crown base height > height - you probably forgot to add the ratio flag") 
                        volume = (1/3.)*pi*((.5*i[6])**2)*(i[2]-i[3]) * length_units**3. # volume of foliage tree cone (length_units^3)
                        density =  i[4]/volume # Density of foliage(kg/length_units^3)
                        num_trees = len(i[9])
                        ht = length_units*i[2]  # ht in length_units
                        cbh = length_units*i[3] # crown base height in length_units 
                        cbr = i[6]*length_units * .5 # crown base radius in length_units
                        
                        #resize output list so we always have a list as long as the tallest tree in length_units
                        if ceil(ht) > max_height:
                                # we always want our list to be as long as ceil(ht) + 1 (as our list starts at 0)
                                max_height = ceil(ht)
                                for pp in range(int(ceil(ht)) - len(x) + 1):
                                        x.append(0)
                        
                        # set up radius function and begin to create the vertical fuel profile
                        #       start with the cone at the top of the tree that is not a full length_units tall
                        r = lambda h: cbr*(h/float(ht-cbh)) # calculate radius of created cone by similar triangles     
                        h = ht - floor(ht)
                        vol_old = ((1/3.) * pi * h * r(h)**2)
                        x[int(ceil(ht))] += (num_trees*density*vol_old)/float(self.x*self.y)
                        
                        if test == 'test':
                                vol_check += vol_old
                                vol_truth += (1/3.)*pi*((.5*i[6])**2)*(i[2]-i[3])
                                mass_truth += num_trees*density*volume # we should get this number but we should not get the actual truth number - due to 
                                                                                                           #    numerical precision 
                        
                        for ii in range(int(floor(ht))-1,int(ceil(cbh))-1,-1):
                                # step through every complete length_unit of each tree starting from the top.
                                # At each length_unit calcuate the volume of the cone created at that height to the top,
                                # then subtract previous volume calculated to get the volume of the cone slice at that particular length_unit.
                                
                                h = ht - ii # height of created cone
                                vol = ((1/3.) * pi * h * r(h)**2) - vol_old
                                x[ii+1] += (num_trees*density*vol)/float(self.x*self.y)
                                vol_old += vol
                                if test == 'test':
                                        vol_check += vol
                        
                        h = ht - cbh
                        vol = ((1/3.) * pi * h * r(h)**2) - vol_old
                        x[int(ceil(cbh))] += (num_trees*density*vol)/float(self.x*self.y)
                        if test == 'test':
                                vol_check += vol
                                
                def smoothList(list,degree=15):  
                        # this function from http://www.swharden.com/blog/2008-11-17-linear-data-smoothing-in-python/
                        #       full credit goes to Scott W Harden
                        smoothed=[0]*(len(list)-degree+1)
                        for i in range(len(smoothed)):  
                                smoothed[i]=sum(list[i:i+degree])/float(degree)  
                        return smoothed  


                xsmooth = smoothList(x,degree=5)
                #print max(xsmooth)
                pylab.clf()
                y = pylab.linspace(7,ceil(max_height)-7,len(x))
                ysmooth = smoothList(y,degree=5)
                pylab.plot(x,y)
                pylab.plot(xsmooth,ysmooth)
                pylab.title(self.file_name)
                pylab.xlabel('kg/m^2')
                pylab.ylabel('m')
                #pylab.xlim(0)
                if test == None:
                        if list(file_path)[-1] == '\\' or list(file_path)[-1] == '/':
                                fname = file_path + self.file_name + '_FUEL_PLOT.png'
                        else: fname = file_path + '\\' + self.file_name + '_FUEL_PLOT.png'
                        pylab.savefig(fname,format='png')
                if test == 'test':
                        print 'vol truth', vol_truth
                        print 'vol check',vol_check/ float(length_units**3)
                        print 'mass truth',mass_truth
                        print 'mass check',sum(x)
                        pylab.show()
        
        def canopy_bulk_density_rein(self):
                # Reinheart et al. (2003) Canadian Jornal of Forest Research
                # ----formula----
                #       ( 0(total stand foliage kg) + (1/2 total stand 1hr kg) )
                #               / ( (90 percentile of ht for the stand) - (50 percentile of cbh) )
                
                tree_list = pylab.array([i[:-1] + [len(i[-1])] for i in self.tree_list])
                ht_90 = scipy.stats.scoreatpercentile(tree_list[:,2],90)
                cbh_50 = scipy.stats.scoreatpercentile(tree_list[:,3],50)
                print ht_90
                print cbh_50
                afl = sum(tree_list[:,4]*tree_list[:,-1] + .5*tree_list[:,5]*tree_list[:,-1])/(self.x*self.y) # avalable fuel load
                return afl/(ht_90 - cbh_50)

        
        def plot_tree_list(self,file_path=None,test=None):
                # check if treelist exists
                try: self.tree_list
                except NameError:
                        sys.exit("tree_list must be defined before ploting tree_list")
                
                x = []
                y = []
                #dbh = []
                pylab.clf()
                pylab.axes()
                for i in self.tree_list:
                        #dbh.append(i[1])
                        r = i[6]/2. # crown radius 
                        if i[7] == 1: color = 'green'
                        if i[7] == 0: color = 'red'
                        for p in i[-1]: # positions of trees 
                                x.append(p[0])
                                y.append(p[1])
                                cir = pylab.Circle(p, radius=r, fc='none')
                                cir.set_edgecolor( color )
                                pylab.gca().add_patch(cir)
                
                pylab.figure(1)
                pylab.axis('scaled')

                pylab.scatter(x,y, marker='+',c='k')
                pylab.xlim(0,self.x)
                pylab.ylim(0,self.y)
                pylab.title(self.file_name)
                pylab.xlabel('x')
                pylab.ylabel('y')
                if test == 'test':
                        pylab.show()
                if test == None:
                        if list(file_path)[-1] == '\\' or list(file_path)[-1] == '/':
                                fname = file_path + self.file_name + '_TREE_PLOT.png'
                        else: fname = file_path + '\\' + self.file_name + '_TREE_PLOT.png'
                        pylab.savefig(fname,format='png')
                
                #pylab.figure(2)
                #pylab.hist(dbh,bins=16)
                #pylab.show()
                
                                        
if __name__ == '__main__':
        print "Testing Method.py"
