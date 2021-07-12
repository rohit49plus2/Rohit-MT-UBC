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


t = 4 #threshold
t=str(t)
data = {'2014':0,'2016':0}
for y in ['2014','2016']:
    #Get classes
    class_file = dir_path+"/Combined_Data_"+y+"_Corrected/data_full_full_"+t+".pkl"
    data[y]=pd.read_pickle(class_file)
    data[y]=data[y].drop(['Part_id','Sc_id', 'ID','Group', 'Name','Gender','Age','Ethnicity','Education','GPA','Major','School','Courses','#Courses', 'Mean # of SRL processes per relevant page while on SG0', 'Mean # of SRL processes per relevant page while on SG1','DurationDay2InSecs','#PLAN','#DEPENDS'], axis=1)
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

drop_columns = [x for x in data['2014'].columns if x not in data['2016'].columns]

for column in drop_columns:
    del data['2014'][column]

# print(data['2014'])

# print(data['2014'].columns[0:409])


log_14=data['2014'][data['2014'].columns[-41:]]
eye_14=data['2014'][data['2014'].columns[1:409]]

log_16=data['2016'][data['2016'].columns[-41:]]
eye_16=data['2016'][data['2016'].columns[1:409]]

for c in eye_16.columns:
    if 'timeto' in c or 'keypressedrate' in c or 'leftclicrate' in c:
        eye_14=eye_14.drop(c, axis=1)
        eye_16=eye_16.drop(c, axis=1)
    elif 'rate' in c or 'velocity' in c:
        eye_16.loc[:,c]=eye_16.loc[:,c]*1000
    if 'timespent' in c or 'duration' in c or'longestfixation' in c or 'length' in c:
        eye_16.loc[:,c]=eye_16.loc[:,c]/1000

log_16 = log_16[log_16['Session duration']<10000]#remove outlier for full window
eye_16 = eye_16[eye_16['numsamples']>10000]#remove outliers for full window


log_14 = log_14.dropna(thresh=40)
eye_14 = eye_14.dropna(thresh=40)
log_16 = log_16.dropna(thresh=40)
eye_16 = eye_16.dropna(thresh=40)

# print(log_16['Note Taking Duration'])
# print(eye_16.loc[:,['key','length']])
# print(eye_14.loc[:,['key','length']]) #add extra key column to show

# print(log_16.isnull().sum())
# print(log_14.isnull().sum())
# print(eye_14.isnull().sum())
# print(eye_16.isnull().sum())

# print(eye_14.columns)
# print(eye_14['meanabspathangles'])


for c in eye_14.columns:
    if 'numfixations' in c or 'totaltimespent' in c  or 'numtransfrom' in c:
        eye_14[c]=eye_14[c]/eye_14['length']
        eye_16[c]=eye_16[c]/eye_16['length']
for c in log_14.columns:
    if 'Subgoal' in c:
        if c != '#Subgoals attempted':
            log_14[c]=log_14[c]/log_14['#Subgoals attempted']
            log_16[c]=log_16[c]/log_16['#Subgoals attempted']


eye_14['sumfixationduration']=eye_14['sumfixationduration']/eye_14['length']
eye_16['sumfixationduration']=eye_16['sumfixationduration']/eye_16['length']

eye_14['sumpathdistance']=eye_14['sumpathdistance']/eye_14['length']
eye_16['sumpathdistance']=eye_16['sumpathdistance']/eye_16['length']

eye_14['sumabspathangles']=eye_14['sumabspathangles']/eye_14['length']
eye_16['sumabspathangles']=eye_16['sumabspathangles']/eye_16['length']

eye_14['sumrelpathangles']=eye_14['sumrelpathangles']/eye_14['length']
eye_16['sumrelpathangles']=eye_16['sumrelpathangles']/eye_16['length']

eye=pd.DataFrame(columns=['Feature','2014 Mean', '2014 Std', '2016 Mean', '2016 Std','Ratio of Means'])
log=pd.DataFrame(columns=['Feature','2014 Mean', '2014 Std', '2016 Mean', '2016 Std','Ratio of Means'])


# print("log features\n\n")
for c in log_14.columns:
    log.loc[len(log)] = [c,log_14[c].mean(),log_14[c].std(),log_16[c].mean(),log_16[c].std(),max(log_14[c].mean(),log_16[c].mean())/min(log_14[c].mean(),log_16[c].mean())]
