'''
Created on Oct 8, 2014

@author: joro
'''
from Phonetizer import Phonetizer
import sys
import numpy
class Phoneme:
    def __init__(self, phonemeID):
        self.ID = phonemeID;
        self.durationInMinUnit = None;
        self.durationInNumFrames = None;
        self.numFirstState = -1
    
    def setbeginTs(self, beginTs):
        '''
        begin ts from annotation
        '''
        self.beginTs = beginTs
            
    def setNumFirstState(self, numFirstState):
            self.numFirstState = numFirstState
        

    def setDurationInNumFrames(self, dur):
        self.durationInNumFrames =    dur; 
      
    
    def setHTKModel(self, hmmModel):
        self.htkModel = hmmModel
    
#     def getStates(self):
#         try: self.htkModel
#         except NameError:
#             sys.exit(" phoneme {} has no model assigned ", self.ID)
#         
#         return self.htkModel.states
        
    def getNumStates(self):
        try: self.htkModel
        except NameError:
            sys.exit("cannot get numsttes. phoneme {} has no model assigned ", self.ID)
        
        return len(self.htkModel.states)
            
            
    
    def __str__(self):
        return self.ID
    
    def isVowel(self):
        
        if (self.ID == 'AA' or
        self.ID == 'A' or
        self.ID == 'O' or
        self.ID == 'OE' or
        self.ID == 'E' or
        self.ID == 'IY' or
        self.ID == 'U' or
        self.ID == 'UE' or
        self.ID == 'I'
        ):
            return True
        
        return False
    
    def getTransMatrix(self):
        '''
        read the trans matrix from model. 
        3x3 or 1x1 matrix for emitting states only.
        as numpy array
        '''
        
        try: self.htkModel
        except AttributeError:
                sys.exit("  phoneme {} has no model assigned ", self.ID)
        
        
        vector_ = self.htkModel.tmat.vector
        currTransMat = numpy.reshape(vector_ ,(len(vector_ )**0.5, len(vector_ )**0.5))
    
        return currTransMat  
    
        