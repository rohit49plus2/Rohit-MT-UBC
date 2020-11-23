import os
import pandas as pd
import numpy as np
import pickle
dir_path = os.path.dirname(os.path.realpath(__file__))

ep=["Frustration","Anxiety"]
# ep=["Boredom"]
eye_window='full'
log_window='full'

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
            with open(dir_path+type+'/results/'+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                res=pickle.load(handle)
            baseline_accuracy=res['baseline_accuracy']
            accs.append(res['mean_accuracy'])
        accuracies['Accuracy'+'_'+data+'_'+threshold]=([baseline_accuracy]+accs)
print(accuracies.T)
accuracies.T.to_excel(dir_path+'/temp_excel.ods')

def class_accuracy(eye_window,log_window,ep,data,threshold,model):
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
    with open(dir_path+type+'/results/'+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
        res=pickle.load(handle)
    conf=res['mean_confusion_matrix']
    accs=[]
    class_acc=pd.DataFrame()
    for i in range(len(classes)):
        accs.append(conf[i][i]/conf[i].sum()*100)
    class_acc['Class']=classes
    class_acc['Accuracy']=accs
    class_acc=class_acc.set_index(['Class'])
    return(class_acc)

ep=["Frustration","Anxiety"]
# ep=["Frustration","Boredom"]
# ep=["Curiosity"]
# ep=["Boredom"]
print(class_accuracy('full','full',ep,'log','4','RF'))
print('\n')
