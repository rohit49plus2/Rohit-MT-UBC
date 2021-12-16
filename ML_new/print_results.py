import os
import pandas as pd
import numpy as np
import pickle
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
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
#     folder='/'
#     result_suffix='_'+threshold
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
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        classes = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'
    result_suffix='_'+threshold
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
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
    folder='/'
    result_suffix='_'+threshold
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
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        classes = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'
    result_suffix='_'+threshold
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

def manova_old_non_aoi(smote,eye_window,log_window,ep,threshold,models,usercv):
    data_types=['log','eye','both']
    if smote:
        results='/results_smote_non_aoi/'
    else:
        results='/results/'
    if len(ep)==1:
        type='/single'
        eps=ep[0]
        classes = ['None',ep[0]]
    else:
        if usercv:
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        classes = ['No_emotion',ep[0],ep[1],ep[0]+'_'+ ep[1]]
    folder='/'
    result_suffix='_'+threshold
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
                    for matrix in matrices:
                        row=[data,model]
                        row.append((np.trace(matrix))/matrix.sum()*100)
                        for i in range(4):
                            row.append(matrix[i][i]/matrix[i].sum()*100)
                        df.loc[len(df)] =row
    argument='Total'
    f=open(dir_path+'/stats_results_2016_non_aoi_only_' +eps+'.txt','w')
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

def plots_old_non_aoi(smote,eye_window,log_window,ep,threshold,models,usercv):
    data_types=['log','eye','both']
    data_types_titles=['Interaction','Gaze','Combined']
    if smote:
        results='/results_smote_non_aoi/'
    else:
        results='/results/'
    if len(ep)==1:
        type='/single'
        eps=ep[0]
        classes = ['None',ep[0]]
    else:
        if usercv:
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        eps_title=ep[0]+' x '+ep[1]
        classes = ['No_emotion',ep[0],ep[1],ep[0]+'_'+ ep[1]]
        classes_title = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'
    result_suffix='_'+threshold
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

