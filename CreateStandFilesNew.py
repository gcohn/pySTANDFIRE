# if no ht in original I am assuming it's a sappling and it's 4 feet tall
# if no crown ratio given (this happens when the tree is dead) I am assuming %50
# if no ht given for a row in csv I am skiping the row
# original dataset TPA actually = TREES PER AREA, area is in hectares. Converting to trees per acre

import csv

in_csv = 'E:\Projects\STANDFIRE\FDSinpCreate\Test_Stands\M2_tree.csv'
meas_num = "M2" #Unique identifier for measurement number (M1, M2, M3, etc..,), appended to output filename
read = csv.reader(open(in_csv,'rb'))
read.next()

def check(x,type_func):
	# checks if x can be converted into type_func (type_func should be one of int(), float(), str())
	try: type_func(x)
	except ValueError:
		return False
	else: return True

cn_old = 0
c = 0

SET_CN = 0
SETTING_ID = 1
MEASUREMENT_DATE = 2
MEASUREMENT_NO = 3
COUNTY = 4
PLOT = 5
TREE_CN = 6
TAG_ID = 7
LIVE_DEAD = 8
SPECIES_SYMBOL = 9
DIAMETER = 10
TPA_EQUIV = 11
BASAL_AREA_EQUIV = 12
HEIGHT = 13
HEIGHT_METHOD = 14
CROWN_RATIO =15
CROWN_CLASS = 16
AGE = 17
AGE_METHOD = 18
RADIAL_GROWTH = 19
RADIAL_GROWTH_METHOD = 20
HEIGHT_GROWTH = 21
HEIGHT_GROWTH_METHOD = 22
SNAG_DECAY_CLASS = 23

for line in read:
	if not check(line[13],float):
		continue
	c += 1
	cn = int(line[0])
	if cn != cn_old:
		if c > 1:
			f.close()
		name = 'NewStands\PLOT%s_%s.csv' % (line[SETTING_ID],meas_num)
		print name
		cn_old = cn
		f = open(name,'wb')
		f.write('SPECIES_SYMBOL,DIAMETER,HEIGHT,CBH,LIVE_DEAD,TPA_EQUIV,MEASUREMENT_DATE,SETTING_ID,TAG_ID\n')
	
	if not check(line[15], float):
		ratio = 50.
	else: ratio = float(line[15])

	l = '%s,%s,%s,%s,%s,%s,%s,%s,%s\n' % (line[SPECIES_SYMBOL],line[DIAMETER],line[HEIGHT],\
                str((1-(ratio/100.))*float(line[HEIGHT])),line[LIVE_DEAD],\
                float(line[TPA_EQUIV])/2.471,line[MEASUREMENT_DATE],line[SETTING_ID],line[TAG_ID])
	f.write(l)
