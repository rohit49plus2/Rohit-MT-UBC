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
#     type='/cooccur'u
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
        if model == 'ENSEMBLE2':
            with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                res=pickle.load(handle)
        else:
            with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                res=pickle.load(handle)
        conf=res['mean_confusion_matrix']
        accs=[]
        base=[]
        for i in range(len(classes)):
            accs.append(conf[i][i]/conf[i].sum()*100)
            base.append(conf[i].sum()/conf.sum()*100)
        class_acc[model]=accs
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
    acc['Model']=models
    accs=[]
    for model in models:
        if model == 'ENSEMBLE2':
            with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                res=pickle.load(handle)
        else:
            with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                res=pickle.load(handle)
        accs.append(res['mean_accuracy']*100)
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
    plt.show()

def anova_class(smote,eye_window,log_window,ep,data,threshold,models,usercv):
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
    cf=pd.DataFrame()
    for model in models:
        if model == 'ENSEMBLE2':
            with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                res=pickle.load(handle)
        else:
            with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                res=pickle.load(handle)
        # print(len(res['confusion_matrices']))
        cf[model]=res['confusion_matrices']

    anova_results=[]
    class_accs=[]
    for i in range(4):
        class_accs.append([])
        for model in models:
            accs=[]
            for matrix in cf[model]:
                accs.append(matrix[i][i]/matrix[i].sum()*100)
            class_accs[i].append(accs)
        print("Class - ", classes[i])
        print(f_oneway(*class_accs[i]))
    total_accs=[]
    for model in models:
        accs = []
        for matrix in cf[model]:
            accs.append((np.trace(matrix))/matrix.sum()*100)
        total_accs.append(accs)
    print("Total Accuracy")
    print(f_oneway(*total_accs))

    print("Multiple T Test Analysis")
    for i in range(len(models)):
        for j in range(i+1,len(models)):
            print(models[i], 'vs',models[j])
            for c in range(4):
                print("Class - ", classes[c],"t tests")
                print(multipletests(ttest_ind(class_accs[c][i],class_accs[c][j])[1]))
            print("Total Accuracy t tests")
            print(multipletests(ttest_ind(total_accs[i],total_accs[j])[1]))


