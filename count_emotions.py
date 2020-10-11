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
class_file= dir_path+"/Eye_Tracking_Classes/data_full_threshold3.csv"

from gen_classes import emotions,emotion_qs

def emotion(emotionq):#returns the emotion label
	return emotions[emotion_qs.index(emotionq)]

data=pd.read_csv(class_file,delimiter='\t')
emotion_percent=dict()
co_occur_percent=dict()
for emotion in emotions:
    emotion_percent[emotion]= 100*data[emotion].sum()/data.shape[0]
for emotion_pair in itertools.permutations(emotions, 2):
    co_occur_percent[frozenset(emotion_pair)] = 100*(data[emotion_pair[0]][data[emotion_pair[1]]==1].sum())/max(data[emotion_pair[0]].sum(),data[emotion_pair[1]].sum())
with open(dir_path+'/stats/emotion_percentages.pickle', 'wb') as handle:
    pickle.dump(emotion_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)
with open(dir_path+'/stats/co_occur_percent_emotion_percentages.pickle', 'wb') as handle:
    pickle.dump(co_occur_percent, handle, protocol=pickle.HIGHEST_PROTOCOL)

print(co_occur_percent)
