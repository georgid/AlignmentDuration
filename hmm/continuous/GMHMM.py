'''
Created on Nov 12, 2012

@author: GuyZ
'''

import numpy

from _DurationHMM import _DurationHMM

from sklearn.mixture import GMM as GMM_
# GMM class from
# http://scikit-learn.org/stable/modules/generated/sklearn.mixture.GMM.html



# from _ContinuousHMM import _ContinuousHMM
# class GMHMM(_ContinuousHMM):
class GMHMM(_DurationHMM):
    '''
    A Gaussian Mixtures HMM - This is a representation of a continuous HMM,
    containing a mixture of gaussians in each hidden state.
    
    For more information, refer to _ContinuousHMM.
    '''

#     def __init__(self,n,m,d=1,A=None,means=None,covars=None,w=None,pi=None,min_std=0.01,init_type='uniform',precision=numpy.double,verbose=False):
#         '''
#         See base class constructor for more information
#         '''
#         super(GMHMM, self).__init__(n,m,d,A,means,covars,w,pi,min_std,init_type,precision,verbose) #@UndefinedVariable
#         self._set_GMMs()
        
    def __init__(self,statesNetwork, numMixtures, numDimensions):
        '''
        See base class constructor for more information
        '''
        super(GMHMM,self).__init__(statesNetwork, numMixtures, numDimensions)
        self._set_GMMs()
        
    def _set_GMMs(self):
        '''
        build n GMMs with scikit-learn's classes  
        '''
        self.GMMs = numpy.empty(self.n, dtype=GMM_)
        
        for stateIdx in range(self.n):
            self.GMMs[stateIdx] = GMM_(covariance_type='diag', n_components=self.m)
            self.GMMs[stateIdx].means_ = self.means[stateIdx]
            
            self.GMMs[stateIdx].covars_  = numpy.zeros((self.m, self.d))
            for m_idx in range(self.m):
                for d_idx in range(self.d):
                    a = self.covars[stateIdx][m_idx][d_idx,d_idx]
                    self.GMMs[stateIdx].covars_[m_idx,d_idx] = a
            
            self.GMMs[stateIdx].weights_ = self.w[stateIdx]
            
        
    def _pdfAllFeatures(self,observations,j):
        '''
        get the pdf of a series of features for model j
        uses sciKit learn's GMM class
        '''
#         old_settings = numpy.seterr(under='warn')

        (logprob,responsibilities) = self.GMMs[j].score_samples(observations)
        return logprob  
        
        
    def _pdf(self,x,mean,covar):
        '''
        Gaussian PDF function
        '''        
        covar_det = numpy.linalg.det(covar);
        
        c = (1 / ( (2.0*numpy.pi)**(float(self.d/2.0)) * (covar_det)**(0.5)))
        pdfval = c * numpy.exp(-0.5 * numpy.dot( numpy.dot((x-mean),covar.I), (x-mean)) )
        return pdfval