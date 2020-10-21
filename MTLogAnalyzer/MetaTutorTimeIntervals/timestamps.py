import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import pickle
import itertools
import numpy as np
import math
dir_path = os.path.dirname(os.path.realpath(__file__))

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
times_full=dict()#for each eiv_count, dict of subject_id, start and stop times when taking in the full window until the EIV
times_interval=dict()#for each eiv_count, dict of subject_id, start and stop times when taking in the last interval of the EIV (from the previous EIV to this one)
for i in {1,2,3,4,5,6,7,8}:
    times_full[i]=dict()
    times_interval[i]=dict()
for index in range(data.shape[0]):
    times_full[data['eiv_count'][index]][data['Participant ID'][index]]=(data['TimeStartSession'][index],data['Absolute time'][index])
    # times_interval[data['eiv_count'][index]][data['Participant ID'][index]]=(data['TimeStartSession'][index],data['Absolute time'][index])
    if data['eiv_count'][index] > 1:
        times_interval[data['eiv_count'][index]][data['Participant ID'][index]]=(data['Absolute time'][index-1],data['Absolute time'][index])
    else:
        times_interval[data['eiv_count'][index]][data['Participant ID'][index]]=(data['TimeStartSession'][index],data['Absolute time'][index])
