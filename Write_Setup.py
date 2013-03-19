# writer file
from math import pi

class WriterSetup():
	# eventually make this inherit a geometry class that will chage the fule and tree definitons
	def __init__(self,tree_function,method_instance,f):
		# INPUT
		#	tree_function 	(string) - defining how input tree is created
		# 	f 				(wirte file) - output fds document to write to
		# 	method_instance (instance) - instance of method class holding tree_list
		
		# ----constructer functions----
		def _green():
			# i = index of tree in treelist
			def fuel(i,init_temp):
				return self.green_foliage(i,init_temp) 
			def  tree(i):
				return self.green_tree(i)
			self.fuel = fuel
			self.tree = tree
			
		def _red():
			# i = index of tree in treelist
			def fuel(i,init_temp):
				return self.mpb_foliage(i,init_temp) 
			def  tree(i):
				return self.mpb_tree(i)
			self.fuel = fuel
			self.tree = tree
		
		def _mpb_truth():
			# i = index of tree in treelist
			tree_list = method_instance.tree_list
			def fuel(i,init_temp):
				if tree_list[i][7] == 0:
					return self.mpb_foliage(i,init_temp)
				if tree_list[i][7] == 1:
					return self.green_foliage(i,init_temp)
			def  tree(i):
				if tree_list[i][7] == 0:
					return self.mpb_tree(i)
				if tree_list[i][7] == 1:
					return self.green_tree(i)
			self.fuel = fuel
			self.tree = tree
					
		constructors = {'green':_green,'red':_red,'mpb_truth':_mpb_truth}
		
		# runs function from constructor dictionary initiateing fuel and tree functions used in fuel_definitons and place_trees
		constructors[tree_function]()
		self.f = f
		self.tree_list = method_instance.tree_list
		
	def fuel_definitons(self,init_temp):
		for i in range(len(self.tree_list)):
			self.fuel(i,init_temp)
	
	def place_trees(self):
		for i in range(len(self.tree_list)):
			self.tree(i)
		
	def green_foliage(self,i,init_temp):
		tree_list = self.tree_list
		# i = index of tree from tree_list
		treeVolume = (1./3.)*pi*(tree_list[i][6]/2.)*tree_list[i][2]
		self.f.write('''
&PART ID='FOLIAGE_TREE_''' + str(i) + '''',TREE=.TRUE.,QUANTITIES='VEG_TEMPERATURE',
	VEG_INITIAL_TEMPERATURE=''' + str(init_temp) + ''',
	VEG_SV=4000.,VEG_MOISTURE=0.8,VEG_CHAR_FRACTION=0.25,
	VEG_DRAG_COEFFICIENT=0.375,VEG_DENSITY=520.,VEG_BULK_DENSITY=''' + str(tree_list[i][4] / treeVolume) + ''',
	VEG_BURNING_RATE_MAX=0.4,VEG_DEHYDRATION_RATE_MAX=0.4,
	VEG_REMOVE_CHARRED=.TRUE.,RGB=78,148,90 /\n''')
	
	def mpb_foliage(self, i, init_temp):
		tree_list = self.tree_list
		# i = index of tree from tree_list 
		treeVolume = (1./3.)*pi*(tree_list[i][6]/2.)*tree_list[i][2]
		self.f.write('''
&PART ID='MPB_FOLIAGE_TREE_''' + str(i) + '''',TREE=.TRUE.,QUANTITIES='VEG_TEMPERATURE',
	VEG_INITIAL_TEMPERATURE=''' + str(init_temp) + ''',
	VEG_SV=4000.,VEG_MOISTURE=0.10,VEG_CHAR_FRACTION=0.25,
	VEG_DRAG_COEFFICIENT=0.375,VEG_DENSITY=520.,VEG_BULK_DENSITY=''' + str(tree_list[i][4] / treeVolume) + ''',
	VEG_BURNING_RATE_MAX=0.4,VEG_DEHYDRATION_RATE_MAX=0.4,
	VEG_REMOVE_CHARRED=.TRUE.,RGB=237,75,21 /\n''')

	def green_tree(self,i):
		tree_list = self.tree_list
		for j in range(len(tree_list[i][-1])):
			x,y = tree_list[i][-1][j]
			self.f.write("&TREE PART_ID='FOLIAGE_TREE_" + str(i) + "',XYZ=" + str(x) + "," + str(y) +\
			",0,FUEL_GEOM='FRUSTUM',CROWN_WIDTH_BOTTOM=" + str(tree_list[i][6]) + ",CROWN_WIDTH_TOP=0.0,CROWN_BASE_HEIGHT=" +\
			str(tree_list[i][3]) + ",TREE_HEIGHT=" + str(tree_list[i][2]) + ",OUTPUT_TREE=.TRUE.,LABEL=tree" + str(i) +"_" + str(j) +  "/\n")

	def mpb_tree(self,i):
		tree_list = self.tree_list
		for j in range(len(tree_list[i][-1])):
			x,y = tree_list[i][-1][j]
			self.f.write("&TREE PART_ID='MPB_FOLIAGE_TREE_" + str(i) + "',XYZ=" + str(x) + "," + str(y) +\
			",0,FUEL_GEOM='FRUSTUM',CROWN_WIDTH_BOTTOM=" + str(tree_list[i][6]) + ",CROWN_WIDTH_TOP=0.0,CROWN_BASE_HEIGHT=" +\
			str(tree_list[i][3]) + ",TREE_HEIGHT=" + str(tree_list[i][2]) + " /\n")
