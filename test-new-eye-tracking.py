# -*- coding: utf-8 -*-
import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import numpy as np
# List of user ID with valid data
# MODIFIE ICI
# ul = ["109", "111", "113", "121", "122", "123", "125", "145", "147", "148", "150", "151", "152", "153", "154", "155", "160", "161", "162", "163", "164", "165", "166", "167", "168", "169", "170", "173", "174", "177"] # removed 116 and 172 because invalid date for aois
dir_path = os.path.dirname(os.path.realpath(__file__))

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

#Get classes
# MODIFIE ICI
emotion_file = dir_path+"/2016 emotions reports.csv"
threshold3=dict()
threshold4=dict()
eye_file1=dir_path+"/Eye_Tracking_Corrected/smi_sample_features.tsv"
eye1=pd.read_csv(eye_file1,delimiter='\t')
print(eye1)
