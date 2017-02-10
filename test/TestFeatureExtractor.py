'''
Created on Jan 13, 2016

@author: joro
'''
from FeatureExtractor import loadMFCCs

def test_loadMFCCs():
    URI_noExt =   '/Users/joro/Documents/Phd/UPF/arias/laosheng-erhuang_04'
    withSynthesis = True
    loadMFCCs(URI_noExt, withSynthesis, 55, 58)


def test_htkmfcRead():
    URI_file = '/Users/joro/Documents/Phd/UPF/arias/laosheng-erhuang_04_0_2.mfc'
    HTKFeat_reader =  open(URI_file, 'rb')
    features = HTKFeat_reader.getall()
    print features.shape
    
if __name__ == '__main__':
    test_loadMFCCs()