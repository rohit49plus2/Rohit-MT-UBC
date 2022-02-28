import os.path
import sys, time, datetime, calendar, csv
import pandas as pd
import pickle
import numpy as np

dir_path = os.path.dirname(os.path.realpath(__file__))

f1 = dir_path+'/Combined_Data_2014_Corrected/data_full_full_3.pkl'

with open(f1,'rb') as f:
    df = pickle.load(f)

print(df)

f2 = dir_path+'/Combined_Data_2016_Corrected/data_full_full_3.pkl'

with open(f2,'rb') as f:
    df = pickle.load(f)

print(df)
