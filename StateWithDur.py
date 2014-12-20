'''
Created on Nov 10, 2014

@author: joro
'''
import os
import sys
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
htkModelParser = os.path.join(parentDir, 'htkModelParser')

sys.path.append(htkModelParser )

from htk_models import State

class StateWithDur(State):
    '''
    extends State with 
    - duration (in minimal_duration unit)
    - duration (in Frames)
    '''


    def __init__(self, mixtures):
        '''
        Constructor
        '''
        State.__init__(self, mixtures)
                                
    def setDurationInMinUnit(self, duration):
        ''' in MinUNIT'''
        
        self.duration = duration
    
    def setDurationInFrames(self, durationInFrames):
        self.durationInFrames = durationInFrames
        
    def getDurationInFrames(self):
        
        try: self.durationInFrames
        except NameError:
            sys.exit("no durationInframes assigned to state {} has no model assigned ", self.ID)
            
        return self.durationInFrames
        
        