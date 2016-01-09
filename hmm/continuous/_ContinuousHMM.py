'''
Created on Nov 12, 2012

@author: GuyZ
'''

import numpy
import numpy as np
import os
import sys
import logging
from hmm.continuous.DurationPdf import NUMFRAMESPERSEC
from matplotlib.lines import Line2D
# from sklearn.utils.extmath import logsumexp

parentDir = os.path.abspath(  os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir ) )

hmmDir = os.path.join(parentDir, 'HMM/hmm')
if hmmDir not in sys.path: sys.path.append(parentDir)
from hmm._BaseHMM import _BaseHMM



workspaceDir = os.path.abspath(  os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir,  os.path.pardir, os.path.pardir ) ) 
pathUtils = os.path.join(workspaceDir, 'utilsLyrics')
if pathUtils not in sys.path: sys.path.append(pathUtils )
from Utilz import writeListOfListToTextFile, readListTextFile



# to replace 0: avoid log(0) = -inf. -Inf + p(d) makes useless the effect of  p(d)
MINIMAL_PROB = sys.float_info.min



class _ContinuousHMM(_BaseHMM):
    '''
    A Continuous HMM - This is a base class implementation for HMMs with
    mixtures. A mixture is a weighted sum of several continuous distributions,
    which can therefore create a more flexible general PDF for each hidden state.
    
    This class can be derived, but should not be used directly. Deriving classes
    should generally only implement the PDF function of the mixtures.
    
    Model attributes:
    - n            number of hidden states
    - m            number of mixtures in each state (each 'symbol' like in the discrete case points to a mixture)
    - d            number of features (an observation can contain multiple features)
    - A            hidden states transition probability matrix ([NxN] numpy array)
    - means        means of the different mixtures ([NxMxD] numpy array)
    - covars       covars of the different mixtures ([NxM] array of [DxD] covar matrices)
    - w            weighing of each state's mixture components ([NxM] numpy array)
    - pi           initial state's PMF ([N] numpy array).
    
    Additional attributes:
    - min_std      used to create a covariance prior to prevent the covariances matrices from underflowing
    - precision    a numpy element size denoting the precision
    - verbose      a flag for printing progress information, mainly when learning
    '''

    def __init__(self,n,m,d=1,A=None,means=None,covars=None,w=None,pi=None,min_std=0.01,init_type='uniform',precision=numpy.double,verbose=False):
        '''
        Construct a new Continuous HMM.
        In order to initialize the model with custom parameters,
        pass values for (A,means,covars,w,pi), and set the init_type to 'user'.
        
        Normal initialization uses a uniform distribution for all probablities,
        and is not recommended.
        '''
        _BaseHMM.__init__(self,n,m,precision,verbose) #@UndefinedVariable
        
        self.d = d
        self.A = A
        self.pi = pi
        self.means = means
        self.covars = covars
        self.w = w
        self.min_std = min_std

#         self.reset(init_type=init_type)
        
        '''
        flag to load some decoding info from cached files, for example bMap and durationLookup table . 
        makes decoding faster 
        '''
        self.usePersistentFiles = False
        self.logger = logging.getLogger(__name__)
        # other logger set in decoder 
        loggingLevel = logging.INFO
