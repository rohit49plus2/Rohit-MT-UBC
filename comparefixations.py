import os
import sys
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import math
# import time

np.set_printoptions(threshold=sys.maxsize)
pd.set_option('display.max_rows', None)
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)

def match_score(N):
    fix_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData/Fixations/Tests/'
    eye_path='/home/rohit/Documents/Academics/UBC/RA-Project/MetaTutor - study data/Data 2014/EyeTrackingData/'

    df=pd.DataFrame(columns=['id','Tobii Fixations','New Fixations','Mean Position Difference','StdDev Position Difference','Max Position Difference', 'Mean Duration Difference', 'StdDev Duration Difference', 'Max Duration Difference','Match Score'])
    for file in os.listdir(eye_path):
        if 'Fixation-Data' in file and file.split('.')[-1] =='tsv':
            id = file.split('-')[0].upper()
            with open(os.path.join(eye_path,file),'r') as f:
                df1 = pd.read_csv(f, sep='\t',skiprows=19)#skip to the data
                # print(df)
            with open(os.path.join(fix_path,id+'-Fixations-'+str(N)+'.csv'),'r') as f:
                df2 = pd.read_csv(f, sep=',',skiprows=0)#skip to the data
                # print(df2)
            # s=time.time()
            print(id)
            # print('true',df1.shape)
            # print('new',df2.shape)
            pos_dif=[]
            dur_dif=[]

            m = []
            for i in range(df2.shape[0]):
                start = df2.loc[i,'fix_start_time']
                dur = df2.loc[i,'fix_duration']
                x1 = df2.loc[i,'fix_x']
                y1 = df2.loc[i,'fix_y']

                # matched_fixation = df1[df1['Timestamp'] == min(list(df1['Timestamp']), key=lambda x:abs(x-start))]
                matched_fixation = df1.iloc[(df1['Timestamp']-start).abs().argsort()[:1]]
                x2 = matched_fixation['MappedFixationPointX']
                y2 = matched_fixation['MappedFixationPointY']
                dur2 = matched_fixation['FixationDuration']

                dist = ((x2-x1)**2 + (y2-y1)**2)**0.5
                pos_dif.append(dist)
                dur_dif.append(dur2-dur)
                m.append(int((dist <= 50) & ((dur2-dur)<100)))

            # print(m)
            # print(m.count(1))
            df.loc[len(df)] = [id,df1.shape[0],df2.shape[0],np.mean(pos_dif),np.std(pos_dif), np.max(pos_dif), np.mean(dur_dif), np.std(dur_dif), np.max(dur_dif),(m.count(1)/df2.shape[0])]
            # print(time.time()-s)
    # print(df.to_latex())
    df.to_csv('fixation-analysis/fixationoutput_'+str(N)+'.csv')

# for N in [2,3,4,6]:
#     print(N)
#     match_score(N)
Ndf=pd.DataFrame(columns = ['N','Mean of Match Score', 'StdDev of Match Score', 'Mean of Mean Position Difference', 'StdDev of Mean Position Difference', 'Mean of Mean Duration Difference'])
for N in [2,3,4,5,6,10]:
    print(N)
    df1 = pd.read_csv('fixation-analysis/fixationoutput_'+str(N)+'.csv')
    df1 = df1.iloc[:,1:]
    file_path='validity/output.txt'
    with open(file_path,'r') as f:
        df2 = pd.read_csv(f, sep='\t',names=['id','Scene', 'Score'])
    df2=df2[df2['Scene'].str.contains('allsc')]
    # df1=df1[df1['Mean Position Difference'] < 2000]
    # print(df2)

    df2=df2[df2['Score'] >= 0.65]
    df = df1.merge(df2[['id','Score']],how='inner').sort_values(by='Score')
    df = df.set_index('id')

    # plt.scatter(df['Score'],df['Match Score'])
    # plt.yticks(np.arange(0,1.1,.1),fontsize=16)
    # plt.xticks(fontsize=16)
    # plt.ylabel('Match Score',fontsize=22)
    # plt.xlabel('Validity Score',fontsize=22)
    # # plt.plot(df['Score'],df['Mean Position Difference'])
    # plt.show()
    # print(df)
    print(df[['Tobii Fixations','New Fixations']].to_latex())
    print(df[['Mean Position Difference','StdDev Position Difference']].round(2).to_latex())
    print(df[['Mean Duration Difference','StdDev Duration Difference']].round(2).to_latex())
    print(df[['Match Score']].round(2).to_latex())

    Ndf.loc[len(Ndf),:]= [N,np.mean(df['Match Score']),np.std(df['Match Score']),np.mean(df['Mean Position Difference']),np.std(df['Mean Position Difference']),np.mean(df['Mean Duration Difference'])]
    # print(np.mean(df['Match Score']))
    # print(np.max(df['Match Score']))
    # print(np.min(df['Match Score']))
    # print(np.std(df['Match Score']))
    # print(np.mean(df['Mean Position Difference']))
    # print(np.mean(df['Mean Duration Difference']))

Ndf = Ndf.set_index('N')
Ndf.loc[:,Ndf.columns!= 'N'] = Ndf.loc[:,Ndf.columns!= 'N'].applymap(lambda x: round(x, 3 - int(np.floor(math.log(abs(x),10)))))#round to 3
print(Ndf[['Mean of Match Score']].round(4).to_latex())
print(Ndf[['Mean of Mean Position Difference', 'StdDev of Mean Position Difference']].round(4).to_latex())
print(Ndf[['Mean of Mean Duration Difference']].round(4).to_latex())
print(Ndf.round(4).to_latex())
