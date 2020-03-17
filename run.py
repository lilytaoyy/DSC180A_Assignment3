import json
import sys
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
from src.data_ingestion import *
from src.feature_extraction import *
from src.baseline_model_training import *
from src.matrix_construction import *
from src.kernel import *
import warnings
#warnings.filterwarnings('ignore')

def load_params(jsonfile):
    with open(jsonfile) as f:
        params = json.load(f)
    return params

def main(commands):
    warnings.filterwarnings("ignore")

    data_params = 'config/data-params.json'
    test_params = 'config/test-params.json'

    if 'remove' in commands:
        shutil.rmtree('data',ignore_errors = True)
        shutil.rmtree('output',ignore_errors = True)

    if 'ingestion' in commands:
        print('--- loading parameters')
        params = load_params(data_params)
        sitemap = params['sitemap']
        out = params['path']
        sub = params['sub']
        num = params['num']
        cat = params['cat']
        malware_path = params['malware']

        print('--- downloading apps')
        appurl = get_app_urls(sitemap, cat, num)
        download_link(appurl, out, sub)

        print('--- cleaning disks')
        clean_disk(out)
        print('exit ingestion')

    if 'baseline' in commands:
        if not os.path.exists('output'):
            os.mkdir('output')
            
        print('--- loading parameters')
        params = load_params(data_params)
        sitemap = params['sitemap']
        out = params['path']
        sub = params['sub']
        num = params['num']
        cat = params['cat']
        malware_path = params['malware']

        print('--- collecting app paths')
        ben_paths = get_sub_dir(out + '/' + sub)
        mal_paths = get_malware_paths(malware_path, num*cat)

        print('--- starting feature extraction and EDA')
        benign_df = generate_df(ben_paths, 'benign')
        malware_df = generate_df(mal_paths, 'malware')
        app_df = pd.concat([benign_df, malware_df])
        app_df.to_csv(os.path.join('output', 'baseline_features.txt'))
        print('== baseline_feature.txt saved to ./output ==')

        app_df[app_df.num_api != 0].describe().to_csv(os.path.join('output', 'describe.txt'))
        print('== describe.txt saved to ./output ==')

        run_baseline(app_df)
        print('== baseline_result.txt saved to ./output ==')
        print('exit baseline')

    if 'HIN' in commands:
        print('--- loading parameters')
        if not os.path.exists('output'):
            os.mkdir('output')
            
        params = load_params(data_params)
        sitemap = params['sitemap']
        out = params['path']
        sub = params['sub']
        num = params['num']
        cat = params['cat']
        malware_path = params['malware']
        
        print('--- collecting app paths')
        ben_paths = get_sub_dir(out + '/' + sub)
        mal_paths = get_malware_paths(malware_path, num*cat)

        print('--- obtaining smali codes')
        benign_smali = all_smali(ben_paths)
        mal_smali = all_smali(mal_paths)

        ben_smali_df = pd.DataFrame(benign_smali)
        ben_smali_df['malware'] = 0
        mal_smali_df = pd.DataFrame(mal_smali)
        mal_smali_df['malware'] = 1

        entire = ben_smali_df.append(mal_smali_df, ignore_index = True)
        
        X = entire.drop('malware', axis = 1)
        y = entire.malware
        print('--- running kernels')
        run_kernel(X, y)

        print('== train_result.txt saved to ./output ==')
        print('== test_result.txt saved to ./output ==')
        print('exit HIN')

    if 'test-small-data' in commands:
        if not os.path.exists('output'):
            os.mkdir('output')

        params = load_params(test_params)
        sitemap = params['sitemap']
        out = params['path']
        sub = params['sub']
        num = params['num']
        cat = params['cat']
        malware_path = params['malware']
        
        print('Data Ingestion:')
        print('--- downloading apps')
        appurl = get_app_urls(sitemap, cat, num)
        download_link(appurl, out, sub)

        print('--- cleaning disks')
        clean_disk(out)
        
        print('Baseline:')
        print('--- collecting app paths')
        ben_paths = get_sub_dir(out + '/' + sub)
        mal_paths = get_malware_paths(malware_path, num*cat)
        
        print('--- starting feature extraction and EDA')
        benign_df = generate_df(ben_paths, 'benign')
        malware_df = generate_df(mal_paths, 'malware')
        app_df = pd.concat([benign_df, malware_df])
        app_df.to_csv(os.path.join('output', 'baseline_features.txt'))
        print('== baseline_feature.txt saved to ./output ==')

        app_df[app_df.num_api != 0].describe().to_csv(os.path.join('output', 'describe.txt'))
        print('== describe.txt saved to ./output ==')

        run_baseline(app_df)
        print('== baseline_result.txt saved to ./output ==')
        
        print('HIN:')
        print('--- obtaining smali codes')
        benign_smali = all_smali(ben_paths)
        mal_smali = all_smali(mal_paths)

        ben_smali_df = pd.DataFrame(benign_smali)
        ben_smali_df['malware'] = 0
        mal_smali_df = pd.DataFrame(mal_smali)
        mal_smali_df['malware'] = 1

        entire = ben_smali_df.append(mal_smali_df, ignore_index = True)
        
        X = entire.drop('malware', axis = 1)
        y = entire.malware
        print('--- running kernels')
        run_kernel(X, y)

        print('== train_result.txt saved to ./output ==')
        print('== test_result.txt saved to ./output ==')

        print('exit test-small-data')

if __name__ == "__main__":
    commands = sys.argv[1:]
    main(commands)