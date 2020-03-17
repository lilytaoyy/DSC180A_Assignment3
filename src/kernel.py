from sklearn.metrics import confusion_matrix
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.preprocessing import MinMaxScaler
import numpy as np
from src.matrix_construction import *

def kernel_train(A, B, P):
    '''
    Obtain a list of training kernels / metapaths
    :param A: matrix A
    :param B: matrix B
    :param P: matrix P
    :return: list of training metapaths (AA^T, ABA^T, APA^T, APBP^TA^T)
    '''
    return [A.dot(A.T), A.dot(B).dot(A.T), A.dot(P).dot(A.T), A.dot(B).dot(P).dot(B).dot(A.T)]

def kernel_test(A_train, A_test, B, P):
    '''
    Obtain a list of test kernels / metapaths
    :param A_train: matrix A
    :param A_test: matrix A test
    :param B: matrix B
    :param P: matrix P
    :return: list of test metapath (AtestA^T, AtestBA^T, AtestPA^T, AtestPBP^TA^T)
    '''
    return [A_test.dot(A_train.T), A_test.dot(B).dot(A_train.T), A_test.dot(P).dot(A_train.T), A_test.dot(P).dot(B).dot(P.T).dot(A_train.T)]

def compute_metrics(mat):
    '''
    Compute accuracy and false negative rate based on given confusion matrix
    :param mat: confusion matrix
    :return: list of confusion matrix + accuracy score + fn rate
    '''
    return mat + [(mat[0]+mat[3])/sum(mat), mat[2]/(mat[2]+mat[3])]

def SVM_result(X_train, X_test, y_train, y_test):
    '''
    Feed data to SVM classifier, fit and predict, and obtain both training and test error metrics
    :param X_train: feature to be trained
    :param X_test: feature to be tested
    :param y_train: training label
    :param y_test: test label
    :return: training and test error metrics
    '''
    svc = SVC(kernel='precomputed')
    svc.fit(X_train, y_train)
    y_pred_te = svc.predict(X_test)
    y_pred_tr = svc.predict(X_train)
    test = list(confusion_matrix(y_test, y_pred_te).ravel())
    train = list(confusion_matrix(y_train, y_pred_tr).ravel())
    return {'train': compute_metrics(train), 'test': compute_metrics(test)}

def save_matrices(mat, path):
    '''
    Saving matrix to local path
    :param mat: matrix to be saved
    :param path: path location of saving file
    :return: none
    '''
    sparse = scipy.sparse.csc_matrix(mat)
    scipy.sparse.save_npz(path, sparse)
    
def run_kernel(X, y):
    '''
    Run the entire kernel including matrices construction and saving, kernel construction, SVM training, and result saving
    :param X: feature matrix
    :param y: label
    :return: none
    '''
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, shuffle=True)
    print('Matrices construction:')
    print('--- start')
    mA, mB, mP, mAtest= A_B_P(X_train, X_test)
    print('--- saving matrics')
    if not os.path.exists('output'):
        os.mkdir('output')
    save_matrices(mA, 'output/A.npz')
    save_matrices(mB, 'output/B.npz')
    save_matrices(mP, 'output/P.npz')
    save_matrices(mAtest, 'output/A_test.npz')
    print('--- Done!')
    
    print('Kernel construction:')
    print('--- start')
    kernels_train = kernel_train(mA, mB, mP)
    kernels_test = kernel_test(mA, mAtest, mB, mP)
    print('--- Done!')
    
    print('SVM training:')
    print('--- start')
    train = []
    test = []

    result0 = SVM_result(kernels_train[0].todense(), kernels_test[0].todense(), y_train, y_test)
    train.append(result0['train'])
    test.append(result0['test'])
    print('25%')
    scaling = MinMaxScaler(feature_range=(-1,1)).fit(kernels_train[1].todense())
    X_train = scaling.transform(kernels_train[1].todense())
    X_test = scaling.transform(kernels_test[1].todense())
    result1 = SVM_result(X_train, X_test, y_train, y_test)
    train.append(result1['train'])
    test.append(result1['test'])
    print('50%')
    result2 = SVM_result(kernels_train[2].todense(), kernels_test[2].todense(), y_train, y_test)
    train.append(result2['train'])
    test.append(result2['test'])
    print('75%')
    scaling = MinMaxScaler(feature_range=(-1,1)).fit(kernels_train[3].todense())
    X_train = scaling.transform(kernels_train[3].todense())
    X_test = scaling.transform(kernels_test[3].todense())
    last = SVM_result(X_train, X_test, y_train, y_test)
    train.append(last['train'])
    test.append(last['test'])
    print('100%')

    print('--- saving result metrics')
    HIN_train = pd.DataFrame(train,index = ['AA^t', 'ABA^t', 'APA^t', 'APBP^tA^t'], columns=['tn', 'fp', 'fn', 'tp', 'acc', 'fnr'])
    HIN_test = pd.DataFrame(test,index = ['AA^t', 'ABA^t', 'APA^t', 'APBP^tA^t'], columns=['tn', 'fp', 'fn', 'tp', 'acc', 'fnr'])
    
    HIN_train.to_csv(os.path.join('output', 'train_result.txt'))
    HIN_test.to_csv(os.path.join('output', 'test_result.txt'))
    print('--- Finished all kernel tasks!')
