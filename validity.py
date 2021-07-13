import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
import os

file_path='./validity/output.txt'
with open(file_path,'r') as f:
    df = pd.read_csv(f, sep='\t',names=['ID','Scene', 'Score'])


# y = list(df['Score'])
# dt = 1
# x = np.arange(0, len(y), dt)
#
# fig, ax = plt.subplots()
# rects1 = ax.scatter(x, y, label='validity')
#
# # Add some text for labels, title and custom x-axis tick labels, etc.
# ax.set_ylabel('Proportion')
# ax.set_title('Valid Eye Tracking Points')
# ax.set_xticks(x)
# # ax.set_xticklabels(labels)
# ax.legend()
#
# # ax.bar_label(rects1, padding=3)
# plt.show()

x = []
y = []
for thres in np.arange(0,1.02,.02):
    prop_samples = (df['Score']>thres).sum()/df.shape[0]
    print(thres,prop_samples)
    x.append(thres)
    y.append(prop_samples)

fig, ax = plt.subplots()
ax.plot(x, y, label='prop_samples')

plt.rc('font', size=20) #controls default text size
plt.rc('axes', titlesize=20) #fontsize of the title
plt.rc('axes', labelsize=20) #fontsize of the x and y labels
plt.rc('xtick', labelsize=24) #fontsize of the x tick labels
plt.rc('ytick', labelsize=24) #fontsize of the y tick labels
plt.rc('legend', fontsize=16) #fontsize of the legend
# plt.rc('title', fontsize=24) #fontsize of the legend

# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Proportion of Samples with Valid Gaze Points more than the Threshold',fontsize=18)
ax.set_xlabel('Threshold',fontsize=20)
ax.set_title('Valid Eye Tracking Points')
ax.legend()

plt.xticks(np.arange(0,1.1,0.1),fontsize=16)
plt.yticks(np.arange(0,1.1,0.1),fontsize=16)
# ax.bar_label(rects1, padding=3)
plt.show()
