import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
# import time

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

fix2014_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData/Fixations'
fix2016_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Eye Tracking Data/SMI Data/Fixations'

N=5
f2016 = dict()
f2014 = dict()
for file in os.listdir(fix2014_path):
    if os.path.isfile(os.path.join(fix2014_path, file)):
        id = file.split('-')[0].upper()
        with open(os.path.join(fix2014_path,id+'-Fixations.csv'),'r') as f:
            f2014[id] = pd.read_csv(f, sep=',',skiprows=0)#skip to the data
for file in os.listdir(fix2016_path):
    id = file.split('-')[0].upper()
    # print(file)
    with open(os.path.join(fix2016_path,id+'-Fixations.csv'),'r') as f:
        f2016[id] = pd.read_csv(f, sep=',',skiprows=0)#skip to the data

max2016=pd.DataFrame(columns = ['id', 'Max X', 'Max Y'])
max2014=pd.DataFrame(columns = ['id', 'Max X', 'Max Y'])
for id in f2016:
     max2016.loc[len(max2016),:]=[id,np.max(f2016[id]['fix_x']),np.max(f2016[id]['fix_y'])]
for id in f2014:
     max2014.loc[len(max2014),:]=[id,np.max(f2014[id]['fix_x']),np.max(f2014[id]['fix_y'])]

print(np.mean(max2014['Max X']))
print(np.mean(max2014['Max Y']))
# print(np.mean(max2016['Max X']))
# print(np.mean(max2016['Max Y']))