#         loggingLevel = logging.WARNING

        self.logger.setLevel(loggingLevel)
        


    
    def setPersitentFiles(self, usePersistentFiles, URI_bmap):
       
        self.usePersistentFiles =  usePersistentFiles
        self.PATH_BMAP = URI_bmap

    def setNonVocal(self, listNonVocalFragments):
        self.listNonVocalFragments = listNonVocalFragments     
    
    def reset(self,init_type='uniform'):
        '''
        If required, initalize the model parameters according the selected policy
        '''        
        if init_type == 'uniform':
            self.pi = numpy.ones( (self.n), dtype=self.precision) *(1.0/self.n)
            self.A = numpy.ones( (self.n,self.n), dtype=self.precision)*(1.0/self.n)
            self.w = numpy.ones( (self.n,self.m), dtype=self.precision)*(1.0/self.m)            
            self.means = numpy.zeros( (self.n,self.m,self.d), dtype=self.precision)
            self.covars = [[ numpy.matrix(numpy.ones((self.d,self.d), dtype=self.precision)) for j in xrange(self.m)] for i in xrange(self.n)]
        elif init_type == 'user':
            # if the user provided a 4-d array as the covars, replace it with a 2-d array of numpy matrices.
            covars_tmp = [[ numpy.matrix(numpy.ones((self.d,self.d), dtype=self.precision)) for j in xrange(self.m)] for i in xrange(self.n)]
            for i in xrange(self.n):
                for j in xrange(self.m):
                    if type(self.covars[i][j]) is numpy.ndarray:
                        covars_tmp[i][j] = numpy.matrix(self.covars[i][j])
                    else:
                        covars_tmp[i][j] = self.covars[i][j]
            self.covars = covars_tmp
    
    def getSilentStates(self):
        '''
        return indices for non-vocal states
        '''
        indices = []
        for currIdx, stateWithDur in enumerate(self.statesNetwork):
            if stateWithDur.phonemeName == 'sil' or stateWithDur.phonemeName == 'sp':
                indices.append(currIdx)
        return indices
    
    
    def _mapBOracle(self,  lyricsWithModelsOracle, lenObservations, fromTs):
        '''
        loop though phoneme states from  lyricsWithModelsOracle. 
        For each one, for the frames of its duration assign 1 in B_map and
         
        @param lyricsWithModelsOracle - lyrics read from annotation ground truth
        @param fromTs - time to start at
        '''
        
        # init matrix to be zero
        self.B_map = numpy.zeros( (self.n, lenObservations), dtype=self.precision)
        self.B_map.fill(MINIMAL_PROB)
        
        offSet = lyricsWithModelsOracle.phonemesNetwork[0].beginTs - fromTs
        import math
        startDurInFrames =  int(math.floor(offSet * NUMFRAMESPERSEC)) 

        
        for phoneme_ in lyricsWithModelsOracle.phonemesNetwork:
        
            # print phoneme
            
            # get total dur of phoneme's states
            counterCurrPhonemeFirstState = phoneme_.numFirstState
            startDurInFrames =  int(math.floor( (phoneme_.beginTs - fromTs) * NUMFRAMESPERSEC))

            self.logger.debug("phoneme: {} with start dur: {} and duration: {}".format( phoneme_.ID, startDurInFrames, phoneme_.durationInNumFrames ))

            for whichFollowingState in range(phoneme_.getNumStates()):
                        counterWhichState = counterCurrPhonemeFirstState + whichFollowingState
                        stateWithDur = lyricsWithModelsOracle.statesNetwork[counterWhichState]
                        self.logger.debug("\tstate {} duration {}".format( stateWithDur.__str__(),  stateWithDur.getDurationInFrames()))
                        
                        finalDurInFrames = startDurInFrames + stateWithDur.getDurationInFrames()
                        
                        self.B_map[counterWhichState, startDurInFrames: finalDurInFrames+1 ] = 1
                        startDurInFrames =  finalDurInFrames+1  
            #TODO: silence at beginning and end
        
        self.B_map = numpy.log( self.B_map) 
        self._normalizeBByMaxLog()
        
        if self.logger.level == logging.DEBUG:
            self.visualizeBMap()
    
        
    def _mapB(self, observations):
        '''
        Required implementation for _mapB. Refer to _BaseHMM for more details.
        with non-vocal
        '''
        self.logger.info("calculating obs probs..." )
        self.B_map = numpy.zeros( (self.n,len(observations)), dtype=self.precision)
         
        for j in xrange(self.n):
            logLiksForj = self._pdfAllFeatures(observations,j)
            
# normalize  probs for each state to sum to 1 (in log domain)
#             sumLogLiks = logsumexp(logLiksForj)
#             logLiksForj -= sumLogLiks
            self.B_map[j,:] = logLiksForj
        
#         self.visualizeBMap()

         
        #### vocal/non-vocal     

        # get non-vocal states 
        indicesSilent = self.getSilentStates() 
         
        # assign 1-s to non-vocal states
#         inputFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentation/data/laoshengxipi02.wav'
#         detectedSegments, outputFile, windowLen = doitSegmentVJP(inputFile)
        
        # if listNonVocalNotdefinednot defined
        if hasattr(self, 'listNonVocalFragments'):