def manova(smote,eye_window,log_window,ep,threshold,models,usercv):
    data_types=['log','eye','both']
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
        classes = ['No_emotion',ep[0],ep[1],ep[0]+'-x-'+ ep[1]]
    folder='/'+eye_window+'_'+log_window
    result_suffix='_'+eye_window+'_'+log_window+'_'+threshold
    column_names=['Feature_Set','Model','Total']+classes
    df=pd.DataFrame(columns=column_names)
    for model in models:
        if 'ENSEMBLE' in model:
            for data in data_types:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    # print(len(res['confusion_matrices']))
                    matrices=res['confusion_matrices']
                    for matrix in matrices:
                        row=[data,model]
                        row.append((np.trace(matrix))/matrix.sum()*100)
                        for i in range(4):
                            row.append(matrix[i][i]/matrix[i].sum()*100)
                        df.loc[len(df)] =row
        else:
            for data in data_types:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    # print(len(res['confusion_matrices']))
                    matrices=res['confusion_matrices']
                    # if model != 'Strat':
                    #     # model_name = model + '_' + str(data)
                    #     pass
                    # else:
                    model_name = model
                    for matrix in matrices:
                        row=[data,model_name]
                        row.append((np.trace(matrix))/matrix.sum()*100)
                        for i in range(4):
                            row.append(matrix[i][i]/matrix[i].sum()*100)
                        df.loc[len(df)] =row

    new_models=[]
    for model in models:
        if 'ENSEMBLE' not in model and model != 'Strat':
            for data in data_types:
                m = model + '_' + str(data)
                new_models.append(m)
        else:
            m = model
            new_models.append(m)
    # models = new_models
    argument='Total'
    f=open(dir_path+'/stats_results_' +eps+'.txt','w')
    for i in range(len(classes)):
        argument+=' + '+classes[i]
    argument+=' ~ Model + Feature_Set'
    print("MANOVA",argument,file=f)
    maov = MANOVA.from_formula(argument, data=df)
    print(maov.mv_test(),file=f)
    argument='Total'
    argument+=' ~ C(Model) + C(Feature_Set) + C(Model):C(Feature_Set)'
    print("2-way ANOVA", argument,file=f)
    model = ols(argument, data=df).fit()
    print(sm.stats.anova_lm(model, typ=2),file=f)
    for i in range(len(classes)):
        argument=classes[i]
        argument+=' ~ C(Model) + C(Feature_Set) + C(Model):C(Feature_Set)'
        print("2-way ANOVA", argument,file=f)
        model = ols(argument, data=df).fit()
        print(sm.stats.anova_lm(model, typ=2),file=f)
    print("\n\nMultiple T Test Analysis across Models",file=f)
    for i in range(len(models)):
        for j in range(i+1,len(models)):
            print('\n',models[i], 'vs',models[j],'\n',file=f)
            t1=df[df['Model']==models[i]]['Total'].values.tolist()
            t2=df[df['Model']==models[j]]['Total'].values.tolist()
            print("Total Accuracy t test",file=f)
            print(multipletests(ttest_ind(t1,t2)[1]),file=f)
            for c in range(4):
                print("Class - ", classes[c],"t test",file=f)
                t1=df[df['Model']==models[i]][classes[c]].values.tolist()
                t2=df[df['Model']==models[j]][classes[c]].values.tolist()
                print(multipletests(ttest_ind(t1,t2)[1]),file=f)
    print("\n\nMultiple T Test Analysis across Feature Sets",file=f)
    for i in range(len(data_types)):
        for j in range(i+1,len(data_types)):
            print('\n',data_types[i], 'vs',data_types[j],'\n',file=f)
            t1=df[df['Feature_Set']==data_types[i]]['Total'].values.tolist()
            t2=df[df['Feature_Set']==data_types[j]]['Total'].values.tolist()
            print("Total Accuracy t test",file=f)
            print(multipletests(ttest_ind(t1,t2)[1]),file=f)
            for c in range(4):
                print("Class - ", classes[c],"t test",file=f)
                t1=df[df['Feature_Set']==data_types[i]][classes[c]].values.tolist()
                t2=df[df['Feature_Set']==data_types[j]][classes[c]].values.tolist()
                print(multipletests(ttest_ind(t1,t2)[1]),file=f)
    f.close()

