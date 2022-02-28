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
from sklearn.svm import SVC
import random
from collections import Counter, defaultdict

from ast import literal_eval as make_tuple

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
f = open(dir_path+'/results_smote/'+ep[0]+'_'+ep[1]+'/'+folder+'/BINARY_ENSEMBLE'+result_suffix+'_'+ep[0]+'_'+ep[1]+'.txt', 'w')


if ep==['Frustration','Boredom']:
    d=pd.read_pickle(dir_path+datafiles_thres[num])
    # print(eye_and_log.isnull().sum())
    d=d.drop(['Mean # of SRL processes per relevant page while on SG1'],axis=1)
    y_temp=d[ep]
    X=d.drop(emotions,axis=1)
    ids=list(d['key'])
    ids=np.array([id[0] for id in ids])
    X=d[d.columns[-57:]]

    X1=X
    y1_temp = y_temp
    X2=X
    y2_temp = y_temp

elif ep==['Curiosity','Anxiety']:
    ids=list(combined['key'])
    ids=np.array([make_tuple(id)[0] for id in ids])
    y_temp=combined[ep]
    X = combined.drop(emotions,axis=1)
    X=X.drop('Unnamed: 0',axis=1)

    X2=X
    y2_temp=y_temp

    X = X[X.columns.intersection(eye.columns)]

    X1=X
    y1_temp=y_temp



X1 = X1.select_dtypes(include=numerics)
X1=X1.to_numpy()
X1=normalize(X1)
X2 = X2.select_dtypes(include=numerics)
X2=X2.to_numpy()
X2=normalize(X2)

y1_temp=y1_temp.to_numpy()
y2_temp=y2_temp.to_numpy()


y1bin1=[]
y1bin2=[]
y1=[]
for i in range(len(y1_temp)):
    if np.array_equal(y1_temp[i],np.array([0,0])):
        y1.append(0)
        y1bin1.append(0)
        y1bin2.append(0)
    elif np.array_equal(y1_temp[i],np.array([1,0])):
        y1.append(1)
        y1bin1.append(1)
        y1bin2.append(0)
    elif np.array_equal(y1_temp[i],np.array([0,1])):
        y1.append(2)
        y1bin1.append(0)
        y1bin2.append(1)
    elif np.array_equal(y1_temp[i],np.array([1,1])):
        y1.append(3)
        y1bin1.append(1)
        y1bin2.append(1)


y1=np.array(y1)
y1bin1=np.array(y1bin1)
y1bin2=np.array(y1bin2)

y2bin1=[]
y2bin2=[]
y2=[]
for i in range(len(y2_temp)):
    if np.array_equal(y2_temp[i],np.array([0,0])):
        y2.append(0)
        y2bin1.append(0)
        y2bin2.append(0)
    elif np.array_equal(y2_temp[i],np.array([1,0])):
        y2.append(1)
        y2bin1.append(1)
        y2bin2.append(0)
    elif np.array_equal(y2_temp[i],np.array([0,1])):
        y2.append(2)
        y2bin1.append(0)
        y2bin2.append(1)
    elif np.array_equal(y2_temp[i],np.array([1,1])):
        y2.append(3)
        y2bin1.append(1)
        y2bin2.append(1)

y2=np.array(y2)
y2bin1=np.array(y2bin1)
y2bin2=np.array(y2bin2)

# print(len(X1))
# print(len(X2))
# print(len(y1))
# print(len(y1bin1))
# print(len(y1bin2))
# print(len(y2))
# print(len(y2bin1))
# print(len(y2bin2))




from sklearn.decomposition import IncrementalPCA
from sklearn.decomposition import PCA

# model = DummyClassifier(strategy="most_frequent")
# model.fit(X, y)
# y_pred = model.predict(X)
# accuracy1 = accuracy_score(y, y_pred)
# print('Majority Class Base Accuracy',accuracy1,file=f)
#
# model = DummyClassifier(strategy="stratified")
# model.fit(X, y)
# y_pred = model.predict(X)
# accuracy2 = accuracy_score(y, y_pred)
# print('Stratified Class Base Accuracy',accuracy2,file=f)

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

