'''
Created on May 19, 2015

@author: joro
'''
from scipy.stats import norm
import sys
from numpy.core.function_base import linspace
import numpy
from numpy.core.numeric import Infinity


NUMFRAMESPERSEC = 100
MINIMAL_PROB = sys.float_info.min



class DurationPdf(object):
    '''
    only one duration probability distribution: normal distribution  
    '''

    def __init__(self, deviationInSec):
        '''
        #@param deviationInSec: how much vocal can deviate from refDur
        '''
        
          
        # normal distribution with 2 symmetric lobes
        self.numDurs = int(2* deviationInSec * NUMFRAMESPERSEC)
        if not self.numDurs % 2:
            self.numDurs += 1
            
        self.minVal = norm.ppf(0.01)
        self.maxVal= norm.ppf(0.99)
        
        quantileVals  = linspace(self.minVal, self.maxVal, self.numDurs )
        self.liks = numpy.zeros((self.numDurs,1)) 
        for d in range(0,self.numDurs):
            self.liks[d] = norm.pdf(quantileVals[d])
        
        self.liks = numpy.log(self.liks)
    
    def getMinRefDur(self, refScoreDur):
        '''
        R_i - \sigma
        '''
        dur =  refScoreDur - (self.numDurs-1)/2
        return  max(1, dur)
    
    def getMaxRefDur(self, refScoreDur):
        '''
        R_i + \sigma
        '''
        return refScoreDur + (self.numDurs-1)/2
    
    def getWaitLogLik(self, d, refScoreDur):
            '''
            get lik for duration d for given score duration refScoreDur for phoneme  
            used in _DurationHMM
            '''
            
            ##### make sure zero is returned
            if d==0:
                sys.exit("d = 0 not implemented yet")
                return 
            # used in kappa. -Inf because we never want kappa to be selected if over max region of duration
            elif d < self.getMinRefDur(refScoreDur):
                return MINIMAL_PROB
            # this never happens
            elif  d > self.getMaxRefDur(refScoreDur):
                return -Infinity
            else:
                # note: allow negative startIdx to get proper index in liks
                startIdx = refScoreDur - (self.numDurs-1)/2
                # make it start from 0
                idx = d- startIdx

#                 idx = d- startIdx + 1
#                 if idx == len(self.liks):
#                     idx = idx -1
                return self.liks[idx]
    #         set_printoptions(threshold='nan') 
    
if __name__ == '__main__':
    
    durPdf = DurationPdf()
    for i in range(1,13+1):    
        print durPdf.getWaitLogLik(i, 5)