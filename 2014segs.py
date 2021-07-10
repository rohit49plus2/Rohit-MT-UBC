import os
import pandas as pd
import csv
import datetime, calendar
log_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/MetaTutor Logs/LOGS'

start_times=dict()
end_times=dict()
for file in os.listdir(log_path):
    with open(os.path.join(log_path,file),'r') as f:
        reader = csv.reader(f, delimiter='\t')
        i=0
        ev_num = 1
        for row in reader:
            if i ==2:
                id = row[1]
            if len(row)==5:
                if row[4] == 'Questionnaire Start - EIV':
                    start_times[(id,ev_num)]=row[1]
            if len(row)==5:
                if row[4] == 'Questionnaire End - EIV':
                    end_times[(id,ev_num)]=row[1]
                    ev_num+=1
            i+=1
print(start_times)
print(end_times)

eye_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData'

date=dict()
eye_start=dict()
for file in os.listdir(eye_path):
    if 'All-Data' in file and file.split('.')[-1] =='tsv':
        id = file.split('-')[0].upper()
        with open(os.path.join(eye_path,file),'r') as f:
            reader = pd.read_csv(f, sep='\t',nrows=11)
            eye_start[id] = reader.iloc[6,0]
            date[id] = reader.iloc[5,0]


format1 = "%H:%M:%S"
format2 = " %I:%M:%S %p"
ids=[]
for pair in start_times.keys():
    id = pair[0]
    ev_num=pair[1]
    if ev_num ==1:
        ids.append(id)
        fsegoutfull = open("/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EIV_window_segs/full_window/EIVsegs_"+str(id)+".segs", "w") # open new output segment file
        start_session = datetime.datetime.strptime(eye_start[id],format2)
        start_time=start_session
    else:
        start_time = datetime.datetime.strptime(end_times[(pair[0],pair[1]-1)],format1)
    end_time = datetime.datetime.strptime(start_times[pair],format1)
    start_time_full = (start_time-start_session).seconds*1000
    end_time_corrected = (end_time - start_session).seconds*1000
    segname = "EIVreport_"+str(ev_num)+"_"+str(end_time_corrected)
    fsegoutfull.write(segname+"\t"+segname+"\t"+str(start_time_full)+"\t"+str(end_time_corrected)+"\n")

print(ids)
