'''
Created on Dec 8, 2014

@author: joro
'''

DEVIATION_IN_SEC = 0.1


# max  duration for silence state (with exp distrib.) in seconds.
MAX_SILENCE_DURATION = 1.0

class Parameters(object):
    '''
    classdocs
    '''
    

    def __init__(self, ALPHA,  ONLY_MIDDLE_STATE ):
        '''
        Constructor
        '''
        
        self.ALPHA = ALPHA
        
        self.ONLY_MIDDLE_STATE = ONLY_MIDDLE_STATE
        
        
     
        
        