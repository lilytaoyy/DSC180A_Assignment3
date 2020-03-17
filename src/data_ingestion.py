import requests
import re
import glob, os, shutil
import gzip
import random
from bs4 import BeautifulSoup
import json
import pandas as pd
import subprocess

#Write code that creates a list of Android Apps on 
#apkpure that will make up the benign apps in your training set. 
def get_submap_xmls(sitemap):
    '''
    Given the sitemap (i.e. APKPure), retrieve all submaps urls from the whole sitemap
    :param sitemap: url of sitemap
    :return: list of submap urls
    '''
    resp = requests.get(sitemap)
    soup = BeautifulSoup(resp.content, 'xml')
    url = soup.find_all('loc') 
    result = []
    for link in url:
        result += [link.get_text()]
    return result

def cat_lst(link_lst):
    '''
    Get a list of categories by scraping xml list from submaps of sitemap.xml 'https://apkpure.com/sitemap.xml'
    :param link_lst: list of submap urls
    :return: list of categories
    '''
    cat = []
    reg = '(?<=sitemaps\/)(.*)(?=\-\d)|(?<=sitemaps\/)(.*)(?=\.xml)'
    for xml in link_lst:
        cat += [re.search(reg,xml).groups()[1]]
    return [i for i in cat if i]

def sample_by_cat(categories):
    '''
    Given categories, find the soup of all decompressed category gz files
    :param categories: list of categories
    :return: a list of soups of all decompressed category gz files
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
    :param sitemap: sitemap url
    :param cat: category, can be 'all', int, or a list of category strings, function will perform accordingly
    :param number: number of links to download by category
    :return: list of app links to be downloaded
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
    :param app_link: list of app links to be downloaded
    :param outpath: outpath of downloads
    :param cat: category
    :return: none
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
    '''
    Clean each downloaded app files to keep only smali file and AndroidManifest.xml
    :param app_path: downloaded app file paths
    :return: none
    '''
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
    clean the outpath containing all downloaded apps by performing clean_folder function to keep only
    smali file and AndroidManifest.xml
    :param out: outpath of downloads
    :return: none
    '''

    subs = os.listdir(out)
    for s in subs:
        if os.path.isdir(out + '/' + s):
            files = os.listdir(out + '/' + s)
            for fi in files:
                clean_folder(out + '/' + s + '/' + fi)
        else:
            os.remove(out + '/' + s)

