'''
Created on May 20, 2016

@author: joro
'''
import sys
import os
from for_jingju.sciKitGMM import SciKitGMM
import numpy

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 

pathHTKParser = os.path.join(parentDir, 'htkModelParser')
if pathHTKParser not in sys.path:    
    sys.path.append(pathHTKParser)
        
import htkparser


class PhonemeBase(object):
    '''
    classdocs
    '''


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
    
 
    
    def setModel(self, model):
        '''
        could be sciKitGMM or htkConverter object 
        '''
        self.model =  model
        if isinstance(model, htkparser.htk_models.Hmm):
            self.isModelTypeHTK = 1
        elif isinstance(model, SciKitGMM):
            self.isModelTypeHTK = 0 
        else:
            sys.exit("models_makam for phoneme {} is neither htk nor sciKitGMM ".format(self.ID) )

        
        
    
    def getTransMatrix(self):
        '''
        read the trans matrix from models_makam. 
        3x3 or 1x1 matrix for emitting states only.
        as numpy array
        '''
        
        try: self.model
        except AttributeError:
                sys.exit("  phoneme {} has no models_makam assigned ".format(self.ID) )
        
        
        if not self.isModelTypeHTK:
                    sys.exit("trans matrix defined only for htk models_makam" )

        vector_ = self.model.tmat.vector
        currTransMat = numpy.reshape(vector_ ,(len(vector_ )**0.5, len(vector_ )**0.5))
    
        return currTransMat  
    
    
    def getNumStates(self):
        '''
        based on assigned htk models
        '''
        

        try: self.model
        except AttributeError:
            sys.exit("cannot get numstates. phoneme {} has no htk or gmm models_makam assigned ".format(self.ID))
            
        if self.isModelTypeHTK:
            if (self.model.tmat.numStates - 2) != len(self.model.states):
                sys.exit('num states in matrix differs from num states in htk ')
            
            lenStates = len(self.model.states)
        
        else:
            lenStates = 1
        
        return lenStates
    
        
    def isLastInSyll(self):
        return self.lastInSyll
    
    def setIsLastInSyll(self, lastInSyll):
        self.lastInSyll = lastInSyll
    
    def __str__(self):
        string_phoneme = self.ID
        if self.lastInSyll:
            string_phoneme+= " :last in syllable " 
        return string_phoneme
     
    def __repr__(self):
        return self.ID
    
    
    def isVowel(self):
        raise NotImplementedError("Phoneme.isVowe not implemented")
    