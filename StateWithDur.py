'''
Created on Nov 10, 2014

@author: joro
'''
import os
import sys
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
htkModelParser = os.path.join(parentDir, 'htk2s3')

sys.path.append(htkModelParser )

from htk_models import State

class StateWithDur(State):
    '''
    classdocs
    '''


    def __init__(self, mixtures):
        '''
        Constructor
        '''
        State.__init__(self, mixtures)
                                
    def setDuration(self, duration):
        self.duration = duration
    
    def setDurationInFrames(self, durationInFrames):
        self.durationInFrames = durationInFrames
        
        