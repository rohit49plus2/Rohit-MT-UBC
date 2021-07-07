#Script to compare the offline and online fixations detected by the fixation detectors of the Experiment platform
#@Sebastien Lalle

import csv
import numpy as np
import os
import pandas as pd

eye_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Eye Tracking Data/SMI Data/'

for file in os.listdir(eye_path):
    if 'Raw' in file and file.split('.')[-1] =='csv':
        id = file.split('-')[0].upper()
        with open(os.path.join(eye_path,file),'r') as f:
            lines = f.readlines()
        new_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2016/Eye Tracking Data/SMI Data/Corrected/'
        with open(os.path.join(new_path,file),'w') as f:
            i=0
            for line in lines:
                if i <38:
                    f.write(line)
                if i>=38:
                    if i%2==0:
                        f.write(line)
                i+=1
