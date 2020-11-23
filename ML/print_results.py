import os
import pandas as pd
import numpy as np
import pickle
dir_path = os.path.dirname(os.path.realpath(__file__))

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)  # or 199

ep=["Frustration","Anxiety"]
# ep=["Boredom"]
eye_window='full'
log_window='full'
smote = False
if smote:
    results='/results_smote/'
else:
    results='/results/'

if len(ep)==1:
    type='/single'
    eps=ep[0]
else:
    type='/cooccur'
    eps=ep[0]+'_'+ep[1]

accuracies=pd.DataFrame()
datasets=['eye','log','both']
for threshold in ['3','4']:
    folder='/'+eye_window+'_'+log_window
    result_suffix='_'+eye_window+'_'+log_window+'_'+threshold
    for data in datasets:
        accs=[]
        accuracies['Model']=['Baseline','SVM','LR','RF','NN']
        for model in ['SVM','LR','RF','NN']:
            with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                res=pickle.load(handle)
            baseline_accuracy=res['baseline_accuracy']
            accs.append(res['mean_accuracy'])
        accuracies['Accuracy'+'_'+data+'_'+threshold]=([baseline_accuracy]+accs)
print(accuracies.T)
accuracies.T.to_excel(dir_path+'/temp_excel.ods')

def class_accuracy(smote,eye_window,log_window,ep,data,threshold,models):
    if smote:
        results='/results_smote/'
    else:
        results='/results/'
    if len(ep)==1:
        type='/single'
        eps=ep[0]
        classes = ['None',ep[0]]
    else:
        type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        classes = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'+eye_window+'_'+log_window
    result_suffix='_'+eye_window+'_'+log_window+'_'+threshold
    class_acc=pd.DataFrame()
    class_acc['Class']=classes
    for model in models:
        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
            res=pickle.load(handle)
        conf=res['mean_confusion_matrix']
        accs=[]
        base=[]
        for i in range(len(classes)):
            accs.append(conf[i][i]/conf[i].sum()*100)
            base.append(conf[i].sum()/conf.sum()*100)
        class_acc[model + ' Accuracy']=accs
    class_acc['Weightage']=base
    class_acc=class_acc.set_index(['Class'])
    return(class_acc)

ep=["Frustration","Boredom"]
# ep=["Curiosity"]
# ep=["Frustration","Anxiety"]
# ep=["Boredom"]
smote = False
# models=['RF','SVM','LR','NN']
models=['RF']
print(class_accuracy(smote,'15s','full',ep,'log','4',models))
print('\n')
