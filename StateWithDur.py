'''
Created on Nov 10, 2014

@author: joro
'''
import os
import sys
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

htkModelParser = os.path.join(parentDir, 'htkModelParser')


sys.path.append(htkModelParser )

from htk_models import State

class StateWithDur(State):
    '''
    extends State with 
    - durationInMinUnit (in minimal_duration unit)
    - durationInMinUnit (in Frames)
    '''


    def __init__(self, mixtures, phonemeName, idxInPhoneme):
        '''
        Constructor
        '''
        State.__init__(self, mixtures)
        self.phonemeName = phonemeName
        self.idxInPhoneme  = idxInPhoneme
                                
    def setDurationInMinUnit(self, duration):
        ''' in MinUNIT'''
        
        self.durationInMinUnit = duration
    
    def setDurationInFrames(self, durationInFrames):
        self.durationInFrames = durationInFrames
        
    def getDurationInFrames(self):
        
        try: self.durationInFrames
        except NameError:
            sys.exit("no durationInframes assigned to state {} has no model assigned ", self.ID)
            
        return self.durationInFrames
    
    def __str__(self):
        return self.phonemeName + "_"  + str(self.idxInPhoneme)
        
        