parameters_svm = {'kernel':['rbf'], 'C':range(1,100,10),'gamma':np.arange(0.05,0.55,.05)}
svm = SVC(probability=True)

conf_matrix_list_of_arrays = []
scores=[]
for i in range(10):
    for fold_ind, (train_index, test_index) in enumerate(stratified_group_k_fold(X1, y1, ids, k=8)):
        print("Fold ", fold_ind)
        # print(train_index,test_index)
        X1_train, X1_test = X1[train_index], X1[test_index]
        X2_train, X2_test = X2[train_index], X2[test_index]
        y1_train, y1_test = y1[train_index], y1[test_index]
        y1bin1_train, y1bin1_test = y1bin1[train_index], y1bin1[test_index]
        y2bin2_train, y2bin2_test = y2bin2[train_index], y2bin2[test_index]
        train_groups, test_groups = ids[train_index], ids[test_index]

        # print(data,X_train.shape)
        pca = IncrementalPCA(n_components=X1_train.shape[1]//5, batch_size=120)
        pca.fit(X1_train)
        X1_train=pca.transform(X1_train)
        X1_test=pca.transform(X1_test)
        X1_train, y1bin1_train = pipeline.fit_resample(X1_train, y1bin1_train)#Smote
        # print(data,X_train.shape)

        pca = IncrementalPCA(n_components=X2_train.shape[1]//5, batch_size=120)
        pca.fit(X2_train)
        X2_train=pca.transform(X2_train)
        X2_test=pca.transform(X2_test)
        X2_train, y2bin2_train = pipeline.fit_resample(X2_train, y2bin2_train)#Smote
        # print(data,X_train.shape)

        if ep==['Frustration','Boredom']:
            model_to_use = rf
            parameters_to_use=parameters_rf
        elif ep==['Curiosity','Anxiety']:
            model_to_use = svm
            parameters_to_use=parameters_svm

        clf1 = GridSearchCV(model_to_use, parameters_to_use,cv=5, n_jobs=4)
        clf1.fit(X1_train, y1bin1_train)
        y_pred = clf1.best_estimator_.predict(X1_train)
        m1=confusion_matrix(y1bin1_train, y_pred)
        # print(X1_train.shape)
        # print(X1_test.shape)
        pred1 = clf1.predict(X1_test)

        clf2 = GridSearchCV(model_to_use, parameters_to_use,cv=5, n_jobs=4)
        clf2.fit(X2_train, y2bin2_train)
        y_pred = clf2.best_estimator_.predict(X2_train)
        m2=confusion_matrix(y2bin2_train, y_pred)
        pred2 = clf2.predict(X2_test)

        pred = []
        for n in range(len(pred1)):
            pred.append(pred1[n]+2*pred2[n])
        pred=np.array(pred)
        # print("pred",pred)
        # print("y test", y_test)
        conf_matrix = confusion_matrix(y1_test, pred)
        # print(i, conf_matrix)
        conf_matrix_list_of_arrays.append(conf_matrix)
        score=accuracy_score(y1_test, pred)
        scores.append(score)

mean_of_conf_matrix_arrays = np.mean(conf_matrix_list_of_arrays, axis=0)
print(mean_of_conf_matrix_arrays,file=f)
print('Accuracy: %.7f (%.7f)' % (np.mean(scores), np.std(scores)),file=f)

f.close()

dict_results={'Model':'BINARY_ENSEMBLE_SMOTE','mean_accuracy':np.mean(scores), 'std_dev_accuracy':np.std(scores), 'mean_confusion_matrix':mean_of_conf_matrix_arrays,'confusion_matrices':conf_matrix_list_of_arrays}

with open(dir_path+'/results_smote/'+ep[0]+'_'+ep[1]+'/'+folder+'/BINARY_ENSEMBLE'+result_suffix+'_'+ep[0]+'_'+ep[1]+'.pickle', 'wb') as handle:
    pickle.dump(dict_results, handle, protocol=pickle.HIGHEST_PROTOCOL)
