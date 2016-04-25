'''
Created on Nov 29, 2015

@author: joro
'''
from sklearn.mixture.gmm import GMM

class SciKitGMM(object):
    '''
    classdocs
    '''


    def __init__(self, gmm, modelName):
        '''
        Constructor
        '''
        self.gmm = gmm
        self.modelName = modelName
        