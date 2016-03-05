'''
Created on Feb 24, 2016

@author: joro
'''
from hmm.continuous._ContinuousHMM import _ContinuousHMM
import numpy
import sys
from numpy.core.numeric import Infinity
from hmm.continuous.DurationPdf import NUMFRAMESPERSEC
from align.FeatureExtractor import tsToFrameNumber
from hmm.ParametersAlgo import ParametersAlgo


class _HMM(_ContinuousHMM):
    '''
    classical Viterbi
    '''
    
    def __init__(self,statesNetwork, numMixtures, NUM_DIMENSIONS, transMatrix, transMatrixOnsets):
    
#     def __init__(self,n,m,d=1,transMatrix=None,means=None,covars=None,w=None,pi=None,min_std=0.01,init_type='uniform',precision=numpy.double, verbose=False):
            '''
            See _ContinuousHMM constructor for more information
            '''
            means, covars, weights, pi = self._constructHMMNetworkParameters(statesNetwork, numMixtures, NUM_DIMENSIONS)
             
            n = len(statesNetwork)
            min_std=0.01
            init_type='uniform'
            precision=numpy.double
            verbose = False 
            _ContinuousHMM.__init__(self, n, numMixtures, NUM_DIMENSIONS, transMatrix, transMatrixOnsets, means, covars, weights, pi, min_std,init_type,precision,verbose) #@UndefinedVariable
    
            self.statesNetwork = statesNetwork
            

      
    def _constructHMMNetworkParameters(self,  statesSequence, numMixtures, NUM_DIMENSIONS):
        '''
        tranform other htkModel params to  format of gyuz's hmm class
        NOTE: better design is to put it in Decoder because this way parameters are not-dependent on Lyrics (.e.g. no statesSequence as arg in the constructor)
        '''
        
       
        numStates = len(statesSequence)
        means = numpy.empty((numStates, numMixtures, NUM_DIMENSIONS))
        
        # init covars
        covars = [[ numpy.matrix(numpy.eye(NUM_DIMENSIONS,NUM_DIMENSIONS)) for j in xrange(numMixtures)] for i in xrange(numStates)]
        
        weights = numpy.ones((numStates,numMixtures),dtype=numpy.double)
        
        # start probs :
        pi = numpy.zeros((numStates), dtype=numpy.double)
        
        # avoid log(0) 
        pi.fill(sys.float_info.min)
#          allow to start only at first state
        pi[0] = 1

#         pi[0] = 0.33
#         pi[1] = 0.33
#         pi[2] = 0.33
        
        # equal prob. for states to start
#         pi = numpy.ones( (numStates)) *(1.0/numStates)
        
    
         
        if statesSequence==None:
            sys.exit('no state sequence')
               
        for i in range(len(statesSequence) ):
            state  = statesSequence[i] 
            
            for (numMixture, weight, mixture) in state.mixtures:
                
                weights[i,numMixture-1] = weight
                
                means[i,numMixture-1,:] = mixture.mean.vector
                
                variance_ = mixture.var.vector
                for k in  range(len( variance_) ):
                    covars[i][numMixture-1][k,k] = variance_[k]
        return means, covars, weights, pi    
        
        
        
    def initDecodingParameters(self,  observationsORLyricsWithModels,  onsetTimestamps, fromTs, toTs):
        '''
        TODO: this and other method should be in _BaseHMM instead of here, becasue they are duplicated in _DurationHMM with slight changes
        '''
        if ParametersAlgo.WITH_ORACLE:
            
            durInSeconds = toTs - fromTs
            lenObservations = tsToFrameNumber(durInSeconds - ParametersAlgo.WINDOW_SIZE / 2.0) 
            self._mapBOracle( observationsORLyricsWithModels, lenObservations, fromTs)
        else:
            lenObservations = len(observationsORLyricsWithModels)
            self._mapB(observationsORLyricsWithModels)
        
        if onsetTimestamps != None:
            self.noteOnsets = numpy.zeros((lenObservations,))
            for onsetTimestamp in onsetTimestamps:
                frameNum = tsToFrameNumber(onsetTimestamp)
                self.noteOnsets[frameNum] = 1
            
        self.phi = numpy.empty((lenObservations,self.n),dtype=self.precision)
        self.phi.fill(-Infinity)
    
       
        # backpointer: form which prev. state
        self.psi = numpy.empty((lenObservations, self.n), dtype=self.precision)
        self.psi.fill(-1)
        
        return lenObservations
        
    
    def viterbi_fast(self):
        
        # init phi and psi at first time
        for j in xrange(self.n):
            currLogPi = numpy.log(self.pi[j])
            self.phi[0][j] = currLogPi + self.B_map[j][0]
            self.psi[0][j] = 0
        
        # viterbi loop    
        lenObs = numpy.shape(self.B_map)[1]
        for t in xrange(1,lenObs):
            self.logger.debug("at time {} out of {}".format(t, lenObs ))
            for j in xrange(self.n):
#                 for i in xrange(self.n):
#                     if (delta[t][j] < delta[t-1][i]*self.transMatrix[i][j]):
#                         delta[t][j] = delta[t-1][i]*self.transMatrix[i][j]
                        
                        if self.noteOnsets[t]:
                            sliceA = self.transMatrixOnsets[:,j]
#                             print "at time {} using matrix for note Onset".format(t)
                        else:
                            sliceA = self.transMatrix[:,j]
                             
#                         print "shape transMatrix:" + str(self.transMatrix.shape)
#                         print "shape phi:" + str(self.phi.shape)
                        APlusPhi = numpy.add(self.phi[t-1,:], sliceA)
                        
                        self.phi[t][j] = numpy.max(APlusPhi)
                        self.phi[t][j] =+ self.B_map[j][t]

                        self.psi[t][j] = numpy.argmax(APlusPhi)
                    
#         numpy.savetxt(PATH_LOGS + '/phi', self.phi)
#         numpy.savetxt( PATH_LOGS + '/psi', self.psi)
        return self.psi
        