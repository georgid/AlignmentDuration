'''
Created on Nov 10, 2014

@author: joro
'''
import os
import sys
from hmm.continuous.DurationPdf import DurationPdf
from hmm.continuous.ExponentialPdf import ExponentialPdf

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 

pathHtkParser = os.path.join(parentDir, 'htkModelParser')
if pathHtkParser not in sys.path:
    sys.path.append(pathHtkParser)
    
from htkparser.htk_models import State
from htkparser.htk_models import Hmm


class StateWithDur(State):
    '''
    extends State with 
    - durationInFrames 
    - durationDistribution
    '''


    def __init__(self,  phoneme, idxInPhoneme, distribType='normal', deviationInSec=0.1):
        '''
        Constructor
        '''
        if phoneme.isModelTypeHTK: # htk model
            state = phoneme.model.states[idxInPhoneme][1]
            State.__init__(self, state.mixtures)
        else: # scikit gmm type of state
            self.mixtures = phoneme.model.gmm

        
        self.phoneme= phoneme
        self.idxInPhoneme  = idxInPhoneme
        
        try:
            distribType
        except NameError:
            pass
        else:
            if not distribType=='normal' and not distribType=='exponential':
                sys.exit(" unknown distrib type. Only normal and exponential aimplemented now!")
            
        self.distributionType = distribType
        if distribType == 'normal':
            self.durationDistribution = DurationPdf(deviationInSec)
        else:
            self.durationDistribution = ExponentialPdf()                                                
  
    def setDurationInFrames(self, durationInFrames):
        '''
        for normal distrib
        '''
        self.durationInFrames = int(durationInFrames)
        
    def getDurationInFrames(self):
        
        try:  
            return self.durationInFrames
        except AttributeError:
            return 0
        
    def setWaitProb(self, waitProb):
        '''
        for exp distrib
        '''   
        
        if self.distributionType == 'exponential':
            self.durationDistribution.setWaitProb(waitProb, self.durationInFrames)
        else:
            sys.exit(" in setWaitProb(). waitProb. defined only for states with prob of type exponential")
     
     
    def getWaitProb(self):
        return self.durationDistribution.getWaitProb()
            
    def setMaxRefDur(self):
        
        try:
            self.durationInFrames
        except AttributeError: 
            sys.exit('self.durationInFrames in frames not set. Use setDurationInFrames() first')
                
            
        if self.distributionType == 'normal':
            self.maxRefDur = int(self.durationDistribution.getMaxRefDur(self.durationInFrames))
        else:  # exponential
            self.maxRefDur = int(self.durationDistribution.getMaxRefDur())        
            
    def getMaxRefDur(self):

        return self.maxRefDur
      
            
    def getMinRefDur(self):
        if self.distributionType == 'normal':
            return int(self.durationDistribution.getMinRefDur(self.durationInFrames))
        else:
            return int(self.durationDistribution.getMinRefDur())
    
    def __str__(self):
        return self.phonemeName + "_"  + str(self.idxInPhoneme)
     
    def __repr__(self):
        return self.phonemeName + "_"  + str(self.idxInPhoneme)    
        