# -*- coding: utf-8 -*-
import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import pickle
import itertools
import numpy as np
import datacompy

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

dir_path = os.path.dirname(os.path.realpath(__file__))

from gen_classes import emotions
from gen_classes2016 import emotions as emotions2016

d = {'enjoying myself':'Enjoyment', 'contempt': 'Contempt', 'confused':'Confusion', 'curious':'Curiosity', 'sad':'Sadness', 'eureka':'Eureka', 'neutral':'Neutral','task is valuable':'Task Value', 'hopeful':'Hope', 'proud':'Pride','frustrated': 'Frustration', 'anxious': 'Anxiety', 'ashamed': 'Shame', 'hopeless':'Hopelessness', 'bored': 'Boredom', 'surprised':'Surprise'}
#no happy,disgust, fear, anger


t = 3 #threshold
t=str(t)
data = {'2014':0,'2016':0}
for y in ['2014','2016']:
    #Get classes
    class_file = dir_path+"/Combined_Data_"+y+"/data_full_full_"+t+".pkl"
    data[y]=pd.read_pickle(class_file)
    data[y]=data[y].drop(['Part_id','Sc_id', 'ID','Group', 'Name','Gender','Age','Ethnicity','Education','GPA','Major','School','Courses','#Courses'], axis=1)
    data[y] = data[y].apply(pd.to_numeric, errors='ignore', downcast = 'float')
    if y=='2016':
        extras = ['endpupilsize', 'fixationsaccadetimeratio', 'longestsaccadedistance', 'longestsaccadeduration', 'maxpupilsize', 'maxpupilvelocity', 'maxsaccadespeed', 'meanpupilsize', 'meanpupilvelocity', 'meansaccadedistance', 'meansaccadeduration', 'meansaccadespeed', 'minpupilsize', 'minpupilvelocity', 'minsaccadespeed', 'numsaccades', 'startpupilsize', 'stddevpupilsize', 'stddevpupilvelocity', 'stddevsaccadedistance', 'stddevsaccadeduration', 'stddevsaccadespeed', 'sumsaccadedistance', 'sumsaccadeduration']
        data[y]=data[y].drop(extras, axis=1)
        data[y]=data[y].rename(columns=d)
    if y=='2014':
        data[y]=data[y].drop(['Happy','Anger','Fear','Disgust'],axis=1)
# print(data['2014'].columns)
# print(data['2016'].columns)
print(data['2014'].shape)
print(data['2016'].shape)
# print(data['2014'].dtypes)
# print(data['2016'].dtypes)
df = data['2016'].merge(data['2014'],how='outer')
print(df.shape)
# print(df.dtypes)

# print(df.isnull().sum())
# print(data['2014'].isnull().sum())
# print(data['2016'].isnull().sum())

log_14=data['2014'][data['2014'].columns[-46:]]
eye_14=data['2014'][data['2014'].columns[1:409]]

log_16=data['2016'][data['2016'].columns[-46:]]
eye_16=data['2016'][data['2016'].columns[1:409]]

print("log features\n\n")
for c in log_14.columns:
    print(c)
    print("2014:",log_14[c].mean(), "+- ", log_14[c].std())
    print("2016:",log_16[c].mean(), "+- ", log_16[c].std())
print("eye features\n\n")
for c in eye_14.columns:
    print(c)
    print("2014:",eye_14[c].mean(), "+- ", eye_14[c].std())
    print("2016:",eye_16[c].mean(), "+- ", eye_16[c].std())

compare = datacompy.Compare(eye_14,eye_16,join_columns='abspathanglesrate', df1_name='2014',df2_name='2016')
# print(compare.report())


emotion_percent=dict()
relative_co_occur_percent=dict()
absolute_co_occur_percent=dict()
for emotion in list(d.values()):

    emotion_percent[emotion]= 100*df[emotion].sum()/df.shape[0]
for emotion_pair in itertools.permutations(d.values(), 2):
	relative_co_occur_percent[frozenset(emotion_pair)] = 100*(df[emotion_pair[0]][df[emotion_pair[1]]==1].sum())/np.array([1 for x in (df[emotion_pair[0]] + df[emotion_pair[1]]) if x>0]).sum()
	absolute_co_occur_percent[frozenset(emotion_pair)] = 100*(df[emotion_pair[0]][df[emotion_pair[1]]==1].sum())/df.shape[0]

relative_co_occur_percent={k: v for k, v in sorted(relative_co_occur_percent.items(), key=lambda item: item[1],reverse=True)}
absolute_co_occur_percent={k: v for k, v in sorted(absolute_co_occur_percent.items(), key=lambda item: item[1],reverse=True)}


with open(dir_path+'/stats/emotion_percentages_'+y+'_'+t+'.pickle', 'wb') as handle:
    pickle.dump(emotion_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(dir_path+'/stats/relative_co_occur_percent_emotion_percentages_'+y+'_'+t+'.pickle', 'wb') as handle:
    pickle.dump(relative_co_occur_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(dir_path+'/stats/absolute_co_occur_percent_emotion_percentages_'+y+'_'+t+'.pickle', 'wb') as handle:
    pickle.dump(absolute_co_occur_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)

# import pprint

# pprint.pprint(relative_co_occur_percent)
# pprint.pprint(absolute_co_occur_percent)

import pandas as pd
cop=pd.DataFrame()
fe=[]
se=[]
rcop=[]
acop=[]
for pair in relative_co_occur_percent:
	fe.append(list(pair)[0])
	se.append(list(pair)[1])
	rcop.append(relative_co_occur_percent[pair])
	acop.append(absolute_co_occur_percent[pair])
cop['Emotion 1']=fe
cop['Emotion 2']=se
cop['Relative Cooccurring percent']=rcop
cop['Absolute Cooccurring percent']=acop
# print(emotion_percent)
ep=pd.DataFrame()
ep['Emotion']=emotion_percent.keys()
ep['Percentage']=list(emotion_percent.values())
ep=ep.sort_values(['Percentage'],ascending=False)
ep = ep.set_index('Emotion')
cop = cop.set_index('Emotion 1')
print(ep.round(2).to_latex())
print(cop.sort_values(['Absolute Cooccurring percent'],ascending = False).head(20).round(2).to_latex())