def manova(smote,eye_window,log_window,ep,threshold,models,usercv,data_types,years=False,indiv=False):
    data_types_titles=['Interaction','Gaze','Combined'][:len(data_types)]
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
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        eps_title=ep[0]+' x '+ep[1]
        classes = ['No_emotion',ep[0],ep[1],ep[0]+'_'+ ep[1]]
        classes_title = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'
    result_suffix='_'+threshold
    if years:
        column_names=['Feature_Set','Model','Dataset','Total']+classes
    else:
        column_names=['Feature_Set','Model','Total']+classes
    df=pd.DataFrame(columns=column_names)
    for data in data_types:
        el=True
        for model in models:
            if years:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    if indiv and model!= 'Strat':
                    # if indiv:
                        row=[data,model + '_'+str(data),'2016 + 2014']
                    else:
                        row=[data,model,'2016 + 2014']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el=False
                else:
                    with open(dir_path+type+results[:-1]+'_2014/'+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    row=[data,model,'2014']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
            else:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el = False
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
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
        # if 'ENSEMBLE' not in model:
            for data in data_types:
                m = model + '_' + str(data)
                new_models.append(m)
        else:
            m = model
            new_models.append(m)
    if indiv:
        models = new_models
    # print(df)
    if years:
        from statsmodels.graphics.factorplots import interaction_plot as ip
        l =['Total']+classes
        for c in l:
            fig = ip(df['Model'],df['Dataset'],df[c])
            ax = plt.gca()
            ax.set_ylabel('Percentage Accuracies',fontsize=24)
            ax.set_xlabel('Model',fontsize=24)
            ax.legend(fontsize=15,loc='upper left')
            plt.yticks(fontsize=19)
            plt.xticks(fontsize=19)
            ax.set_title(eps_title+": Interaction Plot for "+c+" Accuracy on Model * Dataset",fontsize=24)
            plt.show()

            fig = ip(df['Feature_Set'],df['Dataset'],df[c])
            ax = plt.gca()
            ax.set_ylabel('Percentage Accuracies',fontsize=24)
            ax.set_xlabel('Feature Set',fontsize=24)
            ax.legend(fontsize=15,loc='upper left')
            plt.yticks(fontsize=19)
            plt.xticks(fontsize=19)
            ax.set_title(eps_title+": Interaction Plot for "+c+" Accuracy on Feature Set * Dataset",fontsize=24)
            plt.show()

    f=open(dir_path+'/stats_results_' +eps+'.txt','w')
    if len(data_types)>1 and years:
        argument='Total'
        for i in range(len(classes)):
            argument+=' + '+classes[i]
        if years:
            argument+=' ~ Model + Feature_Set + Dataset'
        else:
            argument+=' ~ Model + Feature_Set'
        print("MANOVA",argument,file=f)
        maov = MANOVA.from_formula(argument, data=df)
        print(maov.mv_test(),file=f)
        if years:
            argument='Total'
            argument+=' ~ Dataset'
            print("Univariate ANOVAs for ",argument,file=f)
            model = ols(argument, data=df).fit()
            print(sm.stats.anova_lm(model, typ=2),file=f)
            for i in range(len(classes)):
                argument=classes[i]
                argument+=' ~ Dataset'
                print("Univariate ANOVAs for ",argument,file=f)
                model = ols(argument, data=df).fit()
                print(sm.stats.anova_lm(model, typ=2),file=f)

            argument='Total'
            argument+=' ~ C(Model) + C(Dataset) + C(Model):C(Dataset)'
            print("2-way ANOVA", argument,file=f)
            model = ols(argument, data=df).fit()
            print(sm.stats.anova_lm(model, typ=2),file=f)
            for i in range(len(classes)):
                argument=classes[i]
                argument+=' ~ C(Model) + C(Dataset) + C(Model):C(Dataset)'
                print("2-way ANOVA", argument,file=f)
                model = ols(argument, data=df).fit()
                print(sm.stats.anova_lm(model, typ=2),file=f)

            argument='Total'
            argument+=' ~ C(Feature_Set) + C(Dataset) + C(Feature_Set):C(Dataset)'
            print("2-way ANOVA", argument,file=f)
            model = ols(argument, data=df).fit()
            print(sm.stats.anova_lm(model, typ=2),file=f)
            for i in range(len(classes)):
                argument=classes[i]
                argument+=' ~ C(Feature_Set) + C(Dataset) + C(Feature_Set):C(Dataset)'
                print("2-way ANOVA", argument,file=f)
                model = ols(argument, data=df).fit()
                print(sm.stats.anova_lm(model, typ=2),file=f)
    if len(data_types)>1:
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
    if len(data_types)>1:
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
    if years:
        year_types=['2014','2016 + 2014']
        print("\n\nMultiple T Test Analysis across Datasets for a particular Model",file=f)
        for m in range(len(models)):
            for i in range(len(year_types)):
                for j in range(i+1,len(year_types)):
                    print('\n','Model',models[m],year_types[i], 'vs',year_types[j],'\n',file=f)
                    t1=df[(df['Dataset']==year_types[i]) & (df['Model']==models[m])]['Total'].values.tolist()
                    t2=df[(df['Dataset']==year_types[j]) & (df['Model']==models[m])]['Total'].values.tolist()
                    print("Total Accuracy t test",file=f)
                    print(multipletests(ttest_ind(t1,t2)[1]),file=f)
                    for c in range(4):
                        print("Class - ", classes[c],"t test",file=f)
                        t1=df[(df['Dataset']==year_types[i]) & (df['Model']==models[m])][classes[c]].values.tolist()
                        t2=df[(df['Dataset']==year_types[j]) & (df['Model']==models[m])][classes[c]].values.tolist()
                        print(multipletests(ttest_ind(t1,t2)[1]),file=f)

        print("\n\nMultiple T Test Analysis across Datasets for a particular Feature_Set",file=f)
        for m in range(len(data_types)):
            for i in range(len(year_types)):
                for j in range(i+1,len(year_types)):
                    print('\n','Feature_Set',data_types[m],year_types[i], 'vs',year_types[j],'\n',file=f)
                    t1=df[(df['Dataset']==year_types[i]) & (df['Feature_Set']==data_types[m])]['Total'].values.tolist()
                    t2=df[(df['Dataset']==year_types[j]) & (df['Feature_Set']==data_types[m])]['Total'].values.tolist()
                    print("Total Accuracy t test",file=f)
                    print(multipletests(ttest_ind(t1,t2)[1]),file=f)
                    for c in range(4):
                        print("Class - ", classes[c],"t test",file=f)
                        t1=df[(df['Dataset']==year_types[i]) & (df['Feature_Set']==data_types[m])][classes[c]].values.tolist()
                        t2=df[(df['Dataset']==year_types[j]) & (df['Feature_Set']==data_types[m])][classes[c]].values.tolist()
                        print(multipletests(ttest_ind(t1,t2)[1]),file=f)


        print('\n\nInteraction T Test Analysis across Models and Datasets\n\n',file=f)
        for i in range(len(year_types)):
            for j in range(i+1,len(year_types)):
                print('\n',year_types[i], 'vs',year_types[j],'\n',file=f)
                t1=df[df['Dataset']==year_types[i]]['Total'].values.tolist()
                t2=df[df['Dataset']==year_types[j]]['Total'].values.tolist()
                print("Total Accuracy t test",file=f)
                print(multipletests(ttest_ind(t1,t2)[1]),file=f)
                for c in range(4):
                    print("Class - ", classes[c],"t test",file=f)
                    t1=df[df['Dataset']==year_types[i]][classes[c]].values.tolist()
                    t2=df[df['Dataset']==year_types[j]][classes[c]].values.tolist()
                    print(multipletests(ttest_ind(t1,t2)[1]),file=f)
    f.close()

def plots(smote,eye_window,log_window,ep,threshold,models,usercv,data_types,years=False,indiv=False):
    data_types_titles=['Interaction','Gaze','Combined'][:len(data_types)]
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
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        eps_title=ep[0]+' x '+ep[1]
        classes = ['No_emotion',ep[0],ep[1],ep[0]+'_'+ ep[1]]
        classes_title = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'
    result_suffix='_'+threshold
    if years:
        column_names=['Feature_Set','Model','Dataset','Total']+classes
    else:
        column_names=['Feature_Set','Model','Total']+classes
    df=pd.DataFrame(columns=column_names)
    for data in data_types:
        el=True
        for model in models:
            if years:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    if indiv and model!= 'Strat':
                    # if indiv:
                        row=[data,model + '_'+str(data),'2016 + 2014']
                    else:
                        row=[data,model,'2016 + 2014']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el=False
                else:
                    with open(dir_path+type+results[:-1]+'_2014/'+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    row=[data,model,'2014']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
            else:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el = False
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
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
        # if 'ENSEMBLE' not in model:
            for data in data_types:
                m = model + '_' + str(data)
                new_models.append(m)
        else:
            m = model
            new_models.append(m)
    if indiv:
        models = new_models
    # print(df)

    #accuracies across feature Sets
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

    if len(data_types)>1:
        #accuracies across classifiers
        y=[]
        for i in range(len(data_types)):
            t=df[df['Feature_Set']==data_types[i]]['Total'].values.tolist()
            y.append(np.mean(t).round(2))
        x=data_types_titles
        y_pos = np.arange(len(x))
        print(y,x)
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

    if years:
        year_types=['2014','2016 + 2014']
        #accuracies across datasets
        y=[]
        for i in range(len(year_types)):
            t=df[df['Dataset']==year_types[i]]['Total'].values.tolist()
            y.append(np.mean(t).round(2))
        x=year_types
        y_pos = np.arange(len(x))
        fig=plt.bar(y_pos,y,align='center',color='gray')
        plt.xticks(y_pos, x,fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel('Accuracy',fontsize=15)
        axes = plt.gca()
        axes.set_ylim([0,100])
        plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
        title="Mean Overall Accuracy Across Classifiers and Feature Sets For Emotion Pair " + eps_title
        plt.title(title,fontsize=18)
        # plt.axhline(y = y[0], color = 'black', linestyle = '--')
        for i in range(len(x)):
            plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
        # plt.show()
        table=pd.DataFrame(list(zip(x,y)),columns=['Dataset','Accuracy'])
        table=table.set_index('Dataset')
        print(table.to_latex())
        class_tables=[]
        for j in range(len(classes)):
            y=[]
            for i in range(len(year_types)):
                t=df[df['Dataset']==year_types[i]][classes[j]].values.tolist()
                y.append(np.mean(t).round(2))
            x=year_types
            y_pos = np.arange(len(x))
            fig=plt.bar(y_pos,y,align='center',color='gray')
            plt.xticks(y_pos, x,fontsize=15)
            plt.yticks(fontsize=15)
            plt.ylabel('Accuracy',fontsize=15)
            axes = plt.gca()
            axes.set_ylim([0,100])
            plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
            title="Mean Class Accuracy For " + classes_title[j]+ " Across Classifiers and Feature Sets For Emotion Pair " + eps_title
            plt.title(title,fontsize=18)
            # plt.axhline(y = y[0], color = 'black', linestyle = '--')
            for i in range(len(x)):
                plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
            # plt.show()
            table=pd.DataFrame(list(zip(x,y)),columns=['Dataset',classes_title[j]])
            table=table.set_index('Dataset')
            # print(table)
            class_tables.append(table)
        class_table=reduce(lambda x, y: pd.merge(x, y, on = 'Dataset'), class_tables)
        print(class_table.to_latex())

        ###interaction tables models * datasets
        for m in range(len(models)):
            y=[]
            for i in range(len(year_types)):
                t=df[(df['Dataset']==year_types[i])&(df['Model']==models[m])]['Total'].values.tolist()
                y.append(np.mean(t).round(2))
            x=year_types
            y_pos = np.arange(len(x))
            fig=plt.bar(y_pos,y,align='center',color='gray')
            plt.xticks(y_pos, x,fontsize=15)
            plt.yticks(fontsize=15)
            plt.ylabel('Accuracy',fontsize=15)
            axes = plt.gca()
            axes.set_ylim([0,100])
            plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
            title="Mean Overall Accuracy Across Across Feature Sets for model"+models[m]+ " For Emotion Pair " + eps_title
            plt.title(title,fontsize=18)
            # plt.axhline(y = y[0], color = 'black', linestyle = '--')
            for i in range(len(x)):
                plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
            # plt.show()
            table=pd.DataFrame(list(zip(x,y)),columns=['Dataset','Accuracy'])
            table=table.set_index('Dataset')
            print('Model: ',models[m])
            print(table.to_latex())
            class_tables=[]
            for j in range(len(classes)):
                y=[]
                for i in range(len(year_types)):
                    t=df[(df['Dataset']==year_types[i])&(df['Model']==models[m])][classes[j]].values.tolist()
                    y.append(np.mean(t).round(2))
                x=year_types
                y_pos = np.arange(len(x))
                fig=plt.bar(y_pos,y,align='center',color='gray')
                plt.xticks(y_pos, x,fontsize=15)
                plt.yticks(fontsize=15)
                plt.ylabel('Accuracy',fontsize=15)
                axes = plt.gca()
                axes.set_ylim([0,100])
                plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
                title="Mean Class Accuracy For " + classes_title[j]+ " Across Feature Sets for model"+models[m]+ " For Emotion Pair " + eps_title
                plt.title(title,fontsize=18)
                # plt.axhline(y = y[0], color = 'black', linestyle = '--')
                for i in range(len(x)):
                    plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
                # plt.show()
                table=pd.DataFrame(list(zip(x,y)),columns=['Dataset',classes_title[j]])
                table=table.set_index('Dataset')
                # print(table)
                class_tables.append(table)
            class_table=reduce(lambda x, y: pd.merge(x, y, on = 'Dataset'), class_tables)
            print('Model: ',models[m])
            print(class_table.to_latex())

        ###interaction tables feature sets * datasets
        for m in range(len(data_types)):
            y=[]
            for i in range(len(year_types)):
                t=df[(df['Dataset']==year_types[i])&(df['Feature_Set']==data_types[m])]['Total'].values.tolist()
                y.append(np.mean(t).round(2))
            x=year_types
            y_pos = np.arange(len(x))
            fig=plt.bar(y_pos,y,align='center',color='gray')
            plt.xticks(y_pos, x,fontsize=15)
            plt.yticks(fontsize=15)
            plt.ylabel('Accuracy',fontsize=15)
            axes = plt.gca()
            axes.set_ylim([0,100])
            plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
            title="Mean Overall Accuracy Across Across Models for Feature Set"+data_types[m]+ " For Emotion Pair " + eps_title
            plt.title(title,fontsize=18)
            # plt.axhline(y = y[0], color = 'black', linestyle = '--')
            for i in range(len(x)):
                plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
            # plt.show()
            table=pd.DataFrame(list(zip(x,y)),columns=['Dataset','Accuracy'])
            table=table.set_index('Dataset')
            print('Model: ',data_types[m])
            print(table.to_latex())
            class_tables=[]
            for j in range(len(classes)):
                y=[]
                for i in range(len(year_types)):
                    t=df[(df['Dataset']==year_types[i])&(df['Feature_Set']==data_types[m])][classes[j]].values.tolist()
                    y.append(np.mean(t).round(2))
                x=year_types
                y_pos = np.arange(len(x))
                fig=plt.bar(y_pos,y,align='center',color='gray')
                plt.xticks(y_pos, x,fontsize=15)
                plt.yticks(fontsize=15)
                plt.ylabel('Accuracy',fontsize=15)
                axes = plt.gca()
                axes.set_ylim([0,100])
                plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
                title="Mean Class Accuracy For " + classes_title[j]+ " Across Models for Feature Set"+data_types[m]+ " For Emotion Pair " + eps_title
                plt.title(title,fontsize=18)
                # plt.axhline(y = y[0], color = 'black', linestyle = '--')
                for i in range(len(x)):
                    plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
                # plt.show()
                table=pd.DataFrame(list(zip(x,y)),columns=['Dataset',classes_title[j]])
                table=table.set_index('Dataset')
                # print(table)
                class_tables.append(table)
            class_table=reduce(lambda x, y: pd.merge(x, y, on = 'Dataset'), class_tables)
            print('Model: ',data_types[m])
            print(class_table.to_latex())


def manova_non_aoi(smote,eye_window,log_window,ep,threshold,models,usercv,data_types,aoi=False,indiv=False):
    data_types_titles=['Interaction','Gaze','Combined'][:len(data_types)]
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
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        eps_title=ep[0]+' x '+ep[1]
        classes = ['No_emotion',ep[0],ep[1],ep[0]+'_'+ ep[1]]
        classes_title = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'
    result_suffix='_'+threshold
    if aoi:
        column_names=['Feature_Set','Model','AOI','Total']+classes
    else:
        column_names=['Feature_Set','Model','Total']+classes
    df=pd.DataFrame(columns=column_names)
    for data in data_types:
        el=True
        for model in models:
            if aoi:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    if indiv and model!= 'Strat':
                    # if indiv:
                        row=[data,model + '_'+str(data),'AOI']
                    else:
                        row=[data,model,'AOI']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el=False
                else:
                    with open(dir_path+type+results[:-1]+'_non_aoi/'+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    row=[data,model,'Non AOI']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
            else:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el = False
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
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
        # if 'ENSEMBLE' not in model:
            for data in data_types:
                m = model + '_' + str(data)
                new_models.append(m)
        else:
            m = model
            new_models.append(m)
    if indiv:
        models = new_models
    # print(df)
    if aoi:
        from statsmodels.graphics.factorplots import interaction_plot as ip
        l =['Total']+classes
        # for c in l:
        #     fig = ip(df['Model'],df['AOI'],df[c])
        #     ax = plt.gca()
        #     ax.set_ylabel('Percentage Accuracies',fontsize=24)
        #     ax.set_xlabel('Model',fontsize=24)
        #     ax.legend(fontsize=15,loc='upper left')
        #     plt.yticks(fontsize=19)
        #     plt.xticks(fontsize=19)
        #     ax.set_title(eps_title+": Interaction Plot for "+c+" Accuracy on Model * AOI",fontsize=24)
        #     plt.show()
        #
        #     fig = ip(df['Feature_Set'],df['AOI'],df[c])
        #     ax = plt.gca()
        #     ax.set_ylabel('Percentage Accuracies',fontsize=24)
        #     ax.set_xlabel('Feature Set',fontsize=24)
        #     ax.legend(fontsize=15,loc='upper left')
        #     plt.yticks(fontsize=19)
        #     plt.xticks(fontsize=19)
        #     ax.set_title(eps_title+": Interaction Plot for "+c+" Accuracy on Feature Set * AOI",fontsize=24)
        #     plt.show()

    f=open(dir_path+'/stats_results_non_aoi_' +eps+'.txt','w')
    if len(data_types)>1 and aoi:
        argument='Total'
        for i in range(len(classes)):
            argument+=' + '+classes[i]
        if aoi:
            argument+=' ~ Model + Feature_Set + AOI'
        else:
            argument+=' ~ Model + Feature_Set'
        print("MANOVA",argument,file=f)
        maov = MANOVA.from_formula(argument, data=df)
        print(maov.mv_test(),file=f)
        if aoi:
            argument='Total'
            argument+=' ~ AOI'
            print("Univariate ANOVAs for ",argument,file=f)
            model = ols(argument, data=df).fit()
            print(sm.stats.anova_lm(model, typ=2),file=f)
            for i in range(len(classes)):
                argument=classes[i]
                argument+=' ~ AOI'
                print("Univariate ANOVAs for ",argument,file=f)
                model = ols(argument, data=df).fit()
                print(sm.stats.anova_lm(model, typ=2),file=f)

            argument='Total'
            argument+=' ~ C(Model) + C(AOI) + C(Model):C(AOI)'
            print("2-way ANOVA", argument,file=f)
            model = ols(argument, data=df).fit()
            print(sm.stats.anova_lm(model, typ=2),file=f)
            for i in range(len(classes)):
                argument=classes[i]
                argument+=' ~ C(Model) + C(AOI) + C(Model):C(AOI)'
                print("2-way ANOVA", argument,file=f)
                model = ols(argument, data=df).fit()
                print(sm.stats.anova_lm(model, typ=2),file=f)

            argument='Total'
            argument+=' ~ C(Feature_Set) + C(AOI) + C(Feature_Set):C(AOI)'
            print("2-way ANOVA", argument,file=f)
            model = ols(argument, data=df).fit()
            print(sm.stats.anova_lm(model, typ=2),file=f)
            for i in range(len(classes)):
                argument=classes[i]
                argument+=' ~ C(Feature_Set) + C(AOI) + C(Feature_Set):C(AOI)'
                print("2-way ANOVA", argument,file=f)
                model = ols(argument, data=df).fit()
                print(sm.stats.anova_lm(model, typ=2),file=f)
    if len(data_types)>1:
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
    if len(data_types)>1:
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
    if aoi:
        year_types=['Non AOI','AOI']
        print("\n\nMultiple T Test Analysis across AOIs for a particular Model",file=f)
        for m in range(len(models)):
            for i in range(len(year_types)):
                for j in range(i+1,len(year_types)):
                    print('\n','Model',models[m],year_types[i], 'vs',year_types[j],'\n',file=f)
                    t1=df[(df['AOI']==year_types[i]) & (df['Model']==models[m])]['Total'].values.tolist()
                    t2=df[(df['AOI']==year_types[j]) & (df['Model']==models[m])]['Total'].values.tolist()
                    print("Total Accuracy t test",file=f)
                    print(multipletests(ttest_ind(t1,t2)[1]),file=f)
                    for c in range(4):
                        print("Class - ", classes[c],"t test",file=f)
                        t1=df[(df['AOI']==year_types[i]) & (df['Model']==models[m])][classes[c]].values.tolist()
                        t2=df[(df['AOI']==year_types[j]) & (df['Model']==models[m])][classes[c]].values.tolist()
                        print(multipletests(ttest_ind(t1,t2)[1]),file=f)

        print("\n\nMultiple T Test Analysis across AOIs for a particular Feature_Set",file=f)
        for m in range(len(data_types)):
            for i in range(len(year_types)):
                for j in range(i+1,len(year_types)):
                    print('\n','Feature_Set',data_types[m],year_types[i], 'vs',year_types[j],'\n',file=f)
                    t1=df[(df['AOI']==year_types[i]) & (df['Feature_Set']==data_types[m])]['Total'].values.tolist()
                    t2=df[(df['AOI']==year_types[j]) & (df['Feature_Set']==data_types[m])]['Total'].values.tolist()
                    print("Total Accuracy t test",file=f)
                    print(multipletests(ttest_ind(t1,t2)[1]),file=f)
                    for c in range(4):
                        print("Class - ", classes[c],"t test",file=f)
                        t1=df[(df['AOI']==year_types[i]) & (df['Feature_Set']==data_types[m])][classes[c]].values.tolist()
                        t2=df[(df['AOI']==year_types[j]) & (df['Feature_Set']==data_types[m])][classes[c]].values.tolist()
                        print(multipletests(ttest_ind(t1,t2)[1]),file=f)


        print('\n\nInteraction T Test Analysis across Models and AOIs\n\n',file=f)
        for i in range(len(year_types)):
            for j in range(i+1,len(year_types)):
                print('\n',year_types[i], 'vs',year_types[j],'\n',file=f)
                t1=df[df['AOI']==year_types[i]]['Total'].values.tolist()
                t2=df[df['AOI']==year_types[j]]['Total'].values.tolist()
                print("Total Accuracy t test",file=f)
                print(multipletests(ttest_ind(t1,t2)[1]),file=f)
                for c in range(4):
                    print("Class - ", classes[c],"t test",file=f)
                    t1=df[df['AOI']==year_types[i]][classes[c]].values.tolist()
                    t2=df[df['AOI']==year_types[j]][classes[c]].values.tolist()
                    print(multipletests(ttest_ind(t1,t2)[1]),file=f)
    f.close()


def plots_non_aoi(smote,eye_window,log_window,ep,threshold,models,usercv,data_types,aoi=True,indiv=False):
    data_types_titles=['Interaction','Gaze','Combined'][:len(data_types)]
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
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        eps_title=ep[0]+' x '+ep[1]
        classes = ['No_emotion',ep[0],ep[1],ep[0]+'_'+ ep[1]]
        classes_title = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'
    result_suffix='_'+threshold
    if aoi:
        column_names=['Feature_Set','Model','AOI','Total']+classes
    else:
        column_names=['Feature_Set','Model','Total']+classes
    df=pd.DataFrame(columns=column_names)
    for data in data_types:
        el=True
        for model in models:
            if aoi:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    if indiv and model!= 'Strat':
                    # if indiv:
                        row=[data,model + '_'+str(data),'AOI']
                    else:
                        row=[data,model,'AOI']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el=False
                else:
                    with open(dir_path+type+results[:-1]+'_non_aoi/'+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    row=[data,model,'Non AOI']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
            else:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el = False
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
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
        # if 'ENSEMBLE' not in model:
            for data in data_types:
                m = model + '_' + str(data)
                new_models.append(m)
        else:
            m = model
            new_models.append(m)
    if indiv:
        models = new_models
    # print(df)


    if aoi:
        year_types=['Non AOI','AOI']
        #accuracies across aoi vs non-aoi
        y=[]
        for i in range(len(year_types)):
            t=df[df['AOI']==year_types[i]]['Total'].values.tolist()
            y.append(np.mean(t).round(2))
        x=year_types
        y_pos = np.arange(len(x))
        fig=plt.bar(y_pos,y,align='center',color='gray')
        plt.xticks(y_pos, x,fontsize=15)
        plt.yticks(fontsize=15)
        plt.ylabel('Accuracy',fontsize=15)
        axes = plt.gca()
        axes.set_ylim([0,100])
        plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
        title="Mean Overall Accuracy Across Classifiers and Feature Sets For Emotion Pair " + eps_title
        plt.title(title,fontsize=18)
        # plt.axhline(y = y[0], color = 'black', linestyle = '--')
        for i in range(len(x)):
            plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
        # plt.show()
        table=pd.DataFrame(list(zip(x,y)),columns=['AOI','Accuracy'])
        table=table.set_index('AOI')
        print(table.to_latex())
        class_tables=[]
        for j in range(len(classes)):
            y=[]
            for i in range(len(year_types)):
                t=df[df['AOI']==year_types[i]][classes[j]].values.tolist()
                y.append(np.mean(t).round(2))
            x=year_types
            y_pos = np.arange(len(x))
            fig=plt.bar(y_pos,y,align='center',color='gray')
            plt.xticks(y_pos, x,fontsize=15)
            plt.yticks(fontsize=15)
            plt.ylabel('Accuracy',fontsize=15)
            axes = plt.gca()
            axes.set_ylim([0,100])
            plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
            title="Mean Class Accuracy For " + classes_title[j]+ " Across Classifiers and Feature Sets For Emotion Pair " + eps_title
            plt.title(title,fontsize=18)
            # plt.axhline(y = y[0], color = 'black', linestyle = '--')
            for i in range(len(x)):
                plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
            # plt.show()
            table=pd.DataFrame(list(zip(x,y)),columns=['AOI',classes_title[j]])
            table=table.set_index('AOI')
            # print(table)
            class_tables.append(table)
        class_table=reduce(lambda x, y: pd.merge(x, y, on = 'AOI'), class_tables)
        print(class_table.to_latex())

        ###interaction tables models * datasets
        for m in range(len(models)):
            y=[]
            for i in range(len(year_types)):
                t=df[(df['AOI']==year_types[i])&(df['Model']==models[m])]['Total'].values.tolist()
                y.append(np.mean(t).round(2))
            x=year_types
            y_pos = np.arange(len(x))
            fig=plt.bar(y_pos,y,align='center',color='gray')
            plt.xticks(y_pos, x,fontsize=15)
            plt.yticks(fontsize=15)
            plt.ylabel('Accuracy',fontsize=15)
            axes = plt.gca()
            axes.set_ylim([0,100])
            plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
            title="Mean Overall Accuracy Across Across Feature Sets for model"+models[m]+ " For Emotion Pair " + eps_title
            plt.title(title,fontsize=18)
            # plt.axhline(y = y[0], color = 'black', linestyle = '--')
            for i in range(len(x)):
                plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
            # plt.show()
            table=pd.DataFrame(list(zip(x,y)),columns=['AOI','Accuracy'])
            table=table.set_index('AOI')
            print('Model: ',models[m])
            print(table.to_latex())
            class_tables=[]
            for j in range(len(classes)):
                y=[]
                for i in range(len(year_types)):
                    t=df[(df['AOI']==year_types[i])&(df['Model']==models[m])][classes[j]].values.tolist()
                    y.append(np.mean(t).round(2))
                x=year_types
                y_pos = np.arange(len(x))
                fig=plt.bar(y_pos,y,align='center',color='gray')
                plt.xticks(y_pos, x,fontsize=15)
                plt.yticks(fontsize=15)
                plt.ylabel('Accuracy',fontsize=15)
                axes = plt.gca()
                axes.set_ylim([0,100])
                plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
                title="Mean Class Accuracy For " + classes_title[j]+ " Across Feature Sets for model"+models[m]+ " For Emotion Pair " + eps_title
                plt.title(title,fontsize=18)
                # plt.axhline(y = y[0], color = 'black', linestyle = '--')
                for i in range(len(x)):
                    plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
                # plt.show()
                table=pd.DataFrame(list(zip(x,y)),columns=['AOI',classes_title[j]])
                table=table.set_index('AOI')
                # print(table)
                class_tables.append(table)
            class_table=reduce(lambda x, y: pd.merge(x, y, on = 'AOI'), class_tables)
            print('Model: ',models[m])
            print(class_table.to_latex())

        ###interaction tables feature sets * datasets
        for m in range(len(data_types)):
            y=[]
            for i in range(len(year_types)):
                t=df[(df['AOI']==year_types[i])&(df['Feature_Set']==data_types[m])]['Total'].values.tolist()
                y.append(np.mean(t).round(2))
            x=year_types
            y_pos = np.arange(len(x))
            fig=plt.bar(y_pos,y,align='center',color='gray')
            plt.xticks(y_pos, x,fontsize=15)
            plt.yticks(fontsize=15)
            plt.ylabel('Accuracy',fontsize=15)
            axes = plt.gca()
            axes.set_ylim([0,100])
            plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
            title="Mean Overall Accuracy Across Across Models for Feature Set"+data_types[m]+ " For Emotion Pair " + eps_title
            plt.title(title,fontsize=18)
            # plt.axhline(y = y[0], color = 'black', linestyle = '--')
            for i in range(len(x)):
                plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
            # plt.show()
            table=pd.DataFrame(list(zip(x,y)),columns=['AOI','Accuracy'])
            table=table.set_index('AOI')
            print('Feature Set: ',data_types[m])
            print(table.to_latex())
            class_tables=[]
            for j in range(len(classes)):
                y=[]
                for i in range(len(year_types)):
                    t=df[(df['AOI']==year_types[i])&(df['Feature_Set']==data_types[m])][classes[j]].values.tolist()
                    y.append(np.mean(t).round(2))
                x=year_types
                y_pos = np.arange(len(x))
                fig=plt.bar(y_pos,y,align='center',color='gray')
                plt.xticks(y_pos, x,fontsize=15)
                plt.yticks(fontsize=15)
                plt.ylabel('Accuracy',fontsize=15)
                axes = plt.gca()
                axes.set_ylim([0,100])
                plt.setp(axes.get_xticklabels(), rotation=30, horizontalalignment='center')
                title="Mean Class Accuracy For " + classes_title[j]+ " Across Models for Feature Set"+data_types[m]+ " For Emotion Pair " + eps_title
                plt.title(title,fontsize=18)
                # plt.axhline(y = y[0], color = 'black', linestyle = '--')
                for i in range(len(x)):
                    plt.annotate(y[i], (-0.1 + i, y[i] +1),fontsize=15)
                # plt.show()
                table=pd.DataFrame(list(zip(x,y)),columns=['AOI',classes_title[j]])
                table=table.set_index('AOI')
                # print(table)
                class_tables.append(table)
            class_table=reduce(lambda x, y: pd.merge(x, y, on = 'AOI'), class_tables)
            print('Feature Set: ',data_types[m])
            print('this')
            print(class_table.to_latex())


def new_analysis(smote,eye_window,log_window,ep,threshold,models,usercv,data_types,aoi=True,indiv=False):
    data_types_titles=['Interaction','Gaze','Combined'][:len(data_types)]
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
            type='/cooccur_usercv_new'
        else:
            type='/cooccur'
        eps=ep[0]+'_'+ep[1]
        eps_title=ep[0]+' x '+ep[1]
        classes = ['No_emotion',ep[0],ep[1],ep[0]+'_'+ ep[1]]
        classes_title = ['None',ep[0],ep[1],ep[0]+' and '+ ep[1]]
    folder='/'
    result_suffix='_'+threshold
    if aoi:
        column_names=['Feature_Set','Model','Dataset','Total']+classes
    else:
        column_names=['Feature_Set','Model','Total']+classes
    df=pd.DataFrame(columns=column_names)
    for data in data_types:
        el=True
        for model in models:
            if aoi:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    if indiv and model!= 'Strat':
                    # if indiv:
                        row=[data,model + '_'+str(data),'Combined AOI']
                    else:
                        row=[data,model,'Combined AOI']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                else:
                    with open(dir_path+type+results[:-1]+'_non_aoi/'+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    row=[data,model,'Combined Non AOI']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el=False
                else:
                    with open(dir_path+type+results[:-1]+'_2014/'+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
                # print(len(res['confusion_matrices']))
                matrices=res['confusion_matrices']
                for matrix in matrices:
                    row=[data,model,'2014']
                    row.append((np.trace(matrix))/matrix.sum()*100)
                    for i in range(4):
                        row.append(matrix[i][i]/matrix[i].sum()*100)
                    df.loc[len(df)] =row
            else:
                if 'ENSEMBLE' in model :
                    if el:
                        with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'.pickle', 'rb') as handle:
                            res=pickle.load(handle)
                        el = False
                else:
                    with open(dir_path+type+results+eps+'/'+folder+'/'+model+result_suffix+'_'+eps+'_'+data+'.pickle', 'rb') as handle:
                        res=pickle.load(handle)
                    if indiv and model!= 'Strat':
                    # if indiv:
                        model = model + '_' + str(data)#toggle this on for individual figures and the below toggle
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
        # if 'ENSEMBLE' not in model:
            for data in data_types:
                m = model + '_' + str(data)
                new_models.append(m)
        else:
            m = model
            new_models.append(m)
    if indiv:
        models = new_models
    # print(df)
    best_dfs={}
    class_feature_sets={}
    if ep==['Frustration','Boredom']:
        class_feature_sets={'Total':['log','eye','eye'],
                            classes[0]:['both','eye','eye'],
                            classes[1]:['eye','eye','eye'],
                            classes[2]:['log','log','log'],
                            classes[3]:['log','log','both']
                            }
    else:
        class_feature_sets={'Total':['eye','eye','eye'],
                            classes[0]:['eye','eye','log'],
                            classes[1]:['eye','eye','eye'],
                            classes[2]:['log','log','log'],
                            classes[3]:['both','both','both']
                            }
        # print(class_feature_sets)
    for x in ['Total']+classes:
        slice0=(df['Dataset']=='2014') & (df['Feature_Set']==class_feature_sets[x][0])
        slice1=(df['Dataset']=='Combined AOI') & (df['Feature_Set']==class_feature_sets[x][1])
        slice2=(df['Dataset']=='Combined Non AOI') & (df['Feature_Set']==class_feature_sets[x][2])
        slices=slice0+slice1+slice2
        best_dfs[x]=df.loc[slices,['Feature_Set','Model','Dataset',x]]
        print(x)
        print(len(best_dfs[x]))
        best_dfs[x]['Best_combination']=best_dfs[x]['Dataset']+'_'+best_dfs[x]['Feature_Set']
        # print(best_dfs[x])
    if ep==['Frustration','Boredom']:
        labels=['Acc_Overall','Acc_None','Acc_Frus','Acc_Bore','Acc_Both']
    else:
        labels=['Acc_Overall','Acc_None','Acc_Curi','Acc_Anxi','Acc_Both']
    original=[]
    original_pattern=[]
    combined_aoi=[]
    combined_aoi_pattern=[]
    combined_non_aoi=[]
    combined_non_aoi_pattern=[]
    for x in ['Total']+classes:
        df = best_dfs[x]

        ori = df[df['Dataset']=='2014']
        f1=np.unique(ori['Feature_Set'])
        assert len(f1)==1
        original.append(round(np.mean(ori[x]),2))
        original_pattern.append(f1[0])

        comb_aoi = df[df['Dataset']=='Combined AOI']
        f2=np.unique(comb_aoi['Feature_Set'])
        assert len(f2)==1
        combined_aoi.append(round(np.mean(comb_aoi[x]),2))
        combined_aoi_pattern.append(f2[0])

        comb_non_aoi = df[df['Dataset']=='Combined Non AOI']
        f3=np.unique(comb_non_aoi['Feature_Set'])
        assert len(f3)==1
        combined_non_aoi.append(round(np.mean(comb_non_aoi[x]),2))
        combined_non_aoi_pattern.append(f3[0])

        t1=ori[x].values.tolist()
        t2=comb_aoi[x].values.tolist()
        t3=comb_non_aoi[x].values.tolist()
        argument= x+' ~ Dataset'
        print("1-way ANOVA", argument)
        model = ols(argument, data=best_dfs[x]).fit()
        print(sm.stats.anova_lm(model, typ=2))
        print(x+" Accuracy t tests")
        # print(ttest_ind(t1,t3)[1])
        print(multipletests([ttest_ind(t1,t2)[1],ttest_ind(t1,t3)[1],ttest_ind(t2,t3)[1]],alpha=0.05))

    # print(original)
    # print(original_pattern)
    def pat(x):
        if x=='log':
            return '/'
        elif x=='eye':
            return '.'
        elif x=='both':
            return '*'
    original_pattern=[pat(x) for x in original_pattern]
    combined_aoi_pattern=[pat(x) for x in combined_aoi_pattern]
    combined_non_aoi_pattern=[pat(x) for x in combined_non_aoi_pattern]

    fig, ax = plt.subplots()
    x = np.arange(len(labels))  # the label locations
    width=0.3
    rects1 = ax.bar(x - width, original, width, label='2014',color='#F4D4D4',hatch=original_pattern)
    rects2 = ax.bar(x , combined_aoi, width, label='Combined AOI',color='#F1A879',hatch=combined_aoi_pattern)
    rects3 = ax.bar(x + width, combined_non_aoi, width, label='Combined Non AOI',color='#CAB8C8',hatch=combined_non_aoi_pattern)

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

    # Add some text for labels, title and custom x-axis tick labels, etc.
    ax.set_ylabel('Percentage Accuracies',fontsize=24)
    ax.set_title(ep[0]+' x ' +ep[1],fontsize=24)
    ax.set_xticks(x)
    ax.set_xticklabels(labels)

    legend_elements=[]
    for label,color in {'2014':'#F4D4D4','Combined AOI':'#F1A879','Combined Non AOI':'#CAB8C8'}.items():
        legend_elements.append((mpatches.Patch(color=color), label))
    for label,hatch in {'log':'/','eye':'.','both':'*'}.items():
        legend_elements.append((mpatches.Patch(facecolor='white',hatch=hatch), label))
    ax.legend(*zip(*legend_elements),fontsize=15, loc=2)

    ax.set_ylim([0,60])
    plt.yticks(fontsize=19)
    plt.xticks(fontsize=19)
    fig.tight_layout()
    plt.grid(which='both',axis='y',color='gray', linestyle='--', linewidth=.5)
    plt.minorticks_on()
    plt.show()

# ep=["Frustration","Boredom"]
# ep=["Curiosity"]
ep=["Curiosity","Anxiety"]
# ep=["Boredom"]

smote = True
# smote = False
data_types=['log','eye','both']
# data_types=['eye']
# data_types=['log','eye']

models=['Strat','LR','RF','SVM']
# models=['RF','SVM']
# models+=['ENSEMBLE2']

# usercv=False
usercv=True

# print(class_accuracy(smote,'','',ep,'eye','3',models,usercv).to_latex())
# print('\n')
# print(accuracy(smote,'','',ep,'eye','3',models,usercv))
# print('\n')
# plot_accuracy(smote,'','',ep,'eye','3',models,usercv)
# anova_class(smote,'','',ep,'both','3',models,usercv)
# manova_old_non_aoi(smote,'','',ep,'3',models,usercv)
# plots_old_non_aoi(smote,'','',ep,'3',models,usercv)
# manova(smote,'','',ep,'3',models,usercv,data_types,True,False)
# plots(smote,'','',ep,'3',models,usercv,data_types,False,True)
# manova_non_aoi(smote,'','',ep,'3',models,usercv,data_types,True,False)
# plots_non_aoi(smote,'','',ep,'3',models,usercv,data_types,True,False)
new_analysis(smote,'','',ep,'3',models,usercv,data_types,True,False)
