- [Assignment #1: The Data](#assignment-1-the-data)
    - [Literature Review](#literature-review)
      - [Hindroid Paper](#hindroid-paper)
      - [Background and Problem Introduced](#background-and-problem-introduced)
      - [Data Used](#data-used)
    - [Data Design and Collection](#data-design-and-collection)
      - [Advantages](#advantages)
      - [Shortcomings](#shortcomings)
      - [Historical Context](#historical-context)
      - [Data Generating Process](#data-generating-process)
    - [Data Ingestion Process](#data-ingestion-process)
      - [Data Origination and Legality](#data-origination-and-legality)
      - [Privacy Concerns](#privacy-concerns)
      - [Data Schema](#data-schema)
      - [Pipeline](#pipeline)
      - [Applicability](#applicability)
- [Assignment #2: Cleaning and EDA](#assignment-2-cleaning-and-eda)
    - [Graph Definitions](#graph-definitions)
    - [EDA on Apps](#eda-on-apps)
    - [Baseline Classification Model](#baseline-classification-model)
        - [Observations](#observations)
- [Assignment #3: Hindroid Classification](#assignment-3-hindroid-classification)
    - [The Hindroid](#the-hindroid)
        - [Graph Description:](#graph-description)
        - [Metapath Description:](#metapath-description)
        - [Matrices Implementation Details:](#matrices-implementation-details)
        - [Precomputed Kernel SVM](#precomputed-kernel-svm)
        - [Replication Result](#replication-result)
    - [Conclusion](#conclusion)
    - [Future Work](#future-work)
    - [Reference](#reference)

# Assignment #1: The Data
### Literature Review
#### Hindroid Paper
[Hindroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf) research paper introduces in detail about the implementations of Hindroid, an intelligent Android malware detection system based on structured heterogeneous information network.

#### Background and Problem Introduced
As the use of smart phones experiencing a rapid growth in recent years and Android being the dominate phone type in the market, there are attackers who disseminate malware through maliciously written apps and launch those app on both Google’s official Android market and other third-party markets, which seriously threaten smart phone users. 

Due to the openness of the Android platform, protecting legitimate users from the attacks of malware is arduous, and the number of malicious software is up to 1/5 of the number of total software.  In the Hindroid paper, the authors investigate on the problem of detecting malwares by analyzing the different relationships between Application Programming Interface (API) calls of a variety of Android software and creating higher-level semantics from which.

#### Data Used
To systematically train their model, they obtain two datasets from Comodo Cloud Security Center. One sample set collects recent Android apps containing 1834 training Android apps obtained in one week of 2017 and 500 testing samples, with malware and benign apps roughly equally divided. The other larger sample set contains 30,000 Android apps obtained within the first month of 2017, with malware and benign apps equally divided as well. 


If there are any further question regarding details or Hindroid implementations, please refer directly to the [Hindroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf) paper (DOI:[10.1145/3097983.3098026](https://doi.org/10.1145/3097983.3098026)).

### Data Design and Collection

The data we use in replication of paper will consist of:

- Benign Android Application from [APKPure](http://apkpure.com)
- Malicious Android Application from our private source.

Benign software data will be downloaded through [APKPure](http://apkpure.com), a website that allows users to download `.apk` and `.xapk` files in order to install apps on Android devices from outside the Google Play Store.
Malwares will be provided to us from our private source to avoid unecessary damage to our devices and malicious propagation from online sources. 

The population of the data represents all software being published on [APKPure](http://apkpure.com) in recent years that we can obtain from `sitemap.xml`. It is relevant to the question addressed as we can sample selective credible up-to-date apks from the population, and thus is fairly reliable to use. 

#### Advantages
- The data we will use in the replication is appropriate to address the problem as it contains both benign Android apps and malware samples, together they simulate the datasets being used in the Hindroid paper.
- As addressed in the paper, the data is expected to be balanced, namely, benign apps and malwares in our data should be in equal amount to maximize the performance of the classification model. 
- Downloading benign software samples from [APKPure](http://apkpure.com) ensures greater chance of obtaining popular and trustworthy apps. [APKPure](http://apkpure.com) being a third-party platform provides selective apps while the official [Google Playstore](https://play.google.com/store?&utm_source=na_Med&utm_medium=hasem&utm_content=Jul0119&utm_campaign=Evergreen&pcampaignid=MKT-DR-na-us-1000189-Med-hasem-py-Evergreen-Jul0119-Text_Search_BKWS-id_100754_|EXA|ONSEM_kwid_43700045371544955&gclid=EAIaIQobChMI6ZX7g7eb5wIVFbvsCh0DjAVBEAAYASAAEgIoIvD_BwE) includes all Android apps. Having a not popular or untrustworthy app may bias the training process and affect the performance of ML model which will lead to a less acurate classification. 

#### Shortcomings
- One potential shortcoming of the data may be the lack of variety of categories of benign applications if we don’t designedly pick different types of apps on [APKPure](http://apkpure.com). Again, having similar apps may bias the model and results in lower accuracy.
- Or, as mentioned above, when selecting apps from [APKPure](http://apkpure.com), we may select unwelcome applications with few actual users,which is somewhat meaningless for our training.
- While our benign software samples are from online sources, which is updated frequently, our malware samples are not only limited but also from private database. We may have a small sample size of malware compare to that of benign ones, and our samples may not be up-to-date. Our model may not be able to detect the most updated malware.

#### Historical Context
Referring to [Data Used](#data-used), the data obtained in the Hindroid paper is from Comodo Cloud Security Center. Details are listed as following:


(1) The first sample set contains 1,834 training Android apps (920 of them are benign apps, while the other 914 apps are malware including the families of Lotoor, RevMob, Fakegupdt, and GhostPush, etc), and 500 testing samples (with the analysis by the anti-malware experts of Comodo Security Lab, 198 of them are labeled as benign and 302 of them are labeled as malicious). 
(2) The second dataset has larger sample collection containing 30,000 Android apps obtained within one month (Januray 2017), half of which are benign apps and the half are malicious apps.

#### Data Generating Process
We will first obtain `sitemap.xml` that includes all apks on [APKPure](http://apkpure.com). From which, we can download selective benign apks. To ensure the performance of our ML model, bengin apks will be carefully obtained by their popularity and category, and the amount will be aproximately the same to the number of malware samples we have. A list of apks with actual users and from a variety of categories will be downloaded from [APKPure](http://apkpure.com). Malicious Android apps will be obtains from our private source. 

Android apps are written in Java and compiled to Dalvik bytecode, and distributed in zipped files called apks, to be run on a phone. The bytecode is denoted with the `.dex` file suffix. Our sample apks will be decompiled and the dex files will be convert to Smali, a readable intermediate language that will be used for extracting API calls for further learning.



### Data Ingestion Process

#### Data Origination and Legality
Our data mainly originates from two sources, [APKPure](http://apkpure.com) for benign Android Applications and private database for malicious Android Applications. Since we will be using the private database upon holder's consent, thus legitimacy is affirmed. We will also be legally accessing benign apks as our projects are personal and for educational purpose. We will not be breaking the [Terms of use](https://apkpure.com/terms.html) on [APKPure](http://apkpure.com), stating that all apps and games are *for HOME or PERSONAL use ONLY*.

#### Privacy Concerns
As [APKPure](http://apkpure.com) is an online public platform and all software provided is open source, we will not get into issues regarding privacy. Nevertheless, we will encrypt developers' names in case of any information leakage.

#### Data Schema
In consideration of storage saving, we will only keep the necessary `AndroidManifest.xml` file along with the smali folder from each decomplied `.apk` file. Our observations are not stored in a regular tabular form as for traditional machine learning preprocess, and every unit corresponds to an actual Android application. The general schema is shown down below: 

  ``` source
  data/
  |-- Gmail/
  |   |-- Gmail.apk
  |   |-- Gmail/
  |   |   |-- AndroidManifest.xml
  |   |   |-- .smali/
  |-- Amazon/
  |   |-- Amazon.apk
  |   |-- Amazon/
  |   |   |-- AndroidManifest.xml
  |   |   |-- .smali/
  |-- ...
  ```

#### Pipeline

- From `sitemap.xml`, we first generate a `.csv` file consisting all basic information of applications for future sampling reference.
  - Our perferred sampling method is to sample equal amount by category, and the total samples should be approximately the same as the number of malware we hold. 
  - We may refer to the `.csv` file for other sampling methods if we do not reach a satisfying performance of the model by category only. 
- Having the chosen directory and number of apps to be sampled from each category, we construct `.json` configuration shown as below.
  ```json
  {
    "sitemap": "https://apkpure.com/sitemap.xml",
    "path": "data",
    "cat": 10,
    "num": 20,
    "malware": "/datasets/dsc180a-wi20-public/Malware/amd_data_smali"
    }
  ```
- The above step gives us a list of apk samples to be decompiled into `.dex`files using apktool, from which we obtain corresponding `AndroidManifest.xml` files and smali folders. 

#### Applicability
The above pipeline for scraping benign Android applications may be used for other online Android platforms, both official and third party. It is applicable as long as a `sitemap.xml` exists for the platform. However, if the platform is not public and opensource as [APKPure](http://apkpure.com), the scraping may lead to legal issues and privacy concerns. 

# Assignment #2: Cleaning and EDA
### Graph Definitions
There are four types of graph being used to model the android application as described in the [Hindroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf) paper. 

1. Graph A:
   - A graph demonstrates the relationship between Apps and API calls. If App<sub>i</sub> contains API<sub>j</sub>, then a<sub>ij</sub> = 1; otherwise, a<sub>ij</sub> = 0. All downloaded Apps will be run through and API calls within every App will be extracted. 
   - Nodes: Apps and API calls
   - Edges: If a<sub>ij</sub> = 1, node APP<sub>i</sub> and node API<sub>j</sub> are connected by an edge. Otherwise, no edge. 

2. Graph B
   - A graph demonstrates the relationship among APIs regarding their locations in the code blocks. If API<sub>i</sub> and API<sub>j</sub> co-exist in the same code block, then b<sub>ij</sub> = 1; otherwise, b<sub>ij</sub> = 0. This API relation will be extracted by identifying API calls between a pair of **“.method”** and **“.endmethod”**.
   - Nodes: API calls
   - Edges: If b<sub>ij</sub> = 1, node API<sub>i</sub> and node API<sub>j</sub> are connected by an edge. Otherwise, no edge.

3. Graph P
   - A graph demonstrates the relationship among APIs regarding the packages they belong to. If API<sub>i</sub> and API<sub>j</sub> are with the same package name, then p<sub>ij</sub> = 1; otherwise, p<sub>ij</sub> = 0. This relation will be extracted by identifying the package name before **"-->"** in every call. 
   - Nodes: API calls
   - Edges: If p<sub>ij</sub> = 1, node API<sub>i</sub> and node API<sub>j</sub> are connected by an edge. Otherwise, no edge.

4. Graph I
   - A graph demonstrates the relationship among APIs regarding the invoice methods they use. If API<sub>i</sub> and API<sub>j</sub> use the same invoke method, then i<sub>ij</sub> = 1; otherwise, i<sub>ij</sub> = 0. This relation will be extracted by indentifying the method being used by every API among a total of five methods -- *invoke-static, invoke-virtual, invoke-direct, invoke-super, and invoke-interface*.
   - Node: API calls
   - Edges: If i<sub>ij</sub> = 1, node API<sub>i</sub> and node API<sub>j</sub> are connected by an edge. Otherwise, no edge.

### EDA on Apps

We will perform EDA on a small dataset first then on a large dataset.
1. We sampeld 50 benign Apps on [APKPure](http://apkpure.com) equally distributed across 10 categories, decompiled, and cleaned to `AndroidManifest.xml` and `.smali`.
Equal amount of malware is also sampled from our private database.
We will be performing feature extraction and EDA over the 100 apps (50 benign / 50 malware).

2. We then sampeld ~250 benign Apps on [APKPure](http://apkpure.com) equally distributed across 10 categories, decompiled, and cleaned to `AndroidManifest.xml` and `.smali`.
Equal amount of malware is also sampled from our private database.
We will be performing feature extraction and EDA over the ~500 apps (~50 benign / 50 malware).

**Feature Extracted:**
- num_code_block: number of code blocks per App
- num_uni_block: number of unique code blocks per App
- num_api: number of API calls per App
- num_uni_api: number of unique API calls per App
- num_package: number of packages used per App
- num_uni_package: number of unqiue packages used per App
- num_invoke: number of invoke methods used per App

1. Small dataset:
   Every App on average has 68039 API calls and 13227 unique API calls, 20339 code blocks and 19240 unique code block (code blocks are mostly unique), and on average uses 69554 packages.
   Number of APIs only appear once is 295829.When metapath entries gets too large, this data can be helpful by removing all API calls appear only once.
<br />
   Detailed describe DataFrame is shown below:
   ![alt text](small_describe.png)
<br />
   Histograms:
   All APPs:
   ![alt text](small_all_hist.png)
   Benign APPs:
   ![alt text](small_benign_hist.png)
   Malware:
   ![alt text](small_malware_hist.png)

2. Large dataset:
   Every App on average has 13705 API calls and 73037 unique API calls, 19736 code blocks and 20801 unique code block (code blocks are mostly unique), and on average uses 74583 packages.
   Detailed describe DataFrame is shown below:
   ![alt text](large_describe.png)

   Histograms:
   All APPs:
   ![alt text](large_all_hist.png)
   Benign APPs:
   ![alt text](large_benign_hist.png)
   Malware:
   ![alt text](large_malware_hist.png)

### Baseline Classification Model
We use Logistic Regression, Random Forest, and Gradient Boost Classifier to train our models based on the features extracted above and classify whether an App is benign or malware.

1. Small dataset baseline result:
   ![alt text](small_baseline.png)
   From the result dataframe, we can observe that the performace of logistic regression is not as good as the other two, and gradient boost classifier outperforms with an accuracy score of 0.97.
<br />
2. Large dataset baseline result:
   ![alt text](large_baseline.png)
   From the result dataframe, we can observe that the performace of logistic regression is not as good as the other two. Random forest and gradient boost both have high accuracy and low false negative rate.

##### Observations
Logistic regression is not an ideal model among the three classifiers we trained. Random forest is overall robust as it has similar accuracy ~0.92 and false negative rate ~0.58 on both small and large dataset. However, gradient boost's performance gets worse as dataset gets larger.
The metric important is the number of false negative divided by number of total apps, noted as fnr, as we care more about the missing detections of malware apps.

# Assignment #3: Hindroid Classification
### The Hindroid
The Hindroid approach introduced in [Hindroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf) uses heterogeneous information network to capture the relationships between apps and apis or between apis and apis. The corresponding relationships are extracted as features and saved as adjacency matrices. From these matrices, various matapaths are computed and fed into the Support Vector Machine classifier as kernels. 
As we can observe from EDA and baseline result, api calls almost make up Android app and are keys to successful classification. Since our problem is to investigate malicious attack hiding in Android apps, which is different from many regular classifying problems, the Hindroid approach is an intuitive and useful way for classifying malware from benign apps as it not investigate only apps/apis alone but also the assoiciations between api calls in different places of the entire app code. It utilizes characters of API calls, code blocks, and packages to calculate the similarities between apps.
<br />
We use Hindroid approach to construct out feature matrices A, B, and P.(Details can be found in above [Graph Definitions](#graph-definitions)). 

##### Graph Description:
- Graph A:
   - A graph demonstrates the relationship between Apps and API calls. 
   - Nodes: Apps and API calls
   - Edges: If a<sub>ij</sub> = 1, node APP<sub>i</sub> and node API<sub>j</sub> are connected by an edge. Otherwise, no edge. 

- Graph B
   - A graph demonstrates the relationship among APIs regarding their locations in the code blocks. 
   - Nodes: API calls
   - Edges: If b<sub>ij</sub> = 1, node API<sub>i</sub> and node API<sub>j</sub> are connected by an edge. Otherwise, no edge.

- Graph P
   - A graph demonstrates the relationship among APIs regarding the packages they belong to.
   - Nodes: API calls
   - Edges: If p<sub>ij</sub> = 1, node API<sub>i</sub> and node API<sub>j</sub> are connected by an edge. Otherwise, no edge.

##### Metapath Description:
- **AA^T**:
  The similarity between apps by number of API calls in common.

- **ABA^T**:
  The similarity between apps by number of API calls in the same code block.

- **APA^T**:
  The similarity between apps by number of API calls using the same package.

- **APBP^T A^T**:
  The similarity between apps by number of API calls in the same code block as well as using the same package.

##### Matrices Implementation Details:
  - A Matrix Implementation:
  From a dataframe with index as individual app and column as all smali code within the app, we extract all API calls by app, which is stored as a dataframe, and use a MultiLabelBinarizer to fit_transform the dataframe to get A, and we also save the class of all unique API calls for later use.

  -  B Matrix Implementation:
  From a dataframe with index as individual app and column as all smali code within the app, we extract all code blocks as well as all API calls in each block, store the adjacency information among APIs in dictionary, and finally use MultiLabelBinarizer to fit_transform the value of the dictionary.

  -  P Matrix Implementation:
  From the saved unique API calls we get in matrix A construction, we extract package from those calls respectively. We then save API calls with their according package into a datafrme, groupby package, store the adjacency information among APIs in dictionary, and finally use MultiLabelBinarizer to fit_transform the value of the dictionary.

##### Precomputed Kernel SVM
After the construction of matrices, we then compute several kernel metapaths for precomputed SVM model training and testing.
 - Training kernels:
   AA^T, ABA^T, APA^T, APBP^T A^T
 - Test kernels:
   A_testA_train^T, A_testBA_train^T, A_testPA_train^T, A_testPBP^T A_train^T

##### Replication Result
- Training Result:
  ![alt text](HIN_train.png)
- Test Result:
  ![alt text](HIN_test.png)

From the result dataframe, we can observe that the performace of SVM using `AA^T` metapath kernel is the best, following is `APA^T`. Metapaths associating with matrix B are not as good in accuracy but always have low false netative rate as the model tend to predict 1 / malware.

### Conclusion
From our EDA and baseline model, we observe that malware, at least those in our private database, tend to have fewer API calls on average, which explains the out performances of random forest and gradient boost classifiers using basic features. However, as we stressed in [EDA on Apps](#eda-on-apps), one error metric we consider most important is the false netative rate as we don't want to miss the detection of malware, and our baseline model having the rates ~0.05 is not as ideal. While the baseline model using basic features has a high accuarcy score, it still has a risk of leaving out a few malicious apps. Given that said, our Hindroid model has much lower false negative rates ~0.01, which is more ideal.

From our metapath kernels, we observe that `AA^T` outperforms among all kernels and have the highest accuracy score. However, metapaths associated with matrix B, including `ABA^T` and `APBP^TA^T`, have lower accuracies. 

### Future Work
In order to improve the model, we can (i)improve the model computation efficiency to train more data, (ii)gather more recent detected malware into our database, (iii)assign weights to metapaths according to their overall performances and fit into a multikernel classifier, and (iv)try different graph embedding methods.

### Reference
All replication in this study is in reference to: [Hindroid](https://www.cse.ust.hk/~yqsong/papers/2017-KDD-HINDROID.pdf)
