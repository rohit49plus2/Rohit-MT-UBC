# -*- coding: utf-8 -*-
import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import numpy as np
#List of user ID with valid data
# MODIFIE ICI
# ul = ["109", "111", "113", "121", "122", "123", "125", "145", "147", "148", "150", "151", "152", "153", "154", "155", "160", "161", "162", "163", "164", "165", "166", "167", "168", "169", "170", "173", "174", "177"] # removed 116 and 172 because invalid date for aois
#FOR 2016 set
# emotion_qs=["Q1-enjoying myself","Q2-hopeful","Q3-proud","Q12-curious","Q14-eureka","Q4-frustrated","Q5-anxious","Q6-ashamed","Q7-hopeless","Q8-bored","Q10-contempt","Q11-confused","Q13-sad","Q9-surprised","Q15-neutral","Q16-task is valuable","Q17-can do well on this task"] #List of emotion headings, we will iterate over this list to generate classes
# emotion_qs.sort()
# emotions=[q.split('-')[1] for q in emotion_qs] #the emotion names

#For 2014 set
emotion_qs=["Happy","Enjoyment","Hope","Pride","Curiosity","Eureka","Anger","Fear","Disgust","Frustration","Anxiety","Shame","Hopelessness","Boredom","Contempt","Confusion","Sadness","Surprise","Neutral","Task Value"]

emotions=["Happy","Enjoyment","Hope","Pride","Curiosity","Eureka","Anger","Fear","Disgust","Frustration","Anxiety","Shame","Hopelessness","Boredom","Contempt","Confusion","Sadness","Surprise","Neutral","Task Value"]

def emotion(emotionq):#returns the emotion label
	return emotions[emotion_qs.index(emotionq)]

dir_path = os.path.dirname(os.path.realpath(__file__))

#Get classes
# MODIFIE ICI
emotion_file = dir_path+"/EmotionReportData2014.csv"
threshold3=dict()
threshold4=dict()
# eye_file1=dir_path+"/Eye_Tracking/sample_features_MetaTutor2014_EVfullwindow_6.tsv"
# eye1=pd.read_csv(eye_file1,delimiter='\t')
# eye_file2=dir_path+"/Eye_Tracking/sample_features_MetaTutor2014_EV15swindow_6.tsv"
# eye2=pd.read_csv(eye_file2,delimiter='\t')
# ul1=eye1['Part_id'].unique()
# ul2=eye2['Part_id'].unique()
# ul=[*ul1, *ul2]

with open (emotion_file, 'rt') as f:
	currentid = -1
	reader = csv.DictReader(f, delimiter=';')

	for row in reader:
		# if row["Participant ID"] not in ul: #ignore data for user without valid data
		# 	continue

		if currentid == -1 or (int(row["Participant ID"][-3:]) != currentid and currentid > -1): #new student in logs
			currentid = int(row["Participant ID"][-3:])
			EIV_count = 1

		# EIVtime = int(calendar.timegm(datetime.datetime.strptime(row["DateSession"]+" "+row["Absolute time"], "%m/%d/%Y %H:%M:%S").timetuple()) * 1000000 )

		sc_id = (row["Participant ID"], EIV_count)
		threshold3[sc_id]=dict()
		threshold4[sc_id]=dict()
		for emotionq in emotion_qs:
			if int(row[emotionq])>=3:
				(threshold3[sc_id])[emotion(emotionq)]=1
			else:
				(threshold3[sc_id])[emotion(emotionq)]=0
			if int(row[emotionq])>=4:
				(threshold4[sc_id])[emotion(emotionq)]=1
			else:
				(threshold4[sc_id])[emotion(emotionq)]=0
		EIV_count += 1


#================
pd.options.mode.chained_assignment = None
combined_files = dir_path+"/Combined_Data/"
for file in os.listdir(combined_files):
	rf_full = os.path.join(combined_files,file)
	print('Loading %s' % rf_full)
	thres = (file.split('.')[0]).split('_')[-1]
	df1=pd.read_pickle(rf_full)
	# df1 = df1.sort_values(by = 'key')
	df2=df1.copy()
	# print(df1.isnull().sum())
	threshold = []
	if thres=='3':
	    threshold=threshold3
	else:
	    threshold=threshold4
	for emotionq in emotion_qs:
		emotion_list=[]
		for i in range(df2.shape[0]):
			id=df2.key[i]
			df2[emotionq][i]=(threshold[id][emotionq])
		# print(len(emotion_list))
		# df2[emotionq]=emotion_list
	for i in range(df2.shape[0]):
		id=df2.key[i]
		clean=1
		for emotionq in emotion_qs:
			if not(np.isnan(df1[emotionq][i])):
				assert(df2[emotionq][i]==df1[emotionq][i])
	df2.to_pickle(rf_full)
