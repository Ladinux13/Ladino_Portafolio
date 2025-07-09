### ================================= Modelos de clasificación por ML ================================= ###
### ================================= Ladino Álvarez Ricardo Arturo =============================== ###
### ============================================ Librerias ============================================ ###

import numpy as np
import scipy.stats
import pandas as pd
import xgboost as xgb
import multiprocessing
from sklearn import metrics
import matplotlib.pyplot as plt
import seaborn as sns; sns.set() 

### ============================================ RED NEURONAL ============================================ ###

import time
import keras
import multiprocessing
from keras.models import Sequential

### ============================================ Warnings ============================================ ###

import warnings
warnings.filterwarnings('ignore')


### ================================= ================================= ================================= ###
### ======================================== Clasificador XGBoost ======================================= ###
### ================================= ================================= ================================= ###


def XGBoost_Class(X_train, y_train, X_test, y_test):
    
    parametrs = {"subsample": [0.25, 0.50, 0.75, 1],
                 "max_depth":[None, 1, 3, 5, 10, 20, 30],
                 "learning_rate":[0.001, 0.01, 0.1],
                 "booster":['gbtree']
                 }
    
    idx_validacion = np.random.choice(X_train.shape[0],
                                      size = int(X_train.shape[0]*0.1),
                                      replace = False)
    

    eval_set =  [(X_Val, y_Val)]
    
    estimador = xgb.XGBClassifier(n_estimators = 1000,
                                  n_jobs = multiprocessing.cpu_count() - 1,
                                  eval_metric = 'rmse',
                                  early_stopping_rounds = 10)
    
    model = GridSearchCV(estimator = estimador,
                         param_grid = parametrs, 
                         cv = RepeatedKFold(n_splits = 5, n_repeats = 1, random_state = 42),
                         scoring = 'accuracy',
                         verbose = 0)
    
    GridFit = model.fit(X = X_train_grid,
                        y = y_train_grid,
                        eval_set = eval_set,
                        verbose = 0)
    
    Resultado = pd.DataFrame(GridFit.cv_results_)
    
    Best_estimador = GridFit.best_estimator_

    y_hat = Best_estimador.predict(X = X_test)

    RMSE = mean_squared_error(y_true = y_test, y_pred = y_hat, squared = False)

    print("----------------------------")
    print(f"RMSE test:{round(RMSE, 3)}")
    print("----------------------------")

    return(GridFit, T_Resultado, y_hat)


### ================================= ================================= ================================= ###
### ====================================== Modelo Generador de Datos ==================================== ###
### ================================= ================================= ================================= ###

class FixableDataFrame(pd.DataFrame):
    def __init__(self, *args, fixed={}, **kwargs):
        self.__dict__["var_dictionary"] = fixed
        super(FixableDataFrame, self).__init__(*args, **kwargs)
    def __setitem__(self, key, value):
        out = super(FixableDataFrame, self).__setitem__(key, value)
        if isinstance(key, str) and key in self.__dict__["var_dictionary"]:
            out = super(FixableDataFrame, self).__setitem__(key, self.__dict__["var_dictionary"][key])

### =================================
### Generador de datos
### =================================

def generator(n, fixed={}, seed=0):
    if seed is not None:
        np.random.seed(seed)
    X = FixableDataFrame(fixed=fixed)

### ================================= ================================= ================================= ###
### ============================================ DATOS GENERALES ========================================= ###
### ================================= ================================= ================================= ###


    # Variable "GENERO" con 0:Hombre & 1: Mujer. La ocurrencia es de 70% hombres y 30% mujeres
    X["GENERO"] = np.random.choice([0,1], size=(n,), p = [0.70, 0.30])

    # Variable "EDAD" distribuida de manera uniforme en un rango de 18 a 35 años
    X["EDAD"] =  np.random.uniform(18, 35, size=(n,)) + (np.random.normal(0, 2, size=(n,)))

    # Variable "CEDPRO" con 0: Sin Cédula & 1: Con Cédula
    X["CEDPRO"] = np.random.choice([0,1], size=(n,), p = [0.30, 0.70]) 

    # Variable "OTRSAN" con 0:Sin otro tipo de Sanciones & 1: Con otro tipo de Sanciones
    X["OTRSAN"] = np.random.choice([0,1], size=(n,), p = [0.90, 0.10]) 


    # Variable NIVEST como consecuencia de ESTCIV, GENERO, EDAD, CEDPRO, TOTEMP y U[ERROR]
    X["NIVEST"] = (X["ESTCIV"]) + (X["GENERO"]) + (X["EDAD"]) + (X["CEDPRO"]) + (X["TOTEMP"]) + (np.random.normal(0, 2, size=(n,)))

    # Variable NIVLAB como consecuencia de NIVEST, SANSFP, OTRSAN, TOTEMP, y U[ERROR]
    X["NIVLAB"] = (X["NIVEST"]) + (X["SANSFP"]) + (X["OTRSAN"]) + (X["TOTEMP"]) + (np.random.normal(0, 2, size=(n,)))

    # Variable ATPENAL como consecuencia de FMPENAL, DEMJUD, FMDELIN y U[ERROR]
    
    X["ATPENAL"] = (X["FMPENAL"]) + (X["DEMJUD"]) + (X["FMDELIN"]) + (np.random.normal(0, 2, size=(n,)))



