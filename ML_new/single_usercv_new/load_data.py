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

# ep=["Frustration"]
# ep=["Boredom"]
# ep=["Curiosity"]
ep=["Anxiety"]

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

a1=(eye['Frustration']==0).sum()
b1=(eye['Frustration']==1).sum()
c1=(log['Frustration']==0).sum()
d1=(log['Frustration']==1).sum()

print(a1/(a1+b1))
print(b1/(a1+b1))
print(c1/(c1+d1))
print(d1/(c1+d1))

a2=(eye['Boredom']==0).sum()
b2=(eye['Boredom']==1).sum()
c2=(log['Boredom']==0).sum()
d2=(log['Boredom']==1).sum()

print(a2/(a2+b2))
print(b2/(a2+b2))
print(c2/(c2+d2))
print(d2/(c2+d2))

a3=(eye['Curiosity']==0).sum()
b3=(eye['Curiosity']==1).sum()
c3=(log['Curiosity']==0).sum()
d3=(log['Curiosity']==1).sum()

print(a3/(a3+b3))
print(b3/(a3+b3))
print(c3/(c3+d3))
print(d3/(c3+d3))

a4=(eye['Anxiety']==0).sum()
b4=(eye['Anxiety']==1).sum()
c4=(log['Anxiety']==0).sum()
d4=(log['Anxiety']==1).sum()

print(a4/(a4+b4))
print(b4/(a4+b4))
print(c4/(c4+d4))
print(d4/(c4+d4))

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