#           if listNonVocalNotdefined empty it does not change matrix
            for nonVocalFrag in self.listNonVocalFragments:
            
    #             print "start: " + str(segStart[i]) + "\tend: " + str((segStart[i] + segDuration[i])) + "\t" + str(segPred[i]) 
            
                # non-vocal regions
                
                startFrame = int(NUMFRAMESPERSEC * nonVocalFrag[0] )
                endFrame = int(NUMFRAMESPERSEC * nonVocalFrag[1] )
                
                self.B_map[:,startFrame:endFrame+1] =  numpy.log(MINIMAL_PROB)
                self.B_map[numpy.array([indicesSilent]),startFrame:endFrame+1] =  numpy.log(1)
#                 self.visualizeBMap()

                 
        self._normalizeBByMaxLog()
        
#         if self.logger.level == logging.INFO:
        ax = self.visualizeBMap()
#         self.visualizePath(ax)
         
       

    def visualizeBMap(self): 
            import matplotlib.pyplot as plt
            import matplotlib
            matplotlib.interactive(False)

#             plt.figure(figsize=(16,8))
            fig, ax = plt.subplots()
#             ax.imshow(self.B_map, extent=[0, 200, 0, 100], interpolation='none')
            plt.imshow(self.B_map, interpolation='none')

#             plt.colorbar()
#             fig.colorbar()
            ax.autoscale(False)
            return ax
#             plt.show(block=False)

    def visualizePath(self, ax):
        import matplotlib.pyplot as plt
        path = readListTextFile('path')
            
        if self.B_map.shape[1] != len(path):
            sys.exit("obs features are {}, but path has duration {}".format(self.B_map.shape[1], len(path)))
        
        
        
        ax.plot(path, marker='x', color='k', markersize=5)
        
        plt.show()
        
    
    def _mapB_OLD(self, observations):
        '''
        @deprecated
        Required implementation for _mapB. Refer to _BaseHMM for more details.
        This method highly optimizes the running time, since all PDF calculations
        are done here once in each training iteration.
        
        - self.Bmix_map - computesand maps Bjm(Ot) to Bjm(t).
        log precomputed
        '''   
#         return
        
        if self.usePersistentFiles and os.path.exists(self.PATH_BMAP):
            
            self.logger.info("loading probs all observations from {}".format(self.PATH_BMAP))
 
            self.B_map = numpy.loadtxt(self.PATH_BMAP)
            # check length
            if self.B_map.shape[1]  == len(observations)  and self.B_map.shape[0] == self.n:
