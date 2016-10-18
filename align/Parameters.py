'''
Created on Dec 8, 2014

@author: joro
'''

class Parameters(object):
    '''
    classdocs
    '''
    
    WRITE_TO_FILE = False
    

    def __init__(self, ALPHA,  ONLY_MIDDLE_STATE ):
        '''
        Constructor
        '''
        
        self.ALPHA = ALPHA
        
        self.ONLY_MIDDLE_STATE = ONLY_MIDDLE_STATE
        
     
        
        