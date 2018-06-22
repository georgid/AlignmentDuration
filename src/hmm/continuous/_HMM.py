# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling
# and is modified from https://github.com/guyz/HMM

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/



'''
Created on Feb 24, 2016

@author: joro
'''
from src.hmm.continuous._ContinuousHMM import _ContinuousHMM
import numpy
import sys
from numpy.core.numeric import Infinity
from src.hmm.continuous.DurationPdf import NUMFRAMESPERSEC
from src.align.ParametersAlgo import ParametersAlgo
from src.align.Decoder import visualizeMatrix
from scipy.constants.constants import psi
from src.onsets.OnsetDetector import getDistFromEvent, tsToFrameNumber
import matplotlib


class _HMM(_ContinuousHMM):
    '''
    classical Viterbi
    '''
    
    def __init__(self, statesNetwork, transMatrices):
    
#     def __init__(self,n,m,d=1,transMatrix=None,means=None,covars=None,w=None,pi=None,min_std=0.01,init_type='uniform',precision=numpy.double, verbose=False):
            '''
            See _ContinuousHMM constructor for more information
            '''
            pi = self._set_pi(statesNetwork)
             
            n = len(statesNetwork)
            min_std=0.01
            init_type='uniform'
            precision=numpy.double
            verbose = False 
            _ContinuousHMM.__init__(self, n,   transMatrices, pi, min_std,init_type,precision,verbose) #@UndefinedVariable
    
            self.statesNetwork = statesNetwork
            pass

      
    def _set_pi(self,  statesSequence):

       
        numStates = len(statesSequence)
       
        
        
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
        
    
        
                        
                    
        return  pi    
        
        
        



    def initDecodingParameters(self,  featureExtractor, onsetDetector, fromTsTextGrid, toTsTextGrid):
        '''
        init observation probs map_B 
        and onsets if they are specified (!=None)  
        '''
        
        if ParametersAlgo.WITH_ORACLE_PHONEMES == -1:
            lenFeatures = 80
            self._mapBStub(lenFeatures)
        elif ParametersAlgo.WITH_ORACLE_PHONEMES == 1: # with phoneme annotations as feature vectors
                
                durInSeconds = toTsTextGrid - fromTsTextGrid
                lenFeatures = tsToFrameNumber(durInSeconds - ParametersAlgo.WINDOW_SIZE / 2.0) 
                self._mapBOracle( featureExtractor.featureVectors, lenFeatures, fromTsTextGrid)
        
        
                
        else: # with featureVectors
                lenFeatures = len(featureExtractor.featureVectors)
                self._mapB(featureExtractor.featureVectors)

        
        
        self.noteOnsets = onsetDetector.onsetTsToOnsetFrames( lenFeatures)
            
        self.phi = numpy.empty((lenFeatures,self.n),dtype=self.precision)
        self.phi.fill(-Infinity)
    
       
        # backpointer: form which prev. state
        self.psi = numpy.empty((lenFeatures, self.n), dtype=self.precision)
        self.psi.fill(-1)
        
        return lenFeatures
    
    


    def viterbi_fast_forced(self):
        '''
        forced alignment: considers only previous state in decision
        '''
        
        # init phi and psi at first time
        for j in xrange(self.n):
            currLogPi = numpy.log(self.pi[j])
            self.phi[0][j] = currLogPi + self.B_map[j][0]
        
        lenObs = numpy.shape(self.B_map)[1]
        
        # viterbi loop    
        for t in xrange(1,lenObs):
            self.logger.debug("at time {} out of {}".format(t, lenObs ))
            
            if ParametersAlgo.WITH_ORACLE_ONSETS == -1:
               whichMatrix = -1 # last matrix with no onset
            else:
                # distance of how many frames from closest onset
                onsetDist ,_ = getDistFromEvent( self.noteOnsets, t)
                whichMatrix = min(ParametersAlgo.ONSET_SIGMA_IN_FRAMES + 1, onsetDist)
            
            for j in xrange(self.n):
                        fromState = j-2
                        # if beginning state, no prev. state
                        if j == 0 or j==1:
                            fromState = 0

                            
                        sliceA = self.transMatrices[whichMatrix][fromState:j+1,j]