#                 sys.exit('{} does not store all feature vectors. delete it and generate them again'.format(self.PATH_BMAP))
                
                self.B_map = numpy.log( self.B_map)
                return     
            else:
                self.logger.info("file {} found, but has not the expected num of states {} or observations {}".format(self.PATH_BMAP, self.n, len(observations)) )
       
        self.B_map = numpy.zeros( (self.n,len(observations)), dtype=self.precision)
        self.Bmix_map = numpy.zeros( (self.n,self.m,len(observations)), dtype=self.precision)
        
        for j in xrange(self.n):
            for t in xrange(len(observations)):
                self.logger.debug("at calcbjt at state {} and time {}...\n".format(j, t))
                lik = self._calcbjt(j, t, observations[t])
              
                if lik == 0: 
                    self.logger.debug("obs likelihood at time {} for state {} = 0. Repair by adding {}".format(t,j, MINIMAL_PROB))
                    lik = MINIMAL_PROB
                  
                self.B_map[j,t] = lik
  

        # normalize over states
        for t in xrange(len(observations)):
             self.B_map[:,t] = _normalize(self.B_map[:,t])
             self.logger.debug("sum={} at time {}".format(sum(self.B_map[:,t]), t))
             
        if self.usePersistentFiles:        
            writeListOfListToTextFile(self.B_map, None , self.PATH_BMAP)                 

        self.B_map = numpy.log( self.B_map)
                
    """
    b[j][Ot] = sum(1...M)w[j][m]*b[j][m][Ot]
    Returns b[j][Ot] based on the current model parameters (means, covars, weights) for the mixtures.
    - j - state
    - Ot - the current observation
    Note: there's no need to get the observation itself as it has been used for calculation before.
    """    
    def _calcbjt(self,j,t,Ot):
        '''
        Helper method to compute Bj(Ot) = sum(1...M){Wjm*Bjm(Ot)}
        '''
        
        bjt = 0
        for m in xrange(self.m):
            
            mean = self.means[j][m]
            covar = self.covars[j][m]
            
            self.Bmix_map[j][m][t] = self._pdf(Ot, mean, covar)
            bjt += (self.w[j][m]*self.Bmix_map[j][m][t])
        return bjt
        
    def _calcgammamix(self,alpha,beta,observations):
        '''
        Calculates 'gamma_mix'.
        
        Gamma_mix is a (TxNxK) numpy array, where gamma_mix[t][i][m] = the probability of being
        in state 'i' at time 't' with mixture 'm' given the full observation sequence.
        '''        
        gamma_mix = numpy.zeros((len(observations),self.n,self.m),dtype=self.precision)
        
        for t in xrange(len(observations)):
            for j in xrange(self.n):
                for m in xrange(self.m):
                    alphabeta = 0.0
                    for jj in xrange(self.n):
                        alphabeta += alpha[t][jj]*beta[t][jj]
                    comp1 = (alpha[t][j]*beta[t][j]) / alphabeta
                    
                    bjk_sum = 0.0
                    for k in xrange(self.m):
                        bjk_sum += (self.w[j][k]*self.Bmix_map[j][k][t])
                    comp2 = (self.w[j][m]*self.Bmix_map[j][m][t])/bjk_sum
                    
                    gamma_mix[t][j][m] = comp1*comp2
        
        return gamma_mix
    
    def _updatemodel(self,new_model):
        '''
        Required extension of _updatemodel. Adds 'w', 'means', 'covars',
        which holds the in-state information. Specfically, the parameters
        of the different mixtures.
        '''        
        _BaseHMM._updatemodel(self,new_model) #@UndefinedVariable
        
        self.w = new_model['w']
        self.means = new_model['means']
        self.covars = new_model['covars']
        
    def _calcstats(self,observations):
        '''
        Extension of the original method so that it includes the computation
        of 'gamma_mix' stat.
        '''
        stats = _BaseHMM._calcstats(self,observations) #@UndefinedVariable
        stats['gamma_mix'] = self._calcgammamix(stats['alpha'],stats['beta'],observations)

        return stats
    
    def _reestimate(self,stats,observations):
        '''
        Required extension of _reestimate. 
        Adds a re-estimation of the mixture parameters 'w', 'means', 'covars'.
        '''        
        # re-estimate A, pi
        new_model = _BaseHMM._reestimate(self,stats,observations) #@UndefinedVariable
        
        # re-estimate the continuous probability parameters of the mixtures
        w_new, means_new, covars_new = self._reestimateMixtures(observations,stats['gamma_mix'])
        
        new_model['w'] = w_new
        new_model['means'] = means_new
        new_model['covars'] = covars_new
        
        return new_model
    
    def _reestimateMixtures(self,observations,gamma_mix):
        '''
        Helper method that performs the Baum-Welch 'M' step
        for the mixture parameters - 'w', 'means', 'covars'.
        '''        
        w_new = numpy.zeros( (self.n,self.m), dtype=self.precision)
        means_new = numpy.zeros( (self.n,self.m,self.d), dtype=self.precision)
        covars_new = [[ numpy.matrix(numpy.zeros((self.d,self.d), dtype=self.precision)) for j in xrange(self.m)] for i in xrange(self.n)]
        
        for j in xrange(self.n):
            for m in xrange(self.m):
                numer = 0.0
                denom = 0.0                
                for t in xrange(len(observations)):
                    for k in xrange(self.m):
                        denom += (self._eta(t,len(observations)-1)*gamma_mix[t][j][k])
                    numer += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m])
                w_new[j][m] = numer/denom
            w_new[j] = self._normalize(w_new[j])
                
        for j in xrange(self.n):
            for m in xrange(self.m):
                numer = numpy.zeros( (self.d), dtype=self.precision)
                denom = numpy.zeros( (self.d), dtype=self.precision)
                for t in xrange(len(observations)):
                    numer += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m]*observations[t])
                    denom += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m])
                means_new[j][m] = numer/denom
                
        cov_prior = [[ numpy.matrix(self.min_std*numpy.eye((self.d), dtype=self.precision)) for j in xrange(self.m)] for i in xrange(self.n)]
        for j in xrange(self.n):
            for m in xrange(self.m):
                numer = numpy.matrix(numpy.zeros( (self.d,self.d), dtype=self.precision))
                denom = numpy.matrix(numpy.zeros( (self.d,self.d), dtype=self.precision))
                for t in xrange(len(observations)):
                    vector_as_mat = numpy.matrix( (observations[t]-self.means[j][m]), dtype=self.precision )
                    numer += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m]*numpy.dot( vector_as_mat.T, vector_as_mat))
                    denom += (self._eta(t,len(observations)-1)*gamma_mix[t][j][m])
                covars_new[j][m] = numer/denom
                covars_new[j][m] = covars_new[j][m] + cov_prior[j][m]               
        
        return w_new, means_new, covars_new
    


    def _normalizeBByMax(self):
        '''
        Divide them by max in array. decrease chance of underflow
        seems it does not make difference on performance.
        in non-log domain
        '''
        
        self.logger.debug("normalizing by max ...")

        maxProb = numpy.amax(self.B_map)
        for j in xrange(self.B_map.shape[0]):
            for t in xrange(self.B_map.shape[1]):
                self.B_map[j][t] = self.B_map[j][t] / maxProb
    
    def _normalizeBByMaxLog(self):
        self.logger.info("normalizing by max in log domain...")
        maxProb = numpy.amax(self.B_map)
        self.B_map -= maxProb
        
    
    def _pdf(self,x,mean,covar):
        '''
        Deriving classes should implement this method. This is the specific
        Probability Distribution Function that will be used in each
        mixture component.
        '''        
        raise NotImplementedError("PDF function must be implemented")
    
    def _pdfAllFeatures(self,observations,j):
        '''
        Deriving classes should implement this method.
        get the pdf of a series of features for model j
        
        '''  
        raise NotImplementedError("PDF function must be implemented")
    
