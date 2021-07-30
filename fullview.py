import os
import pandas as pd
import csv
import numpy as np
import datetime, calendar
log_path_2014='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/MetaTutor Logs/LOGS'
log_path_2016='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Logs/cleaned logs compiled'

count_2014=dict()
count_2016=dict()
for file in os.listdir(log_path_2014):
    with open(os.path.join(log_path_2014,file),'r') as f:
        reader = csv.reader(f, delimiter='\t')
        i=0
        for row in reader:
            if i ==2:
                id = row[1]
                count_2014[id]=0
            if len(row)==6:
                row[4] == 'FullView'
                count_2014[id]+=1
            i+=1
for file in os.listdir(log_path_2016):
    with open(os.path.join(log_path_2016,file),'r') as f:
        reader = csv.reader(f, delimiter='\t')
        i=0
        for row in reader:
            if i ==2:
                id = row[1]
                count_2016[id]=0
            if len(row)==6:
                row[4] == 'FullView'
                count_2016[id]+=1
            i+=1
print(list(count_2014.values()))
print(list(count_2016.values()))

print(np.mean(list(count_2014.values())))
print(np.mean(list(count_2016.values())))
