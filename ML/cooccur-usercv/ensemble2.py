from load_data import *
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import r2_score
from sklearn.preprocessing import normalize
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
import random
from collections import Counter, defaultdict

def correlation(dataset, threshold):
    col_corr = set() # Set of all the names of deleted columns
    corr_matrix = dataset.corr()
    for i in range(len(corr_matrix.columns)):
        for j in range(i):
            if (corr_matrix.iloc[i, j] >= threshold) and (corr_matrix.columns[j] not in col_corr):
                colname = corr_matrix.columns[i] # getting the name of column
                col_corr.add(colname)
                if colname in dataset.columns:
                    del dataset[colname] # deleting the column from the dataset

    return(dataset)

def stratified_group_k_fold(X, y, groups, k, seed=None):
    labels_num = np.max(y) + 1
    y_counts_per_group = defaultdict(lambda: np.zeros(labels_num))
    y_distr = Counter()
    for label, g in zip(y, groups):
        y_counts_per_group[g][label] += 1
        y_distr[label] += 1

    y_counts_per_fold = defaultdict(lambda: np.zeros(labels_num))
    groups_per_fold = defaultdict(set)

    def eval_y_counts_per_fold(y_counts, fold):
        y_counts_per_fold[fold] += y_counts
        std_per_label = []
        for label in range(labels_num):
            label_std = np.std([y_counts_per_fold[i][label] / y_distr[label] for i in range(k)])
            std_per_label.append(label_std)
        y_counts_per_fold[fold] -= y_counts
        return np.mean(std_per_label)

    groups_and_y_counts = list(y_counts_per_group.items())
    random.Random(seed).shuffle(groups_and_y_counts)

    for g, y_counts in sorted(groups_and_y_counts, key=lambda x: -np.std(x[1])):
        best_fold = None
        min_eval = None
        for i in range(k):
            fold_eval = eval_y_counts_per_fold(y_counts, i)
            if min_eval is None or fold_eval < min_eval:
                min_eval = fold_eval
                best_fold = i
        y_counts_per_fold[best_fold] += y_counts
        groups_per_fold[best_fold].add(g)

    all_groups = set(groups)
    for i in range(k):
        train_groups = all_groups - groups_per_fold[i]
        test_groups = groups_per_fold[i]

        train_indices = [i for i, g in enumerate(groups) if g in train_groups]
        test_indices = [i for i, g in enumerate(groups) if g in test_groups]

        yield train_indices, test_indices

# datasets=['eye','log','both']
# for data in datasets:
if not os.path.exists(dir_path+'/results_smote/'+ep[0]+'_'+ep[1]+'/'+folder):
    os.makedirs(dir_path+'/results_smote/'+ep[0]+'_'+ep[1]+'/'+folder)
f = open(dir_path+'/results_smote/'+ep[0]+'_'+ep[1]+'/'+folder+'/ENSEMBLE2'+result_suffix+'_'+ep[0]+'_'+ep[1]+'.txt', 'w')

X=eye_and_log.drop(emotions,axis=1)
ids=list(X['key'])
ids=np.array([id[0] for id in ids])
Xlog=X[X.columns[-57:]]
Xeye=X[X.columns[:-57]]
y_temp=eye_and_log[ep]
Xlog = Xlog.select_dtypes(include=numerics)
Xlog=Xlog.to_numpy()
Xlog=normalize(Xlog)
Xeye = Xeye.select_dtypes(include=numerics)
Xeye=Xeye.to_numpy()
Xeye=normalize(Xeye)
from sklearn.decomposition import IncrementalPCA
from sklearn.decomposition import PCA
y_temp=y_temp.to_numpy()
y=[]
for i in range(len(y_temp)):
    if np.array_equal(y_temp[i],np.array([0,0])):
        y.append(0)
    elif np.array_equal(y_temp[i],np.array([1,0])):
        y.append(1)
    elif np.array_equal(y_temp[i],np.array([0,1])):
        y.append(2)
    elif np.array_equal(y_temp[i],np.array([1,1])):
        y.append(3)

