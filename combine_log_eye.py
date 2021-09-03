from gen_classes import *
year = 2014
import numpy as np
np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def make_id_tuple(part_id,sc_id):
    eiv_num = int(sc_id.split('_')[1])
    segID = (part_id,eiv_num)
    return segID

if year==2014:
    # eye_15s_name='/Eye_Tracking_Classes_Corrected/data_2014_15s_threshold'
    eye_full_name='/Eye_Tracking_Classes_Corrected/data_2014_full_threshold'
    log_half_name='/Action Features Rohit/test_file_rohit half' #temporarily keeping full
    log_full_name='/Action Features Rohit/test_file_rohit full'
for threshold in {3,4}:
    log_half=pd.DataFrame()
    log_full=pd.DataFrame()
    # eye_15s=pd.read_csv(dir_path+eye_15s_name+str(threshold)+'.csv',delimiter='\t')
    eye_full=pd.read_csv(dir_path+eye_full_name+str(threshold)+'.csv',delimiter='\t')
    # eye_15s.insert(0,"key",[make_id_tuple(x, y) for x, y in zip(eye_15s['Part_id'], eye_15s['Sc_id'])]) #add new key system
    # eye_15s.set_index('key')
    eye_full.insert(0,"key",[make_id_tuple(x, y) for x, y in zip(eye_full['Part_id'], eye_full['Sc_id'])]) #add new key system
    eye_full.set_index('key')
    for eiv in {1,2,3,4,5}:
        log_half_temp=pd.read_csv(dir_path+log_half_name+str(eiv)+'.csv',delimiter=',')
        log_half_temp.insert(0,"key",[(id,eiv) for id in log_half_temp['ID']])
        log_half_temp.set_index('key')
        log_half=log_half.append(log_half_temp)

        log_full_temp=pd.read_csv(dir_path+log_full_name+str(eiv)+'.csv',delimiter=',')
        log_full_temp.insert(0,"key",[(id,eiv) for id in log_full_temp['ID']])
        log_full_temp.set_index('key')
        log_full=log_full.append(log_full_temp)
    print(eye_full.shape) #(319,610)
    print(list(eye_full.columns))
    # print(log_full.sort_values(by=['key']).shape) #(325,59)
    # merged_15s_half=eye_15s.merge(log_half,how='outer',on='key')
    # merged_15s_full=eye_15s.merge(log_full,how='outer',on='key')
    merged_full_half=eye_full.merge(log_half,how='outer',on='key')
    merged_full_full=eye_full.merge(log_full,how='outer',on='key')

    # print(eye_full.isnull().sum())
    # print(merged_full_full.isnull().sum())
    # print(merged_full_full.shape)
    # merged_15s_half.to_pickle(dir_path+'/Combined_Data_2014/data_15s_half_'+str(threshold)+'.pkl')
    # merged_15s_full.to_pickle(dir_path+'/Combined_Data_2014/data_15s_full_'+str(threshold)+'.pkl')
    merged_full_half.to_pickle(dir_path+'/Combined_Data_2014_Corrected/data_full_half_'+str(threshold)+'.pkl')
    merged_full_full.to_pickle(dir_path+'/Combined_Data_2014_Corrected/data_full_full_'+str(threshold)+'.pkl')
