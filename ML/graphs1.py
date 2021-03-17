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
base=[25.48,24.73,24.24,27.39,25.46]
rf=[31.52,36.71,13.56,30.28,35.32]
lr=[25.71,9.58,11.47,40.06,48.53]
en =[35.28,40.83,11.86,28.30,47.55]

x = np.arange(len(labels))  # the label locations
width = 0.2  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, base, width, label='Baseline',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x , rf, width, label='RF',color='#342A1F',hatch='.')
rects3 = ax.bar(x + width, lr, width, label='LR',color='#CAB8C8',hatch='*')
rects4 = ax.bar(x + 2*width, en, width, label='ENSEMBLE',color='grey',hatch='-')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Frustration x Boredom',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=20,loc='upper left')
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
# autolabel(rects4)

ax.annotate('*',
            xy=(0.4, 35.28),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(1.0, 36.71),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(1.4, 40.83),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(1.8, 24.24),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(3.2,40.06),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(4.2, 48.53),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(4.4, 47.55),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)


fig.tight_layout()

plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()

print('\n\n\n')

labels=['Acc_Overall','Acc_None','Acc_Curi','Acc_Anxi','Acc_Both']
base=[25.59,25.61,25.81,25.68,25.49]
rf=[25.92,26.19,30.93,15.36,25.10]
lr=[20.36,30.01,5.82,28.09,26.24]
en=[28.04,28.2,34.51,12.15,28.89]

x = np.arange(len(labels))  # the label locations

fig, ax = plt.subplots()
rects1 = ax.bar(x - width, base, width, label='Baseline',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x , rf, width, label='RF',color='#342A1F',hatch='.')
rects3 = ax.bar(x + width, lr, width, label='LR',color='#CAB8C8',hatch='*')
rects4 = ax.bar(x + 2*width, en, width, label='ENSEMBLE',color='grey',hatch='-')



# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Curiosity x Anxiety',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=20,loc='upper left')
ax.set_ylim([0,45])
plt.yticks(fontsize=19)
plt.xticks(fontsize=19)


# autolabel(rects1)
# autolabel(rects2)
# autolabel(rects3)
# autolabel(rects4)

ax.annotate('*',
            xy=(0.4, 28.04),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)


ax.annotate('*',
            xy=(1.2, 30.01),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(1.4, 28.2),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(2.0, 30.93),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)
ax.annotate('*',
            xy=(2.4, 34.51),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

ax.annotate('*',
            xy=(3.2, 28.09),color='black',
            xytext=(0, 1),  # 3 points vertical offset
            textcoords="offset points",
            ha='center', va='bottom',fontsize=20)

fig.tight_layout()

plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()
