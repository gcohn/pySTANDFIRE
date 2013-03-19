from Method import *
from Write import *
import os


# inputs can be .pkl file (pyton chach file) or .csv ( if .csv .pkl file will be created)
os.chdir("e:\projects\standfire\data")
a = Method(x=40,y=40,file_name='PLOT1.csv',TreePlaceMethod='sr')
write('green',a,'PLOT1')
