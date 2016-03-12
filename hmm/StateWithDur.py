'''
Created on Nov 10, 2014

@author: joro
'''
import os
import sys
from hmm.continuous.DurationPdf import DurationPdf
from hmm.continuous.ExpDurationPdf import ExpDurationPdf


from htkparser.htk_models import State

class StateWithDur(State):
    '''
    extends State with 
    - durationInFrames 
    - durationDistribution
    '''


    def __init__(self, mixtures, phoneme, idxInPhoneme, distribType='normal', deviationInSec=0.1):
        '''
        Constructor
        '''
        State.__init__(self, mixtures)
        self.phoneme = phoneme
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
            self.durationDistribution = ExpDurationPdf()                                                
  
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
        self.waitProb = waitProb
        if self.distributionType == 'exponential':
            self.durationDistribution.setWaitProb(waitProb, self.durationInFrames)
 
    def getMaxRefDur(self):
        if self.distributionType == 'normal':
            a= int(self.durationDistribution.getMaxRefDur(self.durationInFrames))
        else:
            a= int(self.durationDistribution.getMaxRefDur())
#         print "durationInFrames {}".format(self.durationInFrames) 
        return a
            
    def getMinRefDur(self):
        if self.distributionType == 'normal':
            return int(self.durationDistribution.getMinRefDur(self.durationInFrames))
        else:
            return int(self.durationDistribution.getMinRefDur())
    
    def __str__(self):
        return self.phoneme.ID + "_"  + str(self.idxInPhoneme)
        
        