# print("eye features\n\n")
for c in eye_14.columns:
    # print(c)
    eye.loc[len(eye)] = [c,eye_14[c].mean(),eye_14[c].std(),eye_16[c].mean(),eye_16[c].std(),max(eye_14[c].mean(),eye_16[c].mean())/min(eye_14[c].mean(),eye_16[c].mean())]

print(eye.shape)
# print(eye[eye['2014 Std']==0])
eye = eye[(eye['2014 Std']!=0) & (eye['2016 Std']!=0)]
print(eye.shape)
print(log.shape)
log = log[(log['2014 Std']!=0) & (log['2016 Std']!=0)]
print(log.shape)





# print(eye[eye['Ratio of Means']>100])
import math
eye.reset_index(drop = True, inplace=True)
# print(eye)
N=3
display = log.loc[:,['Feature','Ratio of Means']]
# display = log.loc[:,:]

# display = eye.loc[25:,['Feature','Ratio of Means']]
display = eye.loc[25:,:]
# display = eye.loc[:24,:]
# print(display)
display.loc[:,display.columns!= 'Feature'] = display.loc[:,display.columns!= 'Feature'].applymap(lambda x: round(x, N - int(np.floor(math.log(abs(x),10)))))#round to N

# print(display.dtypes)
print(display.to_latex())

compare = datacompy.Compare(eye_14,eye_16,join_columns='abspathanglesrate', df1_name='2014',df2_name='2016')
# print(compare.report())


# # PRINT CO-OCCURRING PERCENTAGES
#
# emotion_percent=dict()
# relative_co_occur_percent=dict()
# absolute_co_occur_percent=dict()
# emotion_set=list(d.values())
# emotion_set.remove('Task Value')
# for emotion in emotion_set:
#     emotion_percent[emotion]= 100*df[emotion].sum()/df.shape[0]
#
# # iterator=itertools.permutations(emotion_set, 2)
# iterator=itertools.product(['Task Value'],emotion_set)
# for emotion_pair in iterator:
# 	relative_co_occur_percent[frozenset(emotion_pair)] = 100*(df[emotion_pair[0]][df[emotion_pair[1]]==1].sum())/np.array([1 for x in (df[emotion_pair[0]] + df[emotion_pair[1]]) if x>0]).sum()
# 	absolute_co_occur_percent[frozenset(emotion_pair)] = 100*(df[emotion_pair[0]][df[emotion_pair[1]]==1].sum())/df.shape[0]
#
# relative_co_occur_percent={k: v for k, v in sorted(relative_co_occur_percent.items(), key=lambda item: item[1],reverse=True)}
# absolute_co_occur_percent={k: v for k, v in sorted(absolute_co_occur_percent.items(), key=lambda item: item[1],reverse=True)}
#
#
# with open(dir_path+'/stats/emotion_percentages_'+y+'_'+t+'.pickle', 'wb') as handle:
#     pickle.dump(emotion_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)
# with open(dir_path+'/stats/relative_co_occur_percent_emotion_percentages_'+y+'_'+t+'.pickle', 'wb') as handle:
#     pickle.dump(relative_co_occur_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)
# with open(dir_path+'/stats/absolute_co_occur_percent_emotion_percentages_'+y+'_'+t+'.pickle', 'wb') as handle:
#     pickle.dump(absolute_co_occur_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)
#
# # import pprint
#
# # pprint.pprint(relative_co_occur_percent)
# # pprint.pprint(absolute_co_occur_percent)
#
# cop=pd.DataFrame()
# fe=[]
# se=[]
# rcop=[]
# acop=[]
# for pair in relative_co_occur_percent:
# 	fe.append(list(pair)[0])
# 	se.append(list(pair)[1])
# 	rcop.append(relative_co_occur_percent[pair])
# 	acop.append(absolute_co_occur_percent[pair])
# cop['Emotion 1']=fe
# cop['Emotion 2']=se
# # cop['Relative Cooccurring percent']=rcop
# cop['Cooccurring percent']=acop
# # print(emotion_percent)
# ep=pd.DataFrame()
# ep['Emotion']=emotion_percent.keys()
# ep['Percentage']=list(emotion_percent.values())
# ep=ep.sort_values(['Percentage'],ascending=False)
# ep = ep.set_index('Emotion')
# cop = cop.set_index('Emotion 1')
# print(ep.round(2).to_latex())
# print(cop.sort_values(['Cooccurring percent'],ascending = False).head(10).round(2).to_latex())
