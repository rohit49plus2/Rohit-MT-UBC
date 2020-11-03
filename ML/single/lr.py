from load_data import *
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import validation_curve
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.metrics import r2_score
from sklearn.preprocessing import normalize
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import AdaBoostClassifier
from sklearn.linear_model import LogisticRegression

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


X=eye_and_log.drop(emotions,axis=1)
X = X.select_dtypes(include=numerics)
X=correlation(X,0.9)
X=X.to_numpy()
X=normalize(X)

ep=["Boredom"]
y=eye_and_log[ep]
y=y.to_numpy()
y=y.ravel()

model = DummyClassifier(strategy="most_frequent")
model.fit(X, y)
y_pred = model.predict(X)
accuracy1 = accuracy_score(y, y_pred)
print('accuracy',accuracy1)

lr=LogisticRegression()
model = AdaBoostClassifier(lr)

# evaluate model
cv = RepeatedStratifiedKFold(n_splits=8, n_repeats=10, random_state=2)
parameters = {'n_estimators':range(1, 2, 3)}
clf = GridSearchCV(model, parameters,cv=cv, n_jobs=4)
clf.fit(X,y)
print('Accuracy: ', clf.best_score_)
print('Best Parameters: ', clf.best_params_)
# print('\n\ncv results: ', clf.cv_results_)


lr = LogisticRegression()
model = AdaBoostClassifier(lr,n_estimators=clf.best_params_['n_estimators'])
cv = RepeatedStratifiedKFold(n_splits=8, n_repeats=10, random_state=2)

conf_matrix_list_of_arrays = []
scores=[]
for train_index, test_index in cv.split(X, y):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    model.fit(X_train, y_train)
    pred = model.predict(X_test)
    conf_matrix = confusion_matrix(y_test, pred)
    conf_matrix_list_of_arrays.append(conf_matrix)
    score=accuracy_score(y_test, pred)
    scores.append(score)

mean_of_conf_matrix_arrays = np.mean(conf_matrix_list_of_arrays, axis=0)
print(mean_of_conf_matrix_arrays)
print('Accuracy: %.7f (%.7f)' % (np.mean(scores), np.std(scores)))


dict_results={'Model':'LR','baseline_accuracy':accuracy1 ,'cv best parameters':clf.best_params_,'mean_accuracy':np.mean(scores), 'std_dev_accuracy':np.std(scores), 'mean_confusion_matrix':mean_of_conf_matrix_arrays}

with open(dir_path+'/results/LR'+result_suffix+'_'+ep[0]+'.pickle', 'wb') as handle:
    pickle.dump(dict_results, handle, protocol=pickle.HIGHEST_PROTOCOL)
