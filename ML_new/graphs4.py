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
rf_log=[23.46,17.76,23.06,35.61,21.19]
rf_eye=[27.17,35.43,14.34,23.37,25.23]
svm_log=[22.39,4.86,7.57,51.96,30.47]
svm_eye=[30.96,37.67,23.03,28.68,27.30]
en=[32.20,37.45,21.87,32.07,29.40]

x = np.arange(len(labels))  # the label locations
width = 0.15  # the width of the bars

fig, ax = plt.subplots()
rects1 = ax.bar(x - 2*width, rf_log, width, label='RF_log',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x - width, rf_eye, width, label='RF_eye',color='#342A1F',hatch='.')
rects3 = ax.bar(x, svm_log, width, label='SVM_log',color='#CAB8C8',hatch='*')
rects4 = ax.bar(x + width, svm_eye, width, label='SVM_eye',color='grey',hatch='-')
rects5 = ax.bar(x + 2*width, en, width, label='Ensemble',color='black',hatch='-')


# Add some text for labels, title and custom x-axis tick labels, etc.
ax.set_ylabel('Percentage Accuracies',fontsize=24)
ax.set_title('Frustration x Boredom',fontsize=24)
ax.set_xticks(x)
ax.set_xticklabels(labels)
ax.legend(fontsize=20,loc='upper left')
plt.yticks(fontsize=19)
plt.xticks(fontsize=19)
ax.set_ylim([0,70])

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
rf_log=[26.71,24.57,29.23,21.83,27.82]
rf_eye=[27.43,28.39,32.25,14.67,27.50]
svm_log=[14.96,14.62, 3.57,59.02, 8.82]
svm_eye=[29.77,27.85,36.87,14.11,30.83]
en=[30.21,22.48,40.03,13.98,31.74]

x = np.arange(len(labels))  # the label locations

fig, ax = plt.subplots()
rects1 = ax.bar(x - 2*width, rf_log, width, label='RF_log',color='#F4D4D4',hatch='/')
rects2 = ax.bar(x - width, rf_eye, width, label='RF_eye',color='#342A1F',hatch='.')
rects3 = ax.bar(x, svm_log, width, label='SVM_log',color='#CAB8C8',hatch='*')
rects4 = ax.bar(x + width, svm_eye, width, label='SVM_eye',color='grey',hatch='-')
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
