import re
import itertools
import os
import pandas as pd
import requests
import glob, os
import gzip
import numpy as np
from bs4 import BeautifulSoup
import json
from os import listdir
from os.path import isfile, join
from multiprocessing import Pool

#feature extraction
def get_malware_paths(malware_path, num):
    '''
    Get malware app paths by given number
    :param malware_path: the main malware path on server
    :param num: number of apps to retrieve
    :return: list of malware app paths
    '''

    paths = []
    count = 0
    for d, dirs, files in os.walk(malware_path):
        for subd in dirs:
            if subd == 'smali' and count < num:
                paths.append(d)
                count += 1
            if count > num:
                break
    return paths

def get_sub_dir(mypath):
    '''
    Find all sub-directory paths from given path
    :param mypath: main path
    :return: list of sub-directory paths
    '''

    return [os.path.join(mypath, o) for o in os.listdir(mypath) 
                    if os.path.isdir(os.path.join(mypath,o))]

def all_smali(sub_dir):
    '''
    Extract all smali code from give list of directories
    :param sub_dir: list of sub directories
    :return: all smali code extracted from directories
    '''
    pool = Pool(os.cpu_count())
    smali_by_app = pool.map(app_to_smali, sub_dir)
    pool.close()

    return smali_by_app

def app_to_smali(path):
    '''
    From the file path of an app, get all smali text
    :param path: single app path
    :return: all smali code extracted from the app
    '''

    smalis = []
    for d, dirs, files in os.walk(path + '/smali/'):
        for f in files:
            if f.endswith('smali'):
                smalis.append(os.path.join(d, f))
    smali_text = [open(s, 'r').read() for s in smalis]
    return '\n'.join(smali_text)

def by_code_block(smalitxt):
    '''
    Extract code block from smali text
    :param smalitxt: a large chunck of smali code
    :return: total number of unique code blocks, total number of code blocks, list of all code blocks
    '''
    pattern = re.compile('\.method([\S\s]*?)\.end method')
    code_blocks = re.findall(pattern, smalitxt)
    return len(set(code_blocks)), len(code_blocks), code_blocks#not unique!!

def by_api(smalitxt):
    '''
    Extract apis from smali text
    :param smalitxt: a large chunck of smali code
    :return: total number of unique apis, total number of apis, list of all apis
    '''
    pattern = re.compile('invoke-\w+ {.*}, (.*?)\\(')
    api = re.findall(pattern, smalitxt)
    return len(set(api)), len(api), api#not unique!!

def by_package(smalitxt):
    '''
    Extract packages used from smali text
    :param smalitxt: a large chunck of smali code
    :return: total number of unique packages, total number of all packages
    '''
    packages = re.findall('invoke-.*? {.*?}. (\[*[ZBSCFIJD]|\[*L[\w\/$-]+;)->', smalitxt)
    total = len(packages)
    return len(set(packages)), total

def by_invoke(smalitxt):
    '''
    Extract invoke methods from smali text
    :param smalitxt: a large chunck of smali code
    :return: total number of all invoke methods used, list of invoke methods
    '''
    invokes = re.findall('invoke-(\w+)(?:\/range)? {', smalitxt)
    total = len(invokes)
    return total, invokes

def single_app_feature(app):
    i = app_to_smali(app)
    block = by_code_block(i)
    api = by_api(i)
    package = by_package(i)
    invoke = by_invoke(i)

    num_uni_block = block[0]
    num_code_block = block[1]
    num_uni_api = api[0]
    num_api = api[1]
    num_uni_package = package[0]
    num_package = package[1]
    num_invoke = invoke[0]
    
    return [num_uni_block, num_code_block, num_uni_api, num_api, num_uni_package, num_package, num_invoke]
        
def generate_df(path, cat = 'benign'):
    '''
    Generate a baseline feature dataframe of benign apps
    :param path: path of apps
    :return: a dataframe containing all extracted features
    '''
    pool = Pool(os.cpu_count())
    mat = pool.map(single_app_feature, path)
    pool.close()
    
    if cat == 'benign':
        category = 0
    elif cat == 'malware':
        category = 1
    else:
        category = cat
    df = pd.DataFrame(mat, columns = ['num_code_block', 'num_uni_block', 'num_api', 'num_uni_api', 'num_package', 'num_uni_package', 'num_invoke'])
    df['category'] = category
    return df

def generate_malware(path, cat = 'malware'):
    '''
    Generate a baseline feature dataframe of malware
    :param path: list of malware app paths
    :param cat: default set to malware
    :return: a dataframe containing all extracted features
    '''
    num_code_block = []
    num_uni_block = []
    num_api = []
    num_uni_api = []
    num_package = []
    num_uni_package = []
    num_invoke = []
    for app in path:
        i = app_to_smali(app)
        block = by_code_block(i)
        api = by_api(i)
        package = by_package(i)
        invoke = by_invoke(i)

        num_uni_block += [block[0]]
        num_code_block += [block[1]]
        num_uni_api += [api[0]]
        num_api += [api[1]]
        num_uni_package += [package[0]]
        num_package += [package[1]]
        num_invoke += [invoke[0]]
    df = pd.DataFrame({'num_code_block': num_code_block, 
                       'num_uni_block': num_uni_block, 'num_api': num_api, 
                       'num_uni_api': num_uni_api, 'num_package': num_package,
                       'num_uni_package': num_uni_package, 'num_invoke': num_invoke,
                       'category': 1})
    return df