y=np.array(y)

model = DummyClassifier(strategy="most_frequent")
model.fit(X, y)
y_pred = model.predict(X)
accuracy1 = accuracy_score(y, y_pred)
print('Majority Class Base Accuracy',accuracy1,file=f)

model = DummyClassifier(strategy="stratified")
model.fit(X, y)
y_pred = model.predict(X)
accuracy2 = accuracy_score(y, y_pred)
print('Stratified Class Base Accuracy',accuracy2,file=f)

from imblearn.over_sampling import SMOTE
from imblearn.under_sampling import RandomUnderSampler
from imblearn.pipeline import Pipeline

# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=2)
over = SMOTE(sampling_strategy='all',random_state=2)
under = RandomUnderSampler(random_state=2)
# steps = [('o', over), ('u', under)]
steps = [('o', over)]
pipeline = Pipeline(steps=steps)
parameters_lr = {'n_estimators':range(1, 2, 3)}
logr = LogisticRegression()
lr = AdaBoostClassifier(logr)

parameters_rf = {'max_depth':[1,2,3,4,5],
'n_estimators': [10,50,100],
'max_features': [1,2,3,4,5]
}
rf = RandomForestClassifier()

conf_matrix_list_of_arrays = []
scores=[]
for i in range(10):
    for fold_ind, (train_index, test_index) in enumerate(stratified_group_k_fold(Xlog, y, ids, k=8)):
        print("Fold ", fold_ind)
        Xlog_train, Xlog_test = Xlog[train_index], Xlog[test_index]
        Xeye_train, Xeye_test = Xeye[train_index], Xeye[test_index]
        y_train, y_test = y[train_index], y[test_index]
        train_groups, test_groups = ids[train_index], ids[test_index]

        # print(data,X_train.shape)
        pca = PCA(n_components=0.999)
        pca.fit(Xlog_train)
        Xlog_train=pca.transform(Xlog_train)
        Xlog_test=pca.transform(Xlog_test)
        Xlog_train, ylog_train = pipeline.fit_resample(Xlog_train, y_train)#Smote
        # print(data,X_train.shape)

        pca = PCA(n_components=0.999)
        pca.fit(Xeye_train)
        Xeye_train=pca.transform(Xeye_train)
        Xeye_test=pca.transform(Xeye_test)

        Xeye_train, yeye_train = pipeline.fit_resample(Xeye_train, y_train)#Smote

        clf1 = GridSearchCV(rf, parameters_rf,cv=5, n_jobs=4)
        clf1.fit(Xlog_train, ylog_train)
        y_pred = clf1.best_estimator_.predict(Xlog_train)
        m1=confusion_matrix(ylog_train, y_pred)
        pred1 = clf1.predict_proba(Xlog_test)

        clf2 = GridSearchCV(lr, parameters_lr,cv=5, n_jobs=4)
        clf2.fit(Xlog_train, ylog_train)
        y_pred = clf2.best_estimator_.predict(Xlog_train)
        m2=confusion_matrix(ylog_train, y_pred)
        pred2 = clf2.predict_proba(Xlog_test)

        clf3 = GridSearchCV(rf, parameters_rf,cv=5, n_jobs=4)
        clf3.fit(Xeye_train, yeye_train)
        y_pred = clf3.best_estimator_.predict(Xeye_train)
        m3=confusion_matrix(yeye_train, y_pred)
        pred3 = clf3.predict_proba(Xeye_test)

        clf4 = GridSearchCV(lr, parameters_lr,cv=5, n_jobs=4)
        clf4.fit(Xeye_train, yeye_train)
        y_pred = clf4.best_estimator_.predict(Xeye_train)
        m4=confusion_matrix(yeye_train, y_pred)
        pred4 = clf4.predict_proba(Xeye_test)

        c11=m1[0][0]/m1[0].sum()
        c12=m1[1][1]/m1[1].sum()
        c13=m1[2][2]/m1[2].sum()
        c14=m1[3][3]/m1[3].sum()
        c21=m2[0][0]/m2[0].sum()
        c22=m2[1][1]/m2[1].sum()
        c23=m2[2][2]/m2[2].sum()
        c24=m2[3][3]/m2[3].sum()
        c31=m3[0][0]/m3[0].sum()
        c32=m3[1][1]/m3[1].sum()
        c33=m3[2][2]/m3[2].sum()
        c34=m3[3][3]/m3[3].sum()
        c41=m4[0][0]/m4[0].sum()
        c42=m4[1][1]/m4[1].sum()
        c43=m4[2][2]/m4[2].sum()
        c44=m4[3][3]/m4[3].sum()

        c11 = c11/(c11 + c21 + c31 + c41)
        c21 = c21/(c11 + c21 + c31 + c41)
        c31 = c31/(c11 + c21 + c31 + c41)
        c41 = c41/(c11 + c21 + c31 + c41)

        c12 = c12/(c12 + c22 + c32 + c42)
        c22 = c22/(c12 + c22 + c32 + c42)
        c32 = c32/(c12 + c22 + c32 + c42)
        c42 = c42/(c12 + c22 + c32 + c42)

        c13 = c12/(c13 + c23 + c33 + c43)
        c23 = c22/(c13 + c23 + c33 + c43)
        c33 = c32/(c13 + c23 + c33 + c43)
        c43 = c42/(c13 + c23 + c33 + c43)

        c14 = c12/(c14 + c24 + c34 + c44)
        c24 = c22/(c14 + c24 + c34 + c44)
        c34 = c32/(c14 + c24 + c34 + c44)
        c44 = c42/(c14 + c24 + c34 + c44)

        pred_prob = pred1*(c11,c12,c13,c14) + pred2*(c21,c22,c23,c24) + pred3*(c31,c32,c33,c34) + pred4*(c41,c42,c43,c44)

        #Total accuracies to predict the weights
        # acc1 = np.trace(m1)/m1.sum()
        # acc2 = np.trace(m2)/m2.sum()
        # acc3 = np.trace(m3)/m3.sum()
        # acc4 = np.trace(m4)/m4.sum()
        #
        # acc1 = acc1/(acc1 + acc2 + acc3 + acc4)
        # acc2 = acc2/(acc1 + acc2 + acc3 + acc4)
        # acc3 = acc3/(acc1 + acc2 + acc3 + acc4)
        # acc4 = acc4/(acc1 + acc2 + acc3 + acc4)

        # pred_prob = pred1*acc1 + pred2*acc2 + pred3*acc3 + pred4*acc3

        pred = []
        for n in range(len(pred_prob)):
            pred.append(np.argmax(pred_prob[n]))
        pred=np.array(pred)
        # print("pred",pred)
        # print("y test", y_test)
        conf_matrix = confusion_matrix(y_test, pred)
        # print(i, conf_matrix)
        conf_matrix_list_of_arrays.append(conf_matrix)
        score=accuracy_score(y_test, pred)
        scores.append(score)

mean_of_conf_matrix_arrays = np.mean(conf_matrix_list_of_arrays, axis=0)
print(mean_of_conf_matrix_arrays,file=f)
print('Accuracy: %.7f (%.7f)' % (np.mean(scores), np.std(scores)),file=f)

f.close()

dict_results={'Model':'ENSEMBLE2_SMOTE','majority_baseline_accuracy':accuracy1,'stratified_baseline_accuracy':accuracy2 ,'mean_accuracy':np.mean(scores), 'std_dev_accuracy':np.std(scores), 'mean_confusion_matrix':mean_of_conf_matrix_arrays,'confusion_matrices':conf_matrix_list_of_arrays}

with open(dir_path+'/results_smote/'+ep[0]+'_'+ep[1]+'/'+folder+'/ENSEMBLE2'+result_suffix+'_'+ep[0]+'_'+ep[1]+'.pickle', 'wb') as handle:
    pickle.dump(dict_results, handle, protocol=pickle.HIGHEST_PROTOCOL)
