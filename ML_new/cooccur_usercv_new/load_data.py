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

# datafiles_thres=['/../../Combined_Data/data_full_full_3.pkl','/../../Combined_Data/data_full_full_4.pkl','/../../Combined_Data/data_15s_full_3.pkl','/../../Combined_Data/data_15s_full_4.pkl', '/../../Combined_Data/data_full_half_3.pkl','/../../Combined_Data/data_full_half_4.pkl','/../../Combined_Data/data_15s_half_3.pkl','/../../Combined_Data/data_15s_half_4.pkl']

eyefiles_thres=['/../../Processed_Data/eye_3','/../../Processed_Data/eye_4']
logfiles_thres=['/../../Processed_Data/log_3','/../../Processed_Data/log_4']
combinedfiles_thres=['/../../Processed_Data/combined_3','/../../Processed_Data/combined_4']
result_suffixes=['_3','_4']
folders=['','']
num=0#index for choosing data

d = {'enjoying myself':'Enjoyment', 'contempt': 'Contempt', 'confused':'Confusion', 'curious':'Curiosity', 'sad':'Sadness', 'eureka':'Eureka', 'neutral':'Neutral','task is valuable':'Task Value', 'hopeful':'Hope', 'proud':'Pride','frustrated': 'Frustration', 'anxious': 'Anxiety', 'ashamed': 'Shame', 'hopeless':'Hopelessness', 'bored': 'Boredom', 'surprised':'Surprise'}
emotions = list(d.values())

result_suffix=result_suffixes[num]
folder=folders[num]

ep=["Frustration","Boredom"]
# ep=["Curiosity","Anxiety"]

eye=pd.read_csv(dir_path+eyefiles_thres[num]+'.csv')
log=pd.read_csv(dir_path+logfiles_thres[num]+'.csv')
combined=pd.read_csv(dir_path+combinedfiles_thres[num]+'.csv')


# print(eye.shape)
eye=eye.dropna(thresh=len(emotions),axis=0,subset=emotions)
eye=eye.dropna(thresh=eye.shape[0],axis=1)
# print(log.shape)
# print(log)
# print(log.shape)
log=log.dropna(thresh=len(emotions),axis=0,subset=emotions)
log=log.dropna(thresh=log.shape[0],axis=1)

eye_c=eye.columns
log_c = log.columns

combined_c=list(np.union1d(eye_c,log_c))
combined=combined[combined_c]
# print(combined.shape)
combined=combined.dropna(thresh=len(emotions),axis=0,subset=emotions)
combined=combined.dropna(thresh=combined.shape[1],axis=0)

# print(combined)
# print(eye.shape)
# print(log.shape)
# print(combined.shape)
# print(eye.isna().sum().sum())
# print(log.isna().sum().sum())
# print(combined.isna().sum().sum())
#
# print(len(np.unique(combined['key'])))
# print(len(np.unique(eye['key'])))
# print(len(np.unique(log['key'])))


numerics = ['int16', 'int32', 'int64', 'float16', 'float32', 'float64']
