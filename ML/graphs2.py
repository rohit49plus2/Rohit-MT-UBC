import os
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
from scipy.stats import f_oneway
from scipy.stats import ttest_ind
from statsmodels.stats.multitest import multipletests
from statsmodels.multivariate.manova import MANOVA
import statsmodels.api as sm
from statsmodels.formula.api import ols
from functools import reduce

dir_path = os.path.dirname(os.path.realpath(__file__))

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)  # or 199

labels=['Acc_Overall','Acc_None','Acc_Frus','Acc_Bore','Acc_Both']
interaction=[29.92,21.17,14.30,43.63,41.43]
gaze=[25.22,26.17,18.54,21.52,31.44]
combined=[27.08,28.70,18.97,22.93,33.81]

x = np.arange(len(labels))  # the label locations
width = 0.3  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, interaction, width, label='Interaction',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x , gaze, width, label='Gaze',color='#342A1F',hatch='.')
rects3 = ax.bar(x + width, combined, width, label='Both',color='#CAB8C8',hatch='*')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Frustration x Boredom',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=22,loc='upper left')
ax.set_ylim([0,50])
plt.yticks(fontsize=19)
plt.xticks(fontsize=19)

def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        print(rect)
        print(rect.get_x() + rect.get_width() / 2, height)
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 3),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',fontsize=11)


# autolabel(rects1)
# autolabel(rects2)
# autolabel(rects3)

ax.annotate('*',
            xy=(-0.3, 29.92),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(1.3, 28.7),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(1.0, 26.17),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(2.0, 18.54),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(2.3, 18.97),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(2.7, 43.63),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(3.7, 41.43),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)



fig.tight_layout()


plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()

print('\n\n\n')

labels=['Acc_Overall','Acc_None','Acc_Curi','Acc_Anxi','Acc_Both']
interaction=[21.65,21.33,20.38,26.46,20.94]
gaze=[26.26,33.20,21.33,19.63,30.28]
combined=[26.33,31.83,22.13,18.09,31.39]

x = np.arange(len(labels))  # the label locations
width = 0.3  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, interaction, width, label='Interaction',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x , gaze, width, label='Gaze',color='#342A1F',hatch='.')
rects3 = ax.bar(x + width, combined, width, label='Both',color='#CAB8C8',hatch='*')


# Add some text for labels, title and custom x-axis tick labels, etc.plt.grid(which='both',axis='y',color='gray', linestyle='-', linewidth=.5)

ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Curiosity x Anxiety',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=22,loc='upper left')
ax.set_ylim([0,50])
plt.yticks(fontsize=19)
plt.xticks(fontsize=19)


# autolabel(rects1)
# autolabel(rects2)
# autolabel(rects3)
ax.annotate('*',
            xy=(0.0, 26.26),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',color='black',
            xy=(0.3, 26.33),
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)


ax.annotate('*',
            xy=(1.3, 31.83),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(1.0, 33.2),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(2.7, 26.46),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(4.0, 30.28),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(4.3, 31.39),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

fig.tight_layout()

plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()
