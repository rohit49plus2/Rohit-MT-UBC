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
base=[25.63,25.31,25.14,26.05,26.01]
rf=[31.59,39.76,11.79,29.09,32.73]
lr=[24.99,10.98,14.88,32.94,47.94]

x = np.arange(len(labels))  # the label locations
width = 0.3  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, base, width, label='Baseline',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x , rf, width, label='RF',color='#342A1F',hatch='.')
rects3 = ax.bar(x + width, lr, width, label='LR',color='#CAB8C8',hatch='*')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Frustration x Boredom',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=22,loc='upper left')
plt.yticks(fontsize=19)
plt.xticks(fontsize=19)
ax.set_ylim([0,55])

def autolabel(rects):
    """Attach a text label above each bar in *rects*, displaying its height."""
    for rect in rects:
        height = rect.get_height()
        print(rect)
        print(rect.get_x() + rect.get_width() / 2, height)
        ax.annotate('{}'.format(height),
                    xy=(rect.get_x() + rect.get_width() / 2, height),
                    xytext=(0, 1),  # 3 points vertical offset
                    textcoords="offset points",
                    ha='center', va='bottom',fontsize=11)


# autolabel(rects1)
# autolabel(rects2)
# autolabel(rects3)

ax.annotate('*',
            xy=(0.0, 31.59),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(1.0, 39.76),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(1.7, 25.14),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(3.3, 32.94),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(3.0, 29.09),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(4.3, 47.94),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)


fig.tight_layout()

plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()

print('\n\n\n')

labels=['Acc_Overall','Acc_None','Acc_Curi','Acc_Anxi','Acc_Both']
base=[25.56,25.11,25.58,25.59,26.01]
rf=[26.46,24.13,33.00,12.77,27.62]
lr=[22.23,37.12,5.26,25.81,28.99]

x = np.arange(len(labels))  # the label locations
width = 0.3  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, base, width, label='Baseline',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x , rf, width, label='RF',color='#342A1F',hatch='.')
rects3 = ax.bar(x + width, lr, width, label='LR',color='#CAB8C8',hatch='*')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Curiosity x Anxiety',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=22,loc='upper left')
ax.set_ylim([0,45])
plt.yticks(fontsize=19)
plt.xticks(fontsize=19)


# autolabel(rects1)
# autolabel(rects2)
# autolabel(rects3)
ax.annotate('*',
            xy=(-0.3,25.56),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',color='black',
            xy=(0.0, 26.46),
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)


ax.annotate('*',
            xy=(1.3, 37.12),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(2.0, 33.0),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(2.7, 25.59),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(3.3, 25.81),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

fig.tight_layout()

plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()
