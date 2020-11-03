# -*- coding: utf-8 -*-
import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import pickle
import itertools
import numpy as np
dir_path = os.path.dirname(os.path.realpath(__file__))

#Get classes
# MODIFIE ICI
class_file= dir_path+"/Eye_Tracking_Classes/data_2014_full_threshold3.csv"

from gen_classes import emotions

data=pd.read_csv(class_file,delimiter='\t')
emotion_percent=dict()
relative_co_occur_percent=dict()
absolute_co_occur_percent=dict()
print(data.shape[0])
for emotion in emotions:
    emotion_percent[emotion]= 100*data[emotion].sum()/data.shape[0]
for emotion_pair in itertools.permutations(emotions, 2):
	relative_co_occur_percent[frozenset(emotion_pair)] = 100*(data[emotion_pair[0]][data[emotion_pair[1]]==1].sum())/max(data[emotion_pair[0]].sum(),data[emotion_pair[1]].sum())
	absolute_co_occur_percent[frozenset(emotion_pair)] = 100*(data[emotion_pair[0]][data[emotion_pair[1]]==1].sum())/data.shape[0]

relative_co_occur_percent={k: v for k, v in sorted(relative_co_occur_percent.items(), key=lambda item: item[1],reverse=True)}
absolute_co_occur_percent={k: v for k, v in sorted(absolute_co_occur_percent.items(), key=lambda item: item[1],reverse=True)}

with open(dir_path+'/stats/emotion_percentages.pickle', 'wb') as handle:
    pickle.dump(emotion_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(dir_path+'/stats/relative_co_occur_percent_emotion_percentages.pickle', 'wb') as handle:
    pickle.dump(relative_co_occur_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(dir_path+'/stats/absolute_co_occur_percent_emotion_percentages.pickle', 'wb') as handle:
    pickle.dump(absolute_co_occur_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)

import pprint

# pprint.pprint(relative_co_occur_percent)
# pprint.pprint(absolute_co_occur_percent)

import pandas as pd
rcop=pd.DataFrame()
fe=[]
se=[]
cop=[]
for pair in relative_co_occur_percent:
	fe.append(list(pair)[0])
	se.append(list(pair)[1])
	cop.append(relative_co_occur_percent[pair])
rcop['Emotion 1']=fe
rcop['Emotion 2']=se
rcop['Coocurring percent']=cop
print(emotion_percent)
ep=pd.DataFrame()
ep['Emotion']=emotion_percent.keys()
ep['Percentage']=list(emotion_percent.values())
ep=ep.sort_values(['Percentage'],ascending=False)
print(rcop.head(30))
print(ep.head(10))
