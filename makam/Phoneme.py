'''
Created on Oct 8, 2014

@author: joro
'''
import sys
import numpy
from align.ParametersAlgo import ParametersAlgo
class Phoneme:
    def __init__(self, phonemeID):
        self.ID = phonemeID;
        self.durationInMinUnit = None;
        self.durationInNumFrames = None;
        self.numFirstState = -1
        
        self.lastInSyll = False
    
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
    
#     def getStates(self):
#         try: self.htkModel
#         except NameError:
#             sys.exit(" phoneme {} has no model assigned ", self.ID)
#         
#         return self.htkModel.states
        
    def getNumStates(self):
        '''
        based on assigned htk model
        '''
        
        if ParametersAlgo.ONLY_MIDDLE_STATE:
            return 1
        try: self.htkModel
        except NameError:
            sys.exit("cannot get numsttes. phoneme {} has no htk model assigned ", self.ID)
        
        if (self.htkModel.tmat.numStates - 2) != len(self.htkModel.states):
            sys.exit('num states in matrix differs from num states in htk ')
            
        return len(self.htkModel.states)
            
            
    
    def __str__(self):
        string_phoneme = self.ID
        if self.lastInSyll:
            string_phoneme+= " last in syllable" 
        return string_phoneme
    
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
    
    def isVowelOrLiquid(self):
        
        if (self.isVowel() or
        self.ID == 'L' or
        self.ID == 'LL' or
        self.ID == 'N' or
        self.ID == 'NN' or
        self.ID == 'M' or
        self.ID == 'MM' or 
        self.ID == 'Y'):
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
    
    def isLastInSyll(self):
        return self.lastInSyll
    
    def setIsLastInSyll(self, lastInSyll):
        self.lastInSyll = lastInSyll
        