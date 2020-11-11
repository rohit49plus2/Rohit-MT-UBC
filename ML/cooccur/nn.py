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

datasets=['eye','log','both']
for data in datasets:
    ep=["Frustration","Boredom"]
    f = open(dir_path+'/results'+folder+'/NN'+result_suffix+'_'+ep[0]+'_'+ep[1]+'_'+data+'.txt', 'w')

    print("Dataset: ", data,file=f)

    X=eye_and_log.drop(emotions,axis=1)
    if data=='eye':
        X=X[X.columns[:-57]]
    elif data=='log':
        X=X[X.columns[-57:]]
    X = X.select_dtypes(include=numerics)
    X=correlation(X,0.9)
    X=X.to_numpy()
    X=normalize(X)
    from sklearn.decomposition import IncrementalPCA
    print('Shape of X before PCA:', X.shape,file=f)
    ipca = IncrementalPCA(n_components=X.shape[1]//5, batch_size=120)
    ipca.fit(X)
    X=ipca.transform(X)
    print('Shape of X after PCA:', X.shape,file=f)

    y_temp=eye_and_log[ep]
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
    print('Base Accuracy',accuracy1,file=f)

    import tensorflow as tf
    from tensorflow import keras
    from tensorflow.keras.models import Sequential
    from tensorflow.keras.layers import Dense
    from tensorflow.keras.wrappers.scikit_learn import KerasClassifier

    def create_model():
        model = Sequential()
        model.add(Dense(200, input_dim=X.shape[1], activation='relu'))
        model.add(Dense(4, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

    model = KerasClassifier(build_fn=create_model,verbose=0)
    cv = RepeatedStratifiedKFold(n_splits=8, n_repeats=10, random_state=2)
    parameters = {'epochs':[10,20,30]
    }
    clf = GridSearchCV(model, parameters,cv=cv,n_jobs=4)
    clf.fit(X,y)
    print('Accuracy: ', clf.best_score_,file=f)
    print('Best Parameters: ', clf.best_params_,file=f)


    cv = RepeatedStratifiedKFold(n_splits=8, n_repeats=10, random_state=2)

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
    print(mean_of_conf_matrix_arrays,file=f)
    print('Accuracy: %.7f (%.7f)' % (np.mean(scores), np.std(scores)),file=f)

    f.close()

    dict_results={'Model':'NN','baseline_accuracy':accuracy1 ,'cv best parameters':clf.best_params_,'mean_accuracy':np.mean(scores), 'std_dev_accuracy':np.std(scores), 'mean_confusion_matrix':mean_of_conf_matrix_arrays}

    with open(dir_path+'/results'+folder+'/NN'+result_suffix+'_'+ep[0]+'_'+ep[1]+'_'+data+'.pickle', 'wb') as handle:
        pickle.dump(dict_results, handle, protocol=pickle.HIGHEST_PROTOCOL)
