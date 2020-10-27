from load_data import *
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import validation_curve
from sklearn.model_selection import KFold
from sklearn.model_selection import cross_val_score
from sklearn.model_selection import cross_val_predict
from sklearn.model_selection import GridSearchCV
from sklearn.feature_selection import RFE
from sklearn.feature_selection import RFECV
from sklearn.metrics import accuracy_score
from sklearn.metrics import r2_score
from sklearn.preprocessing import normalize
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from sklearn.dummy import DummyClassifier

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
X = X.select_dtypes(include=numerics)
X=correlation(X,0.9)
X=X.to_numpy()
X=normalize(X)

y_temp=eye_and_log[["Frustration","Boredom"]]
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
print('accuracy',accuracy1)


model = RandomForestClassifier()
# evaluate model
cv = RepeatedStratifiedKFold(n_splits=8, n_repeats=10, random_state=2)
parameters = {'max_depth':[1,2,3,4,5],
    'max_depth': [4,8,10],
    'min_samples_leaf': range(100, 400, 200),
    'min_samples_split': range(200, 500, 200),
    'n_estimators': [100,200, 300],
    'max_features': [5, 10]
}
clf = GridSearchCV(model, parameters,cv=cv,n_jobs=-1)
clf.fit(X,y)
print('Accuracy: ', clf.best_score_)
print('Best Parameters: ', clf.best_params_)
# print('\n\ncv results: ', clf.cv_results_)


model = RandomForestClassifier(max_depth=clf.best_params_['max_depth'])
cv = RepeatedStratifiedKFold(n_splits=8, n_repeats=10, random_state=2)

conf_matrix_list_of_arrays = []
scores=[]
for train_index, test_index in cv.split(X, y):
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    model.fit(X_train, y_train)
    conf_matrix = confusion_matrix(y_test, model.predict(X_test))
    conf_matrix_list_of_arrays.append(conf_matrix)
    score=accuracy_score(y_test, model.predict(X_test))
    scores.append(score)

mean_of_conf_matrix_arrays = np.mean(conf_matrix_list_of_arrays, axis=0)
print(mean_of_conf_matrix_arrays)
print('Accuracy: %.7f (%.7f)' % (np.mean(scores), np.std(scores)))
