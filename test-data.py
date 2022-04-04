import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import pickle
import numpy as np

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

dir_path = os.path.dirname(os.path.realpath(__file__))

f1 = dir_path+'/Combined_Data_2016/data_full_full_3.pkl'

with open(f1,'rb') as f:
    df1 = pickle.load(f)

print(df1)

f2 = dir_path+'/Combined_Data_2016_Corrected/data_full_full_3.pkl'

with open(f2,'rb') as f:
    df2 = pickle.load(f)

print(df2)



f3 = dir_path+'/Combined_Data_2014/data_full_full_3.pkl'

with open(f3,'rb') as f:
    df3 = pickle.load(f)

print(df3)

f4 = dir_path+'/Combined_Data_2014_Corrected/data_full_full_3.pkl'

with open(f4,'rb') as f:
    df4 = pickle.load(f)

print(df4)


missing = [x for x in list(df2['key']) if x not in list(df1['key'])]
print(len(missing))
print(missing)

for x in missing:
    print(df2.loc[df2['key']==x,:])
