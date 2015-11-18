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
        
    def setNumStates(self, numStates):
        self.numStates = numStates
    
    def setBeginTs(self, beginTs):
        '''
        begin ts from annotation
        '''
        self.beginTs = beginTs
    
    def setEndTs(self, endTs):
        '''
        begin ts from annotation
        '''
        self.endTs = endTs
            
    def setNumFirstState(self, numFirstState):
            self.numFirstState = numFirstState
        

    def setDurationInNumFrames(self, dur):
        self.durationInNumFrames =    dur; 
      
    
    def setHTKModel(self, hmmModel):
        self.htkModel = hmmModel
    
    def setGMM(self, gmm):
        self.gmm = gmm
    
#     def getStates(self):
#         try: self.htkModel
#         except NameError:
#             sys.exit(" phoneme {} has no model assigned ", self.ID)
#         
#         return self.htkModel.states
        
    def getNumStates(self):
        try: self.htkModel
        except AttributeError:
            return self.numStates
        
        return len(self.htkModel.states)
            
            
    
    def __str__(self):
        return self.ID
     
    def __repr__(self):
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
    
    def getTransMatrix(self, htkModel):
        '''
        read the trans matrix from model. 
        3x3 or 1x1 matrix for emitting states only as numpy array
        '''
        
        try: htkModel
        except NameError:
            try: self.htkModel
            except AttributeError:
                sys.exit("  phoneme {} has no model assigned ", self.ID)
            else:     htkModel = self.htkModel 

        
        vector_ = htkModel.tmat.vector
        currTransMat = numpy.reshape(vector_ ,(len(vector_ )**0.5, len(vector_ )**0.5))
    
        return currTransMat  
    
        