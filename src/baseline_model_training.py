import pandas as pd
import requests
import re
import glob, os, shutil
import gzip
import random
from bs4 import BeautifulSoup
import json
import pandas as pd
import subprocess
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split

#training

def Logistic_Regression(X_train, y_train, X_test, y_test):
    '''
    Training of logistic regression model
    :param X_train: features to be trained
    :param y_train: training labels
    :param X_test: features to be predicted
    :param y_test: test labels
    :return: confusion matrix
    '''
    clf = LogisticRegression()
    clf.fit(X_train,y_train)
    y_pred = clf.predict(X_test)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    return tn, fp, fn, tp

def Random_Forest(X_train, y_train, X_test, y_test):
    '''
    Training of random forest model
    :param X_train: features to be trained
    :param y_train: training labels
    :param X_test: features to be predicted
    :param y_test: test labels
    :return: confusion matrix
    '''
    clf = RandomForestClassifier(max_depth=2, random_state=0)
    clf.fit(X_train,y_train)
    y_pred = clf.predict(X_test)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    return tn, fp, fn, tp

def GBC(X_train, y_train, X_test, y_test):
    '''
    Training of gradient boost model
    :param X_train: features to be trained
    :param y_train: training labels
    :param X_test: features to be predicted
    :param y_test: test labels
    :return: confusion matrix
    '''
    clf = GradientBoostingClassifier()
    clf.fit(X_train,y_train)
    y_pred = clf.predict(X_test)
    tn, fp, fn, tp = confusion_matrix(y_test, y_pred).ravel()
    return tn, fp, fn, tp

def compute_metrics(mat):
    '''
    Compute accuracy and false negative rate based on given confusion matrix
    :param mat: confusion matrix
    :return: list of confusion matrix + accuracy score + fn rate
    '''
    return mat + [(mat[0]+mat[3])/sum(mat), mat[2]/(mat[2]+mat[3])]

def run_baseline(df, test = 0.33, y_column = 'category'):
    '''
    Run the entire baseline and save result
    :param df: feature dataframe
    :param y_column: label column, default set to category
    :param test_size: train test split size
    :return: none
    '''
    
    X = df.drop(y_column, axis = 1)
    y = df[y_column]
    print('--- feature and label ready')
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size = test, shuffle = True)
    print('--- train and test ready')
    
    metric_lr = Logistic_Regression(X_train, y_train, X_test, y_test)
    lr = compute_metrics(list(metric_lr))
    print('--- Done fitting logistic regression')
    metric_rf = Random_Forest(X_train, y_train, X_test, y_test)
    rf = compute_metrics(list(metric_rf))
    print('--- Done fitting random forest')
    metric_gbc = GBC(X_train, y_train, X_test, y_test)
    bgc = compute_metrics(list(metric_gbc))
    print('--- Done fitting gradient boost')
    baseline = pd.DataFrame([lr, rf, bgc], index = ['logistic regression', 'random forest', 'gradient boost classifier'], columns = ['tn', 'fp', 'fn', 'tp', 'acc', 'fnr'])
    print('--- saving result metrics')
    baseline.to_csv(os.path.join('output', 'baseline_result.txt'))
    print('--- Finished all baseline tasks!')
    