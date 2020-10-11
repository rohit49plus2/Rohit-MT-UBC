# -*- coding: utf-8 -*-
import os.path
import sys, time, datetime, calendar, csv

#List of user ID with valid data
# MODIFIE ICI
ul = ["109", "111", "113", "121", "122", "123", "125", "145", "147", "148", "150", "151", "152", "153", "154", "155", "160", "161", "162", "163", "164", "165", "166", "167", "168", "169", "170", "173", "174", "177"] # removed 116 and 172 because invalid date for aois

dir_path = os.path.dirname(os.path.realpath(__file__))

#Get classes
# MODIFIE ICI
emotion_file = dir_path+"/self_report_emotions.csv"
threshold3=dict()
threshold4=dict()

emotion_qs=["Q1-enjoying myself","Q2-hopeful","Q3-proud","Q12-curious","Q14-eureka","Q4-frustrated","Q5-anxious","Q6-ashamed","Q7-hopeless","Q8-bored","Q10-contempt","Q11-confused","Q13-sad","Q9-surprised","Q15-neutral","Q16-task is valuable","Q17-can do well on this task"] #List of emotion headings, we will iterate over this list to generate classes
emotion_qs.sort()
emotions=[q.split('-')[1] for q in emotion_qs] #the emotion names

def emotion(emotionq):#returns the emotion label
	return emotions[emotion_qs.index(emotionq)]

with open (emotion_file, 'rt') as f:
	currentid = -1
	reader = csv.DictReader(f, delimiter=';')

	for row in reader:
		if row["RawPID"][-3:] not in ul: #ignore data for user without valid data
			continue

		if currentid == -1 or (int(row["RawPID"][-3:]) != currentid and currentid > -1): #new student in logs
			currentid = int(row["RawPID"][-3:])
			EIV_count = 1

		EIVtime = int(calendar.timegm(datetime.datetime.strptime(row["date"]+" "+row["logTime"], "%d/%m/%Y %H:%M:%S").timetuple()) * 1000000 )

		sc_id = "EIVreport_"+str(EIV_count)+"_"+str(EIVtime)
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
f_full_threshold3 = open(dir_path+"/Eye_Tracking_Classes/data_full_threshold3.csv", "wt")
f_full_threshold4 = open(dir_path+"/Eye_Tracking_Classes/data_full_threshold4.csv", "wt")
f_15_threshold3 = open(dir_path+"/Eye_Tracking_Classes/data_15s_threshold3.csv", "wt")
f_15_threshold4 = open(dir_path+"/Eye_Tracking_Classes/data_15s_threshold4.csv", "wt")


#Full windows
# MODIFIE ICI
with open (dir_path+"/Eye_Tracking/smi_sample_features_full.tsv", 'rt') as f_full:
	for line in f_full:
		if line.find("Sc_id")>-1: #first line
			f_full_threshold3.write(line.strip())
			f_full_threshold4.write(line.strip())
			for emotion in emotions:
				f_full_threshold3.write("\t"+emotion)
				f_full_threshold4.write("\t"+emotion)
			f_full_threshold3.write("\n")
			f_full_threshold4.write("\n")
			continue

		if line.find("_allsc")>-1: #ignore AVERAGE lines
			continue

		segID = line.strip().split("\t")[1] #get segment ID (sc_id)
		f_full_threshold3.write(line.strip())
		f_full_threshold4.write(line.strip())
		for emotion in emotions:
			f_full_threshold3.write("\t"+str(threshold3[segID][emotion]))
			f_full_threshold4.write("\t"+str(threshold4[segID][emotion]))
		f_full_threshold3.write("\n")
		f_full_threshold4.write("\n")

with open (dir_path+"/Eye_Tracking/smi_sample_features_15s.tsv", 'rt') as f_15:
	for line in f_15:
		if line.find("Sc_id")>-1: #first line
			f_15_threshold3.write(line.strip())
			f_15_threshold4.write(line.strip())
			for emotion in emotions:
				f_15_threshold3.write("\t"+emotion)
				f_15_threshold4.write("\t"+emotion)
			f_15_threshold3.write("\n")
			f_15_threshold4.write("\n")
			continue

		if line.find("_allsc")>-1: #ignore AVERAGE lines
			continue

		segID = line.strip().split("\t")[1] #get segment ID (sc_id)
		f_15_threshold3.write(line.strip())
		f_15_threshold4.write(line.strip())
		for emotion in emotions:
			f_15_threshold3.write("\t"+str(threshold3[segID][emotion]))
			f_15_threshold4.write("\t"+str(threshold4[segID][emotion]))
		f_15_threshold3.write("\n")
		f_15_threshold4.write("\n")
