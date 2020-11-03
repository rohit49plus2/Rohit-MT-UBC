from load_data import *
from sklearn.model_selection import train_test_split
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
from sklearn.dummy import DummyClassifier
from sklearn.preprocessing import OneHotEncoder
from tensorflow.keras.backend import clear_session
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
values=X['Part_id'].value_counts()
drop_values=list(values[values<5].index)

y_temp=eye_and_log[["Frustration","Boredom"]]


Z=X
z_temp=y_temp
for i in range(X.shape[0]):
    if X['Part_id'][i] in drop_values:
        Z=Z.drop(i)
        z_temp=z_temp.drop(i)
# print(Z['Part_id'].value_counts())
Z = Z.select_dtypes(include=numerics)
Z=correlation(Z,0.9)
print('shape of Z: ',Z.shape)
Z=Z.to_numpy()
Z=normalize(Z)


X = X.select_dtypes(include=numerics)
X=correlation(X,0.9)
print('shape of X: ',X.shape)
X=X.to_numpy()
X=normalize(X)


z_temp=z_temp.to_numpy()
z=[]
for i in range(len(z_temp)):
    if np.array_equal(z_temp[i],np.array([0,0])):
        z.append(0)
    elif np.array_equal(z_temp[i],np.array([1,0])):
        z.append(1)
    elif np.array_equal(z_temp[i],np.array([0,1])):
        z.append(2)
    elif np.array_equal(z_temp[i],np.array([1,1])):
        z.append(3)
z=np.array(z)

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


import tensorflow as tf
from tensorflow import keras
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense
from tensorflow.keras.layers import SimpleRNN
from tensorflow.keras.wrappers.scikit_learn import KerasClassifier

Z=np.reshape(Z,(-1,5,396))
z=np.reshape(z,(-1,5))
print(Z.shape)
# print(Z)
X=Z
y=z


def create_model():
    model = Sequential()
    model.add(SimpleRNN(5, return_sequences=True))
    model.add(Dense(1, activation='softmax'))
    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    return model

#
X_train,X_test,y_train,y_test=train_test_split(X,y,test_size=0.2)

model = KerasClassifier(build_fn=create_model)
model.fit(X_train, y_train, epochs=100, batch_size=64)

y_pred = model.predict(X_test)

# print(y_pred)
pred = list()
for i in range(len(y_pred)):
    pred.append(np.argmax(y_pred[i]))
#Converting one hot encoded test label to label
test = list()
for i in range(len(y_test)):
    test.append(np.argmax(y_test[i]))

from sklearn import metrics
print(metrics.confusion_matrix(y_true=test, y_pred=pred))
print("accuracy", metrics.accuracy_score(test, pred))
print("precision", metrics.precision_score(test, pred,average='micro'))
print("recall", metrics.recall_score(test, pred,average='micro'))
cv = RepeatedStratifiedKFold(n_splits=8, n_repeats=10, random_state=2)
# parameters = {'epochs':[10,20,30]
# }
# clf = GridSearchCV(model, parameters,cv=cv,n_jobs=4)
# clf.fit(X,y)
# print('Accuracy: ', clf.best_score_)
# print('Best Parameters: ', clf.best_params_)

# mean_of_conf_matrix_arrays = np.mean(conf_matrix_list_of_arrays, axis=0)
# print(mean_of_conf_matrix_arrays)
# print('Accuracy: %.7f (%.7f)' % (np.mean(scores), np.std(scores)))
#
#
conf_matrix_list_of_arrays = []
scores=[]
for train_index, test_index in cv.split(X, y):
    model = KerasClassifier(build_fn=create_model, epochs=clf.best_params_['epochs'])
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    ohe=OneHotEncoder()
    y_train=ohe.fit_transform(y_train.reshape(-1,1)).toarray()

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    #Converting predictions to label
    pred = list()
    for i in range(len(y_pred)):
        pred.append(np.argmax(y_pred[i]))
    conf_matrix = confusion_matrix(y_test, pred)
    conf_matrix_list_of_arrays.append(conf_matrix)
    score=accuracy_score(y_test, pred)
    scores.append(score)
    clear_session()

mean_of_conf_matrix_arrays = np.mean(conf_matrix_list_of_arrays, axis=0)
print(mean_of_conf_matrix_arrays)
print('Accuracy: %.7f (%.7f)' % (np.mean(scores), np.std(scores)))


# dict_results={'Model':'RNN','baseline_accuracy':accuracy1 ,'cv best parameters':clf.best_params_,'mean_accuracy':np.mean(scores), 'std_dev_accuracy':np.std(scores), 'mean_confusion_matrix':mean_of_conf_matrix_arrays}
#
# with open(dir_path+'/results/RNN'+result_suffix+'.pickle', 'wb') as handle:
#     pickle.dump(dict_results, handle, protocol=pickle.HIGHEST_PROTOCOL)