def plots(smote,eye_window,log_window,ep,threshold,models,usercv):
    data_types=['log','eye','both']
    data_types_titles=['Interaction','Gaze','Combined']
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
        eps_title=ep[0]+' x '+ep[1]
        classes = ['No_emotion',ep[0],ep[1],ep[0]+'-x-'+ ep[1]]
        classes_title = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'+eye_window+'_'+log_window
    result_suffix='_'+eye_window+'_'+log_window+'_'+threshold
    column_names=['Feature_Set','Model','Total']+classes
    df=pd.DataFrame(columns=column_names)
    for data in data_types:
        for model in models:
            if 'ENSEMBLE' in model :
                with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                    res=pickle.load(handle)
            else:
                with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                    res=pickle.load(handle)
                # if model != 'Strat':
                #     model = model + '_' + str(data)
            # print(len(res['confusion_matrices']))
            matrices=res['confusion_matrices']
            for matrix in matrices:
                row=[data,model]
                row.append((np.trace(matrix))/matrix.sum()*100)
                for i in range(4):
                    row.append(matrix[i][i]/matrix[i].sum()*100)
                df.loc[len(df)] =row
    new_models=[]
    for model in models:
        if 'ENSEMBLE' not in model and model != 'Strat':
            for data in data_types:
                m = model + '_' + str(data)
                new_models.append(m)
        else:
            m = model
            new_models.append(m)
    # models = new_models
    # accuracies across feature Sets
    y=[]
    for i in range(len(models)):
        t=df[df['Model']==models[i]]['Total'].values.tolist()
        y.append(np.mean(t).round(2))
    x=models
    y_pos = np.arange(len(x))
    fig=plt.bar(y_pos,y,align='center',color='gray')
    plt.xticks(y_pos, x,fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('Accuracy',fontsize=15)
    axes = plt.gca()
    axes.set_ylim([0,100])
    plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
    title="Mean Overall Accuracy Across Feature Sets For Emotion Pair " + eps_title
    plt.title(title,fontsize=18)
    plt.axhline(y = y[0], color = 'black', linestyle = '--')
    for i in range(len(x)):
        plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
    plt.show()
    table=pd.DataFrame(list(zip(x,y)),columns=['Model','Accuracy'])
    table=table.set_index('Model')
    print(table.to_latex())
    class_tables=[]
    for j in range(len(classes)):
        y=[]
        for i in range(len(models)):
            t=df[df['Model']==models[i]][classes[j]].values.tolist()
            y.append(np.mean(t).round(2))
        x=models
        y_pos = np.arange(len(x))
        fig=plt.bar(y_pos,y,align='center',color='gray')
        plt.xticks(y_pos, x,fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel('Accuracy',fontsize=15)
        axes = plt.gca()
        axes.set_ylim([0,100])
        plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
        title="Mean Class Accuracy For " + classes_title[j]+ " Across Feature Sets For Emotion Pair " + eps_title
        plt.title(title,fontsize=18)
        plt.axhline(y = y[0], color = 'black', linestyle = '--')
        for i in range(len(x)):
            plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
        plt.show()
        table=pd.DataFrame(list(zip(x,y)),columns=['Model',classes_title[j]])
        table=table.set_index('Model')
        # print(table)
        class_tables.append(table)
    class_table=reduce(lambda x, y: pd.merge(x, y, on = 'Model'), class_tables)
    print(class_table.to_latex())


    #accuracies across classifiers
    y=[]
    for i in range(len(data_types)):
        t=df[df['Feature_Set']==data_types[i]]['Total'].values.tolist()
        y.append(np.mean(t).round(2))
    x=data_types_titles
    y_pos = np.arange(len(x))
    fig=plt.bar(y_pos,y,align='center',color='gray')
    plt.xticks(y_pos, x,fontsize=15)
    plt.yticks(fontsize=15)
    plt.ylabel('Accuracy',fontsize=15)
    axes = plt.gca()
    axes.set_ylim([0,100])
    plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
    title="Mean Overall Accuracy Across Classifiers For Emotion Pair " + eps_title
    plt.title(title,fontsize=18)
    # plt.axhline(y = y[0], color = 'black', linestyle = '--')
    for i in range(len(x)):
        plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
    plt.show()
    table=pd.DataFrame(list(zip(x,y)),columns=['Feature Set','Accuracy'])
    table=table.set_index('Feature Set')
    print(table.to_latex())
    class_tables=[]
    for j in range(len(classes)):
        y=[]
        for i in range(len(data_types)):
            t=df[df['Feature_Set']==data_types[i]][classes[j]].values.tolist()
            y.append(np.mean(t).round(2))
        x=data_types_titles
        y_pos = np.arange(len(x))
        fig=plt.bar(y_pos,y,align='center',color='gray')
        plt.xticks(y_pos, x,fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel('Accuracy',fontsize=15)
        axes = plt.gca()
        axes.set_ylim([0,100])
        plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
        title="Mean Class Accuracy For " + classes_title[j]+ " Across Classifiers For Emotion Pair " + eps_title
        plt.title(title,fontsize=18)
        # plt.axhline(y = y[0], color = 'black', linestyle = '--')
        for i in range(len(x)):
            plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
        plt.show()
        table=pd.DataFrame(list(zip(x,y)),columns=['Feature Set',classes_title[j]])
        table=table.set_index('Feature Set')
        # print(table)
        class_tables.append(table)
    class_table=reduce(lambda x, y: pd.merge(x, y, on = 'Feature Set'), class_tables)
    print(class_table.to_latex())






# ep=["Frustration","Boredom"]
# ep=["Curiosity"]
ep=["Curiosity","Anxiety"]
# ep=["Boredom"]

smote = True
# smote = False

# models=['Strat','RF','LR']
models=['Strat','RF','LR','SVM']
# models=['Strat','RF','LR','ENSEMBLE2']
# models=['ENSEMBLE2']

# usercv=False
usercv=True

# print(class_accuracy(smote,'full','full',ep,'eye','3',models,usercv).to_latex())
# print('\n')
# print(accuracy(smote,'full','full',ep,'eye','3',models,usercv))
# print('\n')
# plot_accuracy(smote,'full','full',ep,'eye','3',models,usercv)
# anova_class(smote,'full','full',ep,'both','3',models,usercv)
manova(smote,'full','full',ep,'3',models,usercv)
# plots(smote,'full','full',ep,'3',models,usercv)
