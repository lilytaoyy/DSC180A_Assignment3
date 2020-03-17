import warnings
warnings.filterwarnings("ignore")
import numpy as np
import json
import os
import re
import scipy
import pandas as pd
from sklearn.preprocessing import MultiLabelBinarizer

def extract_api(x):
    '''
    Extract all apis from the input string
    :param x: string, smali code
    :return: a set of all extracted api calls
    '''
    smalis = '\n'.join(x.dropna())
    return set(re.findall('invoke-\w+ {.*}, (.*?)\\(', smalis))

def matA(smali_df):
    '''
    Construction of matrix A
    :param smali_df: a dataframe of single column of smali code by app
    :return: matrix A, and unique set of api calls (columns of matrix A)
    '''
    apis_by_app = smali_df.apply(extract_api, axis = 1)
    mlb_A = MultiLabelBinarizer(sparse_output = True)
    A = mlb_A.fit_transform(apis_by_app)
    apis = mlb_A.classes_
    return A, apis

def matAtest(smali_df, classes):
    '''
    Construction of matrix A test
    :param smali_df: smali_df: a dataframe of single column of smali code by app
    :param classes: unique set of api calls (columns of matrix A)
    :return: matrix A test
    '''
    apis_by_app = smali_df.apply(extract_api, axis = 1)
    mlb_A = MultiLabelBinarizer(sparse_output = True, classes = classes)
    A = mlb_A.fit_transform(apis_by_app)
    return A

def extract_block(x):
    '''
    Extract all code blocks from the input string
    :param x: string, smali code
    :return: a list of all extracted api calls
    '''
    smali = '\n'.join(x.dropna())
    return list(set(re.findall('\.method([\S\s]*?)\.end method', smali)))

def matB(smali_df):
    '''
    Construction of matrix B
    :param smali_df: a dataframe of single column of smali code by app
    :return: matrix B
    '''
    code_blocks = smali_df.apply(extract_block, axis = 1)
    block_df = code_blocks.explode().reset_index().drop('index', axis = 1)
    B_dic= {}
    
    def extract_api_from_blocks(block):
        apis = set(re.findall('invoke-\w+ {.*}, (.*?)\\(',block))
        for api in apis:
            if not api in B_dic.keys():
                B_dic[api] = apis
            else:
                B_dic[api] = B_dic[api].union(apis)
    
    block_df[0].dropna().apply(extract_api_from_blocks)
    mlb_b = MultiLabelBinarizer(sparse_output = True)
    B = mlb_b.fit_transform(B_dic.values())
    return B

def extract_package(x):
    return re.search('(\[*[ZBSCFIJD]|\[*L[\w\/$-]+;)->', x)[1] 

def matP(apis):
    '''
    Construction of matrix P
    :param apis: unique set of api calls (columns of matrix A)
    :return: matrix P
    '''
    P_dic = {}
    api_df = pd.DataFrame({'apis': apis}).dropna()
    api_df['package'] = api_df['apis'].apply(extract_package)
    P_dic = api_df.groupby('package')['apis'].apply(set).to_dict()
    api_df['same_pac'] = api_df['package'].apply(lambda x: P_dic[x])
    P_series = api_df.drop('package',axis=1).set_index('apis')['same_pac']
    mlb_p = MultiLabelBinarizer(sparse_output = True)
    P = mlb_p.fit_transform(P_series)
    return P


def A_B_P(smali_df, test_df = None):
    '''
    Combining the construction of A, B, P and test A matices
    :param smali_df: a dataframe of single column of smali code by app
    :param test_df: a test dataframe of single column of smali code by app
    :return: matrix A, B, P, A test
    '''
    mA, apis = matA(smali_df)
    if not (test_df is None):
        mA_test = matAtest(test_df, apis)
    else:
        mA_test = None
    mB = matB(smali_df)
    mP = matP(apis)
    return mA, mB, mP, mA_test
