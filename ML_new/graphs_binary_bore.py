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

labels=['Acc_Overall','Acc_None','Acc_Bore']
interaction=[51.25,49.29,53.79]
gaze=[50.47,50.41,50.61]
combined=[51.21,51.00,51.57]

x = np.arange(len(labels))  # the label locations
width = 0.3  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, interaction, width, label='Interaction',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x , gaze, width, label='Gaze',color='#342A1F',hatch='.')
rects3 = ax.bar(x + width, combined, width, label='Both',color='#CAB8C8',hatch='*')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Boredom - 2014 Dataset',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=22,loc='upper left')
ax.set_ylim([0,100])
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


autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

# ax.annotate('*',
#             xy=(-0.3, 29.92),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(1.3, 28.7),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(1.0, 26.17),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(2.0, 18.54),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(2.3, 18.97),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(2.7, 43.63),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(3.7, 41.43),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)



fig.tight_layout()


plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()

print('\n\n\n')

labels=['Acc_Overall','Acc_None','Acc_Bore']
interaction=[47.07,41.61,53.08]
gaze=[50.27,47.79,52.65]
combined=[46.79,45.28,48.35]

x = np.arange(len(labels))  # the label locations
width = 0.3  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, interaction, width, label='Interaction',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x , gaze, width, label='Gaze',color='#342A1F',hatch='.')
rects3 = ax.bar(x + width, combined, width, label='Both',color='#CAB8C8',hatch='*')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Boredom - Combined AOI Dataset',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=22,loc='upper left')
ax.set_ylim([0,100])
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


autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

# ax.annotate('*',
#             xy=(-0.3, 29.92),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(1.3, 28.7),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(1.0, 26.17),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(2.0, 18.54),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(2.3, 18.97),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(2.7, 43.63),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(3.7, 41.43),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)



fig.tight_layout()


plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()

print('\n\n\n')

labels=['Acc_Overall','Acc_None','Acc_Bore']
interaction=[47.14,41.49,53.47]
gaze=[51.09,47.34,54.57]
combined=[46.80,38.90,55.04]

x = np.arange(len(labels))  # the label locations
width = 0.3  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, interaction, width, label='Interaction',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x , gaze, width, label='Gaze',color='#342A1F',hatch='.')
rects3 = ax.bar(x + width, combined, width, label='Both',color='#CAB8C8',hatch='*')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Boredom - Combined Non AOI Dataset',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=22,loc='upper left')
ax.set_ylim([0,100])
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


autolabel(rects1)
autolabel(rects2)
autolabel(rects3)

# ax.annotate('*',
#             xy=(-0.3, 29.92),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(1.3, 28.7),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(1.0, 26.17),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(2.0, 18.54),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(2.3, 18.97),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(2.7, 43.63),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(3.7, 41.43),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)



fig.tight_layout()


plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()

print('\n\n\n')
