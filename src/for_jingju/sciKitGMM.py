'''
Created on Nov 29, 2015

@author: joro
'''

class SciKitGMM(object):
    '''
    convenienve class wrapper for scikit-learns gmm model
    '''


    def __init__(self, gmm, modelName):
        '''
        Constructor
        '''
        self.gmm = gmm
        self.modelName = modelName
        