### ================================= ================================= ================================= ###
### ====================================== Bienes Muebles e inmuebles ====================================== ###
### ================================= ================================= ================================= ###
# 
#     # Variable "FADINMU"
    X["FADINMU"] = np.random.choice([0,1], size=(n,), p = [0.80, 0.20]) 

    # Variable "TPOINMB" con FADINMU
    X["TPOINMB"] = X["FADINMU"] + (np.random.normal(0, 2, size=(n,))) + np.random.choice([0,1], size=(n,), p = [0.80, 0.20])

    # Variable "TITINMB" con TPOINMB & FADINMU
    X["TITINMB"] = np.random.choice([0,1], size=(n,), p = [0.80, 0.20]) +  X["TPOINMB"]  +  X["FADINMU"] + (np.random.normal(0, 2, size=(n,)))

### ================================= ================================= ================================= ###
### ====================================== CTAS BANCARIAS  ============================================== ###
### ================================= ================================= ================================= ###
# 


    # Variable "TITCTAS"
    X["TITCTAS"] = np.random.choice([0,1], size=(n,), p = [0.40, 0.60]) 

    # Variable "DEPOSITO" con "NOCTAS", "DINFRA", "DEUFAM" y "DINPRES"
    X["DEPOSITO"] = np.random.uniform(15000, 44240, size=(n,))  + X["NOCTAS"] \
                     + X["DINFRA"] + X["DEUFAM"] + X["DINPRES"]\
                          + (np.random.normal(0, 2, size=(n,)))

    # Variable "RETIRO" con "NOCTAS" 
    X["RETIRO"] = np.random.uniform(15000, 45000, size=(n,))  + X["NOCTAS"]  + (np.random.normal(0, 2, size=(n,)))

    
    X["TIPO_CLASS"] = np.where((X["DEPOSITO"] > X["RETIRO"]),0,1)
    
### ================================= ================================= ================================= ###
### ====================================== CLASE  ======================================================= ###
### ================================= ================================= ================================= ###

    # Variable CLASE como consecuencia de todas las anteriores 
    X["CLASE"] = scipy.special.expit((1/X["NIVEST"])\
                                     + (1/X["NIVLAB"])\
                                        + (X["SANSFP"])\
                                            + (X["OTRSAN"])\
                                                + (1/X["ATPENAL"])\
                                                    +(X["FMPENAL"])\
                                                          +(X["DEMJUD"])\
                                                            +(X["FMDELIN"])\
                                                                + (X["NOINMB"]) + (X["TIPO_CLASS"])\
                                                                    + np.random.normal(0, 1, size=(n,)))
    
    X["CLASE"] = scipy.stats.bernoulli.rvs(X["CLASE"])

    return X

### ================================= ================================= ================================= ###
### ========================================= FUNCION GENERADORA ======================================== ###
### ================================= ================================= ================================= ###

def Generadora(n):
    X_full = generator(n)
    Data = X_full.drop(['DEPOSITO', 'RETIRO','TIPO_CLASS'], axis = 1)
    return Data

### ================================= ================================= ================================= ###
### ================================= ================================= ================================= ###


### ================================= ================================= ================================= ###
### ================================== REGULARIZACIÓN DE CLASES ========================================= ###
### ================================= ================================= ================================= ###

def Optimiza_Class (X_train, y_train, X_test, y_test, pickle, ThOpt_metrics):

    y_proba_train = pickle.predict_proba(X_train)[:,1]
    threshold = np.round(np.arange(0.01, 0.85, 0.015), 2)

    if ThOpt_metrics == 'Kappa':
        tscores = []
        for thresh in threshold:
            scores = [1 if x >= thresh else 0 for x in y_proba_train]
            kappa = metrics.cohen_kappa_score(y_train, scores)
            tscores.append((np.round(kappa, 4), thresh))
        tscores.sort(reverse = True)
        thresh = tscores[0][-1]
    elif ThOpt_metrics == 'ROC':
        fpr, tpr, threshold_roc = metrics.roc_curve(y_train, y_proba_train, pos_label = 1)
        specificity = (1 - fpr)
        roc_dist = (( 2*tpr*specificity )/(tpr + specificity))
        thresh = threshold_roc[np.argmax(roc_dist)]

    y_proba_test= pickle.predict_proba(X_test)[:,1]

    
    print("")
    print("-------------------")
    print (f"Test accuracy: {np.round(100* Accuracy, 3)} %")
    print("")
    print("-------------------")
    print(classification_report(y_test, scores))
    
    accuracy_dt = np.round(accuracy_score(y_test, scores), 2)
    misclassification_dt = np.round(1-accuracy_dt, 2)
    precision_dt = np.round(precision_score(y_test, scores), 2)
    recall_dt = np.round(recall_score(y_test, scores), 2)
    f1_score_dt = np.round(f1_score(y_test, scores), 2)
    
    print('Score')
    print('Accuracy:              {0:.2f}'.format(accuracy_dt))
    print('Misclassification:     {0:.2f}'.format(misclassification_dt))
    print('Precision:             {0:.2f}'.format(precision_dt))
    print('Recall:                {0:.2f}'.format(recall_dt))
    print('F1-Score:              {0:.2f}\n'.format(f1_score_dt))
    