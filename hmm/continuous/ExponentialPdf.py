'''
Created on Dec 17, 2014

@author: joro
'''
import sys
import numpy

class ExponentialPdf(object):
    
    def __init__(self):
        self.MAX_ALLOWED_DURATION_RATIO = 2
        # wait at same state prob TODO: read from model
    
    def setWaitProb(self, waitProb, durationInFrames):
        self.waitProb = waitProb
        self.durationInFrames = durationInFrames
        
        # TODO: create here wait prob. 
        
    def getWaitProb(self):
        return self.waitProb
    
    def getMinRefDur(self):
        return 1
    
    def getMaxRefDur(self):
        '''
        max ref duration is same as assigned duration in frames
        '''
        return  self.durationInFrames
            
    def getWaitLogLik(self, d):
        '''
        get lik for duration d for given score duration refScoreDur for phoneme  
        used in _DurationHMM
        '''
        
        ##### make sure zero is returned
       
        
        if d==0:
            sys.exit("d = 0 not implemented yet")
            return 
        
        # just in case
        elif d > self.getMaxRefDur():
            return -Infinity
        else:
#             if refScoreDur > self.lookupTableLogLiks.shape[0]:
#                 sys.exit("current score duration {} is bigger than max in list of lookup score durations {}".format( refScoreDur, self.lookupTableLogLiks.shape[0]))
            lik = (1-self.waitProb) * pow(self.waitProb, d-1) 
            old_settings = numpy.seterr( under='raise')
            out =  numpy.log(lik)
            return out
    
    
if __name__ == '__main__':
    durPdf = ExponentialPdf(0.9)
    
    for i in range(1, 100):
        print durPdf.getWaitLogLik(i)