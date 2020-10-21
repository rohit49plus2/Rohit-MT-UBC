import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import pickle
import numpy as np
dir_path = os.path.dirname(os.path.realpath(__file__))

data=pd.read_pickle(dir_path+'/../Combined_Data/data_full_prev_3.pkl')

data=data.drop(['Part_id','Sc_id'],axis=1)
data=data.sort_values(by=['key'])
print(data.shape)
np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', -1)

print(data.dropna(thresh=460).isnull().sum())
