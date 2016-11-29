'''
Created on Nov 12, 2012

@author: GuyZ
'''

import numpy


from sklearn.mixture import GaussianMixture as GMM_
from sklearn.mixture.gaussian_mixture import _compute_precision_cholesky
from hmm.continuous._HMM import _HMM
import sys
from src.align.ParametersAlgo import ParametersAlgo
from hmm.continuous._DurationHMM import _DurationHMM
# GMM class from
# http://scikit-learn.org/stable/modules/generated/sklearn.mixture.GMM.html

if ParametersAlgo.WITH_DURATIONS:
    baseClass = _DurationHMM
else:   
    baseClass = _HMM
    
# from _ContinuousHMM import _ContinuousHMM
class GMHMM(baseClass):
    '''
    A Gaussian Mixtures HMM - This is a representation of a continuous HMM,
    containing a mixture of gaussians in each hidden state.
    
    For more information, refer to _ContinuousHMM.
    
    - m            number of mixtures in each state (each 'symbol' like in the discrete case points to a mixture)
    - d            number of features (an observation can contain multiple features)
    - means        means of the different mixtures ([NxMxD] numpy array)
    - covars       covars of the different mixtures ([NxM] array of [DxD] covar matrices)
    - w            weighing of each state's mixture components ([NxM] numpy array)
    '''

        
    def __init__(self,statesSequence,  transMatrices):
        '''
        See base class constructor for more information
        '''
        super(GMHMM, self).__init__(statesSequence, transMatrices)
        if baseClass == _DurationHMM:
            super(GMHMM, self).setALPHA(ParametersAlgo.ALPHA)
        self._set_GMMs(statesSequence)

   
        
    def _set_GMMs(self, statesSequence):
        '''
        build n-state GMMs with scikit-learn's classes.
        copy means etc. from self.weights and self.means and self.covars
        '''
        
        
        if statesSequence==None:
            sys.exit('no state sequence')
        
        numMixtures = self._get_num_mixtures(statesSequence)
        
        means = numpy.empty((self.n, numMixtures, self.numDimensions))
        
        weights = numpy.ones((self.n, numMixtures),dtype=numpy.double)
        
        # init covars
        covars = [[ numpy.matrix(numpy.eye(self.numDimensions, self.numDimensions)) for j in xrange(numMixtures)] for i in xrange(self.n)]
               
        for i in range(len(statesSequence) ):
            state  = statesSequence[i] 
            
            if ParametersAlgo.FOR_MAKAM:
                for (numMixture, weight, mixture) in state.mixtures:
                    
                    weights[i,numMixture-1] = weight
                    
                    means[i,numMixture-1,:] = mixture.mean.vector
                    
                    variance_ = mixture.var.vector
                    for k in  range(len( variance_) ):
                        covars[i][numMixture-1][k,k] = variance_[k]
            
            elif ParametersAlgo.FOR_JINGJU:
                gmm_ = state.mixtures
            
                for numMixture in range(gmm_.n_components):
                    weights[i,numMixture] = gmm_.weights_[numMixture]
                    
                    means[i,numMixture,:] = gmm_.means_[numMixture]
                    
                    variance_ = gmm_.covars_[numMixture]
                    
                    for k in  range(len( variance_) ):
                        covars[i][numMixture][k,k] = variance_[k]
        
        ####### put into GMM models 
        self.GMMs = numpy.empty(self.n, dtype=GMM_)

        
  
        
        for stateIdx in range(self.n):
            curr_GMM = GMM_(covariance_type='diag', n_components=numMixtures)
            curr_GMM.means_ = means[stateIdx]
            
            curr_GMM.covars_  = numpy.zeros((numMixtures, self.numDimensions))
            for m_idx in range(numMixtures):
                for d_idx in range(self.numDimensions):
                    a = covars[stateIdx][m_idx][d_idx,d_idx]
                    curr_GMM.covars_[m_idx,d_idx] = a
            
            curr_GMM.weights_ = weights[stateIdx]
            
            
            curr_GMM.precisions_cholesky_ = _compute_precision_cholesky(curr_GMM.covars_, curr_GMM.covariance_type)
            self.GMMs[stateIdx] = curr_GMM    
    
    def _get_num_mixtures(self, statesSequence):
        '''
        sets num dimensions
        NOTE: better design is to put it in Decoder because this way parameters are not-dependent on Lyrics (.e.g. no statesSequence as arg in the constructor)
        '''
        
        if ParametersAlgo.FOR_MAKAM:
            numMixtures = len(statesSequence[0].mixtures)
            (numMixture, weight, mixture) = statesSequence[0].mixtures[0]
            self.numDimensions = len(mixture.var.vector)
             
        elif ParametersAlgo.FOR_JINGJU:
            
            firstGmm_ = statesSequence[0].mixtures # mixtures are of type 
            numMixtures = firstGmm_.n_components
            firstMeansVector = firstGmm_.means_[0]
            self.numDimensions = firstMeansVector.shape[0]
        return numMixtures      
        
    def _pdfAllFeatures(self,features,j):
        '''
        get the pdf of a series of features for models_makam j
        uses sciKit learn's GMM class
        '''
#         old_settings = numpy.seterr(under='warn')
        
        # double check that features are in same dimension as models
        if features.shape[1] != self.numDimensions:
                sys.exit("dimension of feature vector should be {} but is {} ".format(self.numDimensions, features.shape[1]) )
        
        logprob = self.GMMs[j].score_samples(features)
        return logprob  
        
        
    def _pdf(self,x,mean,covar):
        '''
        Gaussian PDF function
        '''        
        covar_det = numpy.linalg.det(covar);
        
        c = (1 / ( (2.0*numpy.pi)**(float(self.numDimension/2.0)) * (covar_det)**(0.5)))
        pdfval = c * numpy.exp(-0.5 * numpy.dot( numpy.dot((x-mean),covar.I), (x-mean)) )
        return pdfval