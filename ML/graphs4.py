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
rf_log=[36.49, 32.94,18.05,39.37,51.54]
rf_eye=[26.56,40.48,9.06,21.18,19.10]
lr_log=[28.64,6.37,3.74,63.76,48.51]
lr_eye=[22.77,12.79,19.19,16.36,48.56]
en=[34.36,38.57,9.12, 31.82,44.89]

x = np.arange(len(labels))  # the label locations
width = 0.15  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - 2*width, rf_log, width, label='RF_log',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x - width, rf_eye, width, label='RF_eye',color='#342A1F',hatch='.')
rects3 = ax.bar(x, lr_log, width, label='LR_log',color='#CAB8C8',hatch='*')
rects4 = ax.bar(x + width, lr_eye, width, label='LR_eye',color='grey',hatch='-')
rects5 = ax.bar(x + 2*width, en, width, label='Ensemble',color='black',hatch='-')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Frustration x Boredom',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=20,loc='upper left')
plt.yticks(fontsize=19)
plt.xticks(fontsize=19)
ax.set_ylim([0,90])

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
                    ha='center', va='bottom',fontsize=12)


# autolabel(rects1)
# autolabel(rects2)
# autolabel(rects3)
# autolabel(rects4)
# autolabel(rects5)
#
# ax.annotate('*',
#             xy=(0.4, 35.28),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(1.0, 36.71),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(1.4, 40.83),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(1.8, 24.24),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(3.2,40.06),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(4.2, 48.53),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(4.4, 47.55),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)


fig.tight_layout()

plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()

print('\n\n\n')

labels=['Acc_Overall','Acc_None','Acc_Curi','Acc_Anxi','Acc_Both']
rf_log=[25.62,29.22,28.71,22.82,20.22]
rf_eye=[26.23,23.15,33.15, 7.90,29.97]
lr_log=[13.96,8.47, 6.98,33.30,16.87]
lr_eye=[26.76,51.54, 4.67,22.89,35.61]
en=[24.31,26.70,28.02, 9.17,26.24]

x = np.arange(len(labels))  # the label locations

fig, ax = plt.subplots()
rects1 = ax.bar(x - 2*width, rf_log, width, label='RF_log',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x - width, rf_eye, width, label='RF_eye',color='#342A1F',hatch='.')
rects3 = ax.bar(x, lr_log, width, label='LR_log',color='#CAB8C8',hatch='*')
rects4 = ax.bar(x + width, lr_eye, width, label='LR_eye',color='grey',hatch='-')
rects5 = ax.bar(x + 2*width, en, width, label='Ensemble',color='black',hatch='-')



# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Curiosity x Anxiety',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=20,loc='upper left')
ax.set_ylim([0,70])
plt.yticks(fontsize=19)
plt.xticks(fontsize=19)


# autolabel(rects1)
# autolabel(rects2)
# autolabel(rects3)
# autolabel(rects4)
# autolabel(rects5)

# ax.annotate('*',
#             xy=(0.4, 28.04),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
#
# ax.annotate('*',
#             xy=(1.2, 30.01),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(1.4, 28.2),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(2.0, 30.93),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
# ax.annotate('*',
#             xy=(2.4, 34.51),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)
#
# ax.annotate('*',
#             xy=(3.2, 28.09),color='black',
#             xytext=(0, 1),  # 3 points vertical offset
#             textcoords="offset points",
#             ha='center', va='bottom',fontsize=20)

fig.tight_layout()

plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
plt.minorticks_on()
plt.show()
