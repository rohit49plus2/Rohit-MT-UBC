import os
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
dir_path = os.path.dirname(os.path.realpath(__file__))

pd.set_option('display.max_columns', None)  # or 1000
pd.set_option('display.max_rows', None)  # or 1000
pd.set_option('display.max_colwidth', None)  # or 199

# ep=["Frustration","Anxiety"]
# # ep=["Boredom"]
# eye_window='full'
# log_window='full'
# smote = False
# if smote:
#     results='/results_smote/'
# else:
#     results='/results/'
#
# if len(ep)==1:
#     type='/single'
#     eps=ep[0]
# else:
#     type='/cooccur'
#     eps=ep[0]+'_'+ep[1]
#
# accuracies=pd.DataFrame()
# datasets=['eye','log','both']
# for threshold in ['3','4']:
#     folder='/'+eye_window+'_'+log_window
#     result_suffix='_'+eye_window+'_'+log_window+'_'+threshold
#     for data in datasets:
#         accs=[]
#         accuracies['Model']=['Baseline','SVM','LR','RF','NN']
#         for model in ['SVM','LR','RF','NN']:
#             with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
#                 res=pickle.load(handle)
#             baseline_accuracy=res['baseline_accuracy']
#             accs.append(res['mean_accuracy'])
#         accuracies['Accuracy'+'_'+data+'_'+threshold]=([baseline_accuracy]+accs)
# print(accuracies.T)
# accuracies.T.to_excel(dir_path+'/temp_excel.ods')

def class_accuracy(smote,eye_window,log_window,ep,data,threshold,models,usercv):
    if smote:
        results='/results_smote/'
    else:
        results='/results/'
    if len(ep)==1:
        type='/single'
        eps=ep[0]
        classes = ['None',ep[0]]
    else:
        if usercv:
            type='/cooccur-usercv'
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
    class_acc.insert(0, 'Distribution', base)
    class_acc=class_acc.set_index(['Class'])
    return(class_acc.round(2))

def accuracy(smote,eye_window,log_window,ep,data,threshold,models,usercv):
    if smote:
        results='/results_smote/'
    else:
        results='/results/'
    if len(ep)==1:
        type='/single'
        eps=ep[0]
    else:
        if usercv:
            type='/cooccur-usercv'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
    folder='/'+eye_window+'_'+log_window
    result_suffix='_'+eye_window+'_'+log_window+'_'+threshold
    acc=pd.DataFrame()
    acc['Model']=['Majority','Stratified']+models
    accs=[]
    for model in models:
        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
            res=pickle.load(handle)
        accs.append(res['mean_accuracy']*100)
        base1=res['majority_baseline_accuracy']*100
        base2=res['stratified_baseline_accuracy']*100
    accs=[base1,base2]+accs
    acc['Accuracy']=accs
    acc=acc.set_index(['Model'])
    return(acc.round(2))

def plot_accuracy(smote,eye_window,log_window,ep,data,threshold,models,usercv):
    if len(ep)==1:
        eps=ep[0]
    else:
        eps=ep[0]+' and '+ep[1]
    df=accuracy(smote,eye_window,log_window,ep,data,threshold,models,usercv)
    x=list(df.index)
    y=list(df.Accuracy)
    y_pos = np.arange(len(x))
    fig=plt.bar(y_pos,y,align='center',color='gray')
    plt.xticks(y_pos, x,fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('Accuracy',fontsize=15)
    axes = plt.gca()
    axes.set_ylim([0,100])
    plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
    if smote:
        smotes='\n with SMOTE '
    else:
        smotes='\n without SMOTE '
    if data=='log':
        title='Accuracy for ' + eps +'\n using log data with ' +log_window+ ' window' + ' and threshold set at ' + threshold + smotes
    elif data=='eye':
        title='Accuracy for ' + eps +'\n using gaze data with ' +eye_window+ ' window' + ' and threshold set at ' + threshold + smotes
    else:
        title='Accuracy for ' + eps +'\n using combined data with ' +eye_window+ ' gaze window and '+log_window+ ' log window ' + ' and threshold set at ' + threshold + smotes
    plt.title(title,fontsize=18)
    plt.axhline(y = y[0], color = 'black', linestyle = '--')
    for i in range(len(x)):
        plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
    plt.savefig(dir_path+'/../graphs/'+title+'.png',bbox_inches='tight')
    plt.show()

# ep=["Frustration","Boredom"]
# ep=["Curiosity"]
ep=["Curiosity","Anxiety"]
# ep=["Boredom"]

# smote = True
smote = False

models=['RF','SVM','LR','NN']
# models=['RF']

usercv=False
# usercv=True

print(class_accuracy(smote,'full','full',ep,'both','3',models,usercv).to_latex())
print('\n')
# print(accuracy(smote,'full','full',ep,'log','3',models))
# print('\n')
plot_accuracy(smote,'full','full',ep,'both','3',models,usercv)
