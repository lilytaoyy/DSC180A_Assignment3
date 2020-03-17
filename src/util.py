import requests
import re
import itertools
import os
import pandas as pd
import requests
import glob, os, shutil
import gzip
from bs4 import BeautifulSoup
import json
import subprocess
from os import listdir
from os.path import isfile, join
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier,GradientBoostingClassifier
from sklearn.preprocessing import OneHotEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import confusion_matrix


#Write code that creates a list of Android Apps on 
#apkpure that will make up the benign apps in your training set. 
def get_submap_xmls(sitemap):
    resp = requests.get(sitemap)
    soup = BeautifulSoup(resp.content, 'xml')
    url = soup.find_all('loc') 
    result = []
    for link in url:
        result += [link.get_text()]
    return result

def cat_lst(link_lst):
    '''
    Get a list of categories by scraping xml list from sitemap.xml 'https://apkpure.com/sitemap.xml'
    '''
    cat = []
    reg = '(?<=sitemaps\/)(.*)(?=\-\d)|(?<=sitemaps\/)(.*)(?=\.xml)'
    for xml in link_lst:
        cat += [re.search(reg,xml).groups()[1]]
    return [i for i in cat if i]

def sample_by_cat(categories):
    '''
    Given categories, find the soup of all decompressed category gz files
    '''
    soups = []
    for c in categories:
        url = 'https://apkpure.com/sitemaps/{}.xml.gz'.format(c)
        try:
            r = requests.get(url)
        except:
            url = 'https://apkpure.com/sitemaps/{}.xml.gz'.format(c+'-1')
            r = requests.get(url)
    
        data = gzip.decompress(r.content)
        soup = BeautifulSoup(data,features = 'lxml')
        soups.append(soup)
    return soups

def get_app_urls(sitemap, cat, number):
    '''
    Obtain the a selective number of download links for apps by category
    '''
    xmls = get_submap_xmls(sitemap)
    
    if cat == 'all':
        categories = cat_lst(xmls)
    elif type(cat) == int:
        categories = random.choices(cat_lst(xmls), k = cat)
    else:
        categories = cat
        
    soups = sample_by_cat(categories)
    apps = []
    for soup in soups:
        count = 0
        sp = soup.find_all(re.compile('loc')) 
        lst = [] 
        for i in sp:
            if re.match('<loc>', str(i)) and count < number:
                try:
                    lst += [re.search('(?<=<loc>)(https:\/\/apkpure.com\/.*?\/.*[a-zA-Z\d].*)(?=<\/loc>)', str(i)).group()] #find all urls storec in loc
                    count += 1
                except:
                    continue
        apps += lst
    return apps

#Given an android app on apkpure, download the apk, 
#decompile the apk to Smali code.

def download_link(app_link, outpath, cat):
    '''
    From the app link, find the download page, obtain the download link
    '''
    if not os.path.exists(outpath):
        os.mkdir(outpath)
    if not os.path.exists(outpath + '/' + cat):
        os.mkdir(outpath + '/' + cat)

    for url in app_link:
        download_link = url + '/download?from=details'
        r1 = requests.get(download_link)
        soup = BeautifulSoup(r1.text)
        try:
            download_link_file = soup.find('div',attrs = {"class":"fast-download-box fast-bottom"}).find('p',attrs = {'class':'down-click'}).find('a',href = True)['href']
        except:
            continue
        r2 = requests.get(download_link_file)
        apkfile = r2.content
        complete_name = os.path.join(outpath+'/'+cat+'/', url.split('/')[-1]+".apk")
        out_name = os.path.join(outpath+'/'+cat+'/', url.split('/')[-1])
        with open(complete_name, 'wb') as fh:
            fh.write(apkfile)
        subprocess.call(['apktool', 'd', outpath+'/'+cat+'/'+url.split('/')[-1]+".apk", '-o',out_name])
    
#Given a directory contain Smali code (as returned from running apktool), 
#organize it on disk
def clean_folder(app_path):
    if '.DS_Store' not in app_path:
        if os.path.isdir(app_path):
            subs = os.listdir(app_path)
            for s in subs:
                if s not in ['smali', 'AndroidManifest.xml']:
                    path = app_path+'/'+s
                    if os.path.isdir(path):
                        shutil.rmtree(path)
                    elif os.path.isfile(path):
                        os.remove(path)
        else:
            os.remove(app_path)
            
def clean_disk(out):
    '''
    keep only smali folder and AndroidManifest.xml
    '''
    subs = os.listdir(out)
    for s in subs:
        if os.path.isdir(out + '/' + s):
            files = os.listdir(out + '/' + s)
            for fi in files:
                clean_folder(out + '/' + s + '/' + fi)
        else:
            os.remove(out + '/' + s)


#feature extraction
def app_to_smali(path):
    '''
    from the file path of an app, get all smali text
    '''
    smalis = []
    for d, dirs, files in os.walk(path + '/smali/'):
        for f in files:
            if f.endswith('smali'):
                smalis.append(os.path.join(d, f))
    smali_text = [open(s, 'r').read() for s in smalis]
    return '\n'.join(smali_text)

