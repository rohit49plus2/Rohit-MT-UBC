import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import pickle
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))

datafiles_thres=['/../../Combined_Data/data_full_full_3.pkl','/../../Combined_Data/data_full_full_4.pkl','/../../Combined_Data/data_15s_full_3.pkl','/../../Combined_Data/data_15s_full_4.pkl', '/../../Combined_Data/data_full_half_3.pkl','/../../Combined_Data/data_full_half_4.pkl','/../../Combined_Data/data_15s_half_3.pkl','/../../Combined_Data/data_15s_half_4.pkl']
result_suffixes=['_full_full_3','_full_full_4','_15s_full_3','_15s_full_4', '_full_half_3','_full_half_4','_15s_half_3','_15s_half_4']
folders=['/full_full','/full_full','/15s_full','/15s_full', '/full_half','/full_half','/15s_half','/15s_half']
num=0#index for choosing data

data=pd.read_pickle(dir_path+datafiles_thres[num])
result_suffix=result_suffixes[num]
folder=folders[num]

# ep=["Frustration","Boredom"]
ep=["Curiosity","Anxiety"]

data=data.sort_values(by=['key'])
np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)
# print(data.isnull().sum())
eye_and_log=data.dropna(thresh=480)
# print(data.isnull().sum())
eye_and_log=eye_and_log.drop(['Mean # of SRL processes per relevant page while on SG1'],axis=1)
# print(eye_and_log.columns[-57:])
# print(eye_and_log.columns[:-57])

# print(eye_and_log.isnull().sum())
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from gen_classes import emotions
#
numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']

# X = X.select_dtypes(include=numerics)
# print(X)

#
# y_temp=eye_and_log[["Frustration","Boredom"]]
# y_temp=y_temp.to_numpy()
# y=[]
# for i in range(len(y_temp)):
#     if np.array_equal(y_temp[i],np.array([0,0])):
#         y.append('None')
#     elif np.array_equal(y_temp[i],np.array([1,0])):
#         y.append('Frustration')
#     elif np.array_equal(y_temp[i],np.array([0,1])):
#         y.append('Boredom')
#     elif np.array_equal(y_temp[i],np.array([1,1])):
#         y.append('Both')
#
# X['Class']=y
# X.insert(0,'Sc_id',data['Sc_id'])
# X.insert(0,'Part_id',data['Part_id'])
#
# X.fillna(0)
# X.to_csv(dir_path+'/../Combined_Data/data_full_prev_3.csv',sep=',')