def _normalize(arr):
        '''
        Helper method to normalize probabilities, so that
        they all sum to '1'
        '''
        summ = numpy.sum(arr)
        for i in xrange(len(arr)):
            arr[i] = (arr[i]/summ)
        return arr
    
def logsumexp(arr, axis=0):
    """Computes the sum of arr assuming arr is in the log domain.
    
    TAKEN FROM sklearn/utils/extmath.py
    
    Returns log(sum(exp(arr))) while minimizing the possibility of
    over/underflow.
    
    Examples
    --------

    >>> import numpy as np
    >>> from sklearn.utils.extmath import logsumexp
    >>> a = np.arange(10)
    >>> np.log(np.sum(np.exp(a)))
    9.4586297444267107
    >>> logsumexp(a)
    9.4586297444267107
    """
    import sys
    MINIMAL_PROB = sys.float_info.min
    
    arr = np.rollaxis(arr, axis)
    # Use the max to normalize, as with the log this is what accumulates
    # the less errors
    vmax = arr.max(axis=0)
    old_settings = np.seterr( under='raise')
    try:
        a = np.exp(arr - vmax)
    except FloatingPointError:
        old_settings = np.seterr( under='ignore')
        a = np.exp(arr - vmax)
        a[a==0] = MINIMAL_PROB
    b = np.sum(a, axis=0)
    out = np.log(b)
    out += vmax
    
    old_settings = np.seterr( under='raise')
    return out

    
if __name__ == '__main__':
     
#     inputFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentation/data/laoshengxipi02.wav'
#     detectedSegments, outputFile, windowSize = doitSegmentVJP(inputFile)
    
    VJPpredictionFile = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/segmentationShuo/data/output_VJP_laoshengxipi02/predictionVJP.txt'
    smoothedPred = parsePrediction(VJPpredictionFile)
    windowLen = 0.25
    segStart, segDuration, segPred = prepareAnnotation(smoothedPred,  windowLen)
    for i in range(len(segStart)):
        print "start: " + str(segStart[i]) + "\tend: " + str((segStart[i] + segDuration[i])) + "\t" + str(segPred[i]) 
        
    