def by_code_block(smalitxt):
    pattern = re.compile('\.method([\S\s]*?)\.end method')
    code_blocks = re.findall(pattern, smalitxt)
    return len(set(code_blocks)), len(code_blocks), code_blocks#not unique!!

def by_api(smalitxt):
    pattern = re.compile('invoke-\w+ {.*}, (.*?)\\(')
    api = re.findall(pattern, smalitxt)
    return len(set(api)), len(api), api#not unique!!

def by_package(smalitxt):
    packages = re.findall('invoke-.*? {.*?}. (\[*[ZBSCFIJD]|\[*L[\w\/$-]+;)->', smalitxt)
    total = len(packages)
    return len(set(packages)), total

def by_invoke(smalitxt):
    invokes = re.findall('invoke-(\w+)(?:\/range)? {', smalitxt)
    total = len(invokes)
    return total, invokes

def list_package(apis):
    packages = []
    for api in apis:
        pac = api_to_package(api)
        packages += [pac]
    return packages

def list_invoke(apis):
    invokes = []
    for api in apis:
        ivk = api_to_invoke_method(api)
        invokes += [ivk]
    return invokes

def api_to_package(api):
    pattern = re.compile('invoke-.*? {.*?}. (\[*[ZBSCFIJD]|\[*L[\w\/$-]+;)->')
    package = re.search(pattern, api)
    return package[1]

def api_to_invoke_method(api):
    pattern = re.compile('invoke-(\w+)(?:\/range)? {')
    invoke = re.search(pattern, api)
    return invoke[1]

def all_smali(mypath):
    names = os.listdir(mypath)
    names.remove('.DS_Store')
    sub_dir = [os.path.join(mypath, o) for o in os.listdir(mypath) 
                    if os.path.isdir(os.path.join(mypath,o))]
    smali_by_app = []
    for i in sub_dir:
        smali_by_app += [app_to_smali(i)]
    return smali_by_app

def generate_df(out, cat):
    names = os.listdir(out + '/' + cat)
    num_code_block = []
    num_uni_block = []
    num_api = []
    num_uni_api = []
    num_package = []
    num_uni_package = []
    num_invoke = []
    most_freq_package = []
    for app in names:
        i = app_to_smali(out + '/' + cat + '/' + app)
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
    df = pd.DataFrame({'app_names': names, 'num_code_block': num_code_block, 
                       'num_uni_block': num_uni_block, 'num_api': num_api, 
                       'num_uni_api': num_uni_api, 'num_package': num_package,
                       'num_uni_package': num_uni_package, 'num_invoke': num_invoke,
                       'category': cat})
    return df[df['app_names']!='.ipynb_checkpoints']

#training
def one_hot():
    cat_feat = ['most_freq_package']
    cat_trans = Pipeline(steps=[
        ('onehot', OneHotEncoder())
        ])
    return ColumnTransformer(transformers=[('cat', cat_trans,cat_feat)])

def Logistic_Regression(df, pre):
    pipe = Pipeline(steps=[('preprocessor', pre),
                       ('clf', LogisticRegression())
                       ])
    X = df.drop('malware', 1)
    y = df.malware
    
    pipe.fit(X,y)
    y_pred = pipe.predict(X,y)
    tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()

    return fn/(tn+fp+fn+tp)

def Random_Forest(df, pre):
    pipe = Pipeline(steps=[('preprocessor', pre),
                       ('clf', RandomForestClassifier(max_depth=2, random_state=0))
                       ])
    X = df.drop('malware', 1)
    y = df.malware
    
    pipe.fit(X,y)
    y_pred = pipe.predict(X,y)
    tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()

    return fn/(tn+fp+fn+tp)

def GBC(df, pre):
    pipe = Pipeline(steps=[('preprocessor', pre),
                       ('clf', GradientBoostingClassifier())
                       ])
    X = df.drop('malware', 1)
    y = df.malware
    
    pipe.fit(X,y)
    y_pred = pipe.predict(X,y)
    tn, fp, fn, tp = confusion_matrix(y, y_pred).ravel()

    return fn/(tn+fp+fn+tp)



#Matrix Construction
def A(smali_df):
    apis_by_app = smali_df.apply(extract_api, axis = 1)
    mlb_A = MultiLabelBinarizer(sparse_output = True)
    A = mlb_A.fit_transform(apis_by_app)
    apis = mlb_A.classes_
    return A, apis

def B(smali_df):
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
    
    api_from_block_df[0].dropna().apply(extract_api_from_blocks)
    mlb_b = MultiLabelBinarizer(sparse_output = True)
    B = mlb_b.fit_transform(B_dic.values())
    return B

def P(apis):
    P_dic = {}
    api_df = pd.DataFrame({'apis': apis})
    api_df['package'] = api_df['apis'].apply(extract_package)
    api_by_pac = api_df.groupby('package').apis.apply(set).to_frame().reset_index().apis
    def extract_api_package(x):
        for api in x:
            if not api in P_dic.keys():
                P_dic[api] = x
            else:
                P_dic[api] = P_dic[api].union(x)
    api_by_pac.apply(extract_api_package)
    mlb_p = MultiLabelBinarizer(sparse_output = True)
    P = mlb_p.fit_transform(P_dic.values())
    return P