#                         if j <= t:
#                             print 'at time {} and state {} a_j-1,j and a_j,j = {}'.format(t, j, sliceA)
                        APlusPhi = numpy.add(self.phi[t-1,fromState:j+1], sliceA)
#                         if j <= t:
#                             print 'at time {} and state {} a_j-1,j and a_j,j + phis = {}'.format(t, j, APlusPhi)
                         
                        
                        self.phi[t][j] = numpy.max(APlusPhi)
                        self.psi[t][j] = numpy.argmax(APlusPhi) + fromState

                        self.phi[t][j] += self.B_map[j][t]
#                         if j <= t:
#                             print self.phi[t][j]
#                             print '\n'

            ##### visualize each selected chunk of psi
            tmpArray = numpy.zeros((1,self.psi.shape[1]))
            tmpArray[0,:] = self.psi[t,:]
#             visualizeMatrix(tmpArray)
#             visualizeMatrix(self.phi, 'phi at time {}'.format(t))
                    
#         numpy.savetxt(PATH_LOGS + '/phi', self.phi)
#         numpy.savetxt( PATH_LOGS + '/psi', self.psi)
        
        return self.psi 
   
    
    def viterbi_fast(self):
        '''
        basic viterbi, no forced alignment, with onsets
        @broken, not updated after refactoring
        '''
        
        # init phi and psi at first time
        for j in xrange(self.n):
            currLogPi = numpy.log(self.pi[j])
            self.phi[0][j] = currLogPi + self.B_map[j][0]
        
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
                        self.phi[t][j] += self.B_map[j][t]

                        self.psi[t][j] = numpy.argmax(APlusPhi)
            ##### visualize each selected chunk
            tmpArray = numpy.zeros((1,self.psi.shape[1]))
            tmpArray[0,:] = self.psi[t,:]
#             visualizeMatrix(tmpArray)
                    
#         numpy.savetxt(PATH_LOGS + '/phi', self.phi)
#         numpy.savetxt( PATH_LOGS + '/psi', self.psi)
        return self.psi
       
       
    def visualize_trans_probs(self, lyricsWithModels, fromFrame, toFrame, from_phoneme, to_phoneme):
        '''
        forced alignment: considers only previous state in desicion
        '''
        

        lenObs = numpy.shape(self.B_map)[1]
        tmpOnsetProbArray = numpy.zeros((to_phoneme-from_phoneme + 1, lenObs)) 
        
        # viterbi loop    
#         for t in xrange(1,lenObs):
        for t in xrange(fromFrame, toFrame):
            self.logger.debug("at time {} out of {}".format(t, lenObs ))
            
            if ParametersAlgo.WITH_ORACLE_ONSETS == -1:
                    whichMatrix = -1 # last matrix with no onset
            else:
                    # distance of how many frames from closest onset
                    onsetDist, _ = getDistFromEvent( self.noteOnsets, t)
                    whichMatrix = min(ParametersAlgo.ONSET_SIGMA_IN_FRAMES + 1, onsetDist)
                    self.logger.debug( "which Matrix: " + str(whichMatrix) )
                    
            for j in xrange(from_phoneme, to_phoneme+1):
                        if j > 0:
                            a = self.transMatrices[whichMatrix][j-1,j]
                            tmpOnsetProbArray[j-from_phoneme, t] = a # because of indexing

                         
#             visualizeMatrix(tmpOnsetProbArray, 'titleName')

        matplotlib.rcParams['figure.figsize'] = (20, 8)
        visualizeMatrix(tmpOnsetProbArray[:,fromFrame:toFrame], '')
        
        ###### add vertical legend names
        statesNetworkNames  = []
        for i in range(from_phoneme,to_phoneme+1):
            stateWithDur = lyricsWithModels.statesNetwork[i]
            stateWithDurPrev = lyricsWithModels.statesNetwork[i - 1]
            statesNetworkNames.append("{} -> {}".format(stateWithDurPrev.phoneme.ID, stateWithDur.phoneme.ID))
            
        import matplotlib.pyplot as plt
        from numpy.core.numeric import arange
        plt.yticks(arange(len(statesNetworkNames)) , statesNetworkNames )
        plt.show()
        
            
