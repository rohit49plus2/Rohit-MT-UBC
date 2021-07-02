import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import pickle
import itertools
import numpy as np
import math
dir_path = os.path.dirname(os.path.realpath(__file__))
t = []

#Get classes
# MODIFIE ICI
EV_file= dir_path+"/EmotionReportData2014.csv"
data=pd.read_csv(EV_file,delimiter=';')
# print(data.columns)
currentid=-1
sc_ids=[]
eiv_counts=[]
def isnan(string):
    return string != string
for index in range(data.shape[0]):
    if currentid == -1 or (int(data['Participant ID'][index][-3:]) != currentid and currentid > -1): #new student in logs
        currentid = int(data['Participant ID'][index][-3:])
        EIV_count = 1
    if isnan(data["DateSession"][index]) or isnan(data["Absolute time"][index]):
        sc_ids.append("NA")
    else:
        EIVtime = int(calendar.timegm(datetime.datetime.strptime(data["DateSession"][index]+" "+data["Absolute time"][index], "%m/%d/%Y %H:%M:%S").timetuple()) * 1000000 )
        sc_ids.append("EIVreport_"+str(EIV_count)+"_"+str(EIVtime))
    eiv_counts.append(EIV_count)
    EIV_count+=1
data["sc_id"]=sc_ids
data["eiv_count"]=eiv_counts
ids_with_eiv_number=dict()#dictionary of which subjects have at least (key) EIVs
for i in {1,2,3,4,5,6,7,8}:
    ids_with_eiv_number[i]=[]
for index in range(data.shape[0]):
    ids_with_eiv_number[data['eiv_count'][index]].append(data['Participant ID'][index])


data=data.dropna().reset_index(drop=True)
def half_time(t1,t2):
    sec1=secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(t1.split(':'))))
    sec2=secs = sum(int(x) * 60 ** i for i, x in enumerate(reversed(t2.split(':'))))
    return(time.strftime('%H:%M:%S', time.gmtime((sec1+sec2)/2)))

format = "%H:%M:%S"

times_interval=dict()#for each eiv_count, dict of subject_id, start and stop times when taking in the last interval of the EIV (from the previous EIV to this one)
times_half_interval=dict()
for i in {1,2,3,4,5,6,7,8}:
    times_interval[i]=dict()
    times_half_interval[i]=dict()
for index in range(data.shape[0]):
    time_curr_eiv=data['Absolute time'][index]
    if data['eiv_count'][index] > 1:
        time_prev_eiv=data['Absolute time'][index-1]
        time_half=half_time(time_prev_eiv, time_curr_eiv)
        times_interval[data['eiv_count'][index]][data['Participant ID'][index]]=(time_prev_eiv, time_curr_eiv)
        times_half_interval[data['eiv_count'][index]][data['Participant ID'][index]]=(time_half, time_curr_eiv)
        time_curr_eiv = datetime.datetime.strptime(time_curr_eiv, format)
        time_prev_eiv = datetime.datetime.strptime(time_prev_eiv, format)
        t.append((time_curr_eiv - time_prev_eiv).seconds)
    else:
        time_zero = data['TimeStartSession'][index]
        time_half=half_time(time_zero,time_curr_eiv)
        times_interval[data['eiv_count'][index]][data['Participant ID'][index]]=(time_zero,time_curr_eiv)
        times_half_interval[data['eiv_count'][index]][data['Participant ID'][index]]=(time_half,time_curr_eiv)
        time_curr_eiv = datetime.datetime.strptime(time_curr_eiv, format)
        time_zero = datetime.datetime.strptime(time_zero, format)
        t.append((time_curr_eiv - time_zero).seconds)

t = [x for x in t if x <3000]
print(np.mean(t))
print(np.std(t))
