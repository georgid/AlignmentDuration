'''
Created on Oct 27, 2014

@author: joro
'''
import os
import sys
from Utilz import writeListOfListToTextFile


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics')
pathHtk2Sp = os.path.join(parentDir, 'htk2s3')
pathHMM = os.path.join(parentDir, 'HMM')

sys.path.append(pathHtk2Sp)
sys.path.append(pathUtils )
sys.path.append(pathHMM)

from hmm.continuous.GMHMM  import GMHMM

import numpy

# TODO: read from models
numMixtures = 9
numDimensions = 25

# TODO: read from feat extraction parameters
NUM_FRAMES_PERSECOND = 100.0

class Decoder(object):
    '''
    holds structures used in decoding and decoding result
    '''


    def __init__(self, lyricsWithModels):
        '''
        Constructor
        '''
        self.lyricsWithModels = lyricsWithModels
        self.hmmNetwork = []
                
        self.indicesStateStarts = []

        self._constructHmmNetwork()
        
        
    def _constructHmmNetwork(self ):
        '''
        Tests the guyz hmm viterbi with one word. 
        '''
        
    #     sequencePhonemes = sequencePhonemes[0:4]
        
        
        ######## construct transition matrix
        #######
        
        transMAtrix = self._constructTransMatrixHMMNetwork(self.lyricsWithModels.phonemesNetwork)
        
#        DEBUG
#  writeListOfListToTextFile(transMAtrix, None , '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentStep/transMatrix')
        
        # construct means, covars, and all the rest params
        #########
        
        
        means, covars, weights, pi = self._constructHMMNetworkParameters(self.lyricsWithModels.statesNetwork)
        
        numStates = len(self.lyricsWithModels.statesNetwork) 
        
        self.hmmNetwork = GMHMM(numStates,numMixtures,numDimensions,transMAtrix,means,covars,weights,pi,init_type='user',verbose=True)
        
    def  _constructTransMatrixHMMNetwork(self, sequencePhonemes):
        
        # just for initialization totalNumPhonemes
        totalNumStates = 0
        for phoneme in sequencePhonemes:
            currNumStates = phoneme.htkModel.tmat.numStates - 2
            totalNumStates += currNumStates
            
        transMAtrix = numpy.zeros((totalNumStates, totalNumStates), dtype=numpy.double)
        
        
        counterOverallStateNum = 0 
        
        for phoneme in sequencePhonemes:
            currNumStates =   phoneme.htkModel.tmat.numStates - 2
            
            vector_ = phoneme.htkModel.tmat.vector
            currTransMat = numpy.reshape(vector_ ,(len(vector_ )**0.5, len(vector_ )**0.5))
            
    #         disregard 1st and last states from transMat because they are the non-emitting states
       
            transMAtrix[counterOverallStateNum : counterOverallStateNum + currNumStates, counterOverallStateNum : counterOverallStateNum + currNumStates ] = currTransMat[1:-1,1:-1]
           
            # transition probability to next state
            #         TODO: here multiply by [0,1] matrix next state. check if it exists
            nextStateTransition = 1
            
            if (counterOverallStateNum + currNumStates) < transMAtrix.shape[1]:
                val = currTransMat[-2,-1] * nextStateTransition
                transMAtrix[counterOverallStateNum + currNumStates -1, counterOverallStateNum + currNumStates] =  val
    
    
            # increment in final trans matrix  
            counterOverallStateNum +=currNumStates
            
            
        return transMAtrix
    
    def _constructHMMNetworkParameters(self, sequenceStates):
        '''
        tranform h2s hmm model to  format of gyuz's hmm class
        '''
        numStates = len(sequenceStates) 
        
        means = numpy.empty((numStates, numMixtures, numDimensions))
        
        # init covars
        covars = [[ numpy.matrix(numpy.eye(numDimensions,numDimensions)) for j in xrange(numMixtures)] for i in xrange(numStates)]
        
        weights = numpy.ones((numStates,numMixtures),dtype=numpy.double)
        
        # start probs : allow to start only at first state
        pi = numpy.zeros((numStates), dtype=numpy.double)
    
        pi[0] = 1
        
        for i in range(len(sequenceStates) ):
            state  = sequenceStates[i] 
            for (numMixture, weight, mixture) in state.mixtures:
                
                weights[i,numMixture-1] = weight
                
                means[i,numMixture-1,:] = mixture.mean.vector
                
                variance_ = mixture.var.vector
                for k in  range(len( variance_) ):
                    covars[i][numMixture-1][k,k] = variance_[k]
        return means, covars, weights, pi
    
    def decodeAudio( self, observationFeatures):
        ''' decode path for given exatrcted features for audio
        '''
        # TODO: doulbe check that features are in same dimension as model
        
    #     observationsMfccs = observationsMfccs[0:1000,:]
        
        self.path, psi, delta = self.hmmNetwork._viterbiForced(observationFeatures)
         
         # DEBUG
        writeListOfListToTextFile(psi, None , '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentStep/psi', True)
        writeListOfListToTextFile(delta, None , '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentStep/delta', True)
        
         
        for p in range(len(self.path)):
            print p ," ", self.path[p], "\n" 
        
        return self.path, psi, delta
    
    def _path2stateIndices(self):
        '''
         indices in path where a new state starts. 
         the array index is the consequtive state count from sequence  
        '''
        self.indicesStateStarts = []
        currState = -1
        for i, p in enumerate(self.path):
            if not p == currState:
              self.indicesStateStarts.append(i)
              currState = p
    
    

   

    def path2ResultWordList(self):
        '''
        excludes 
        to be called after decoding
        '''
        # indices in path
        self._path2stateIndices()
        #sanity check
        numStates = len(self.lyricsWithModels.statesNetwork)
        numdecodedStates = len(self.indicesStateStarts)
        if numStates != numdecodedStates:
            sys.exit("detected path has {} states, but stateNetwork transcript has {} states".format( numdecodedStates, numStates ) )
        
        detectedWordList = []
        
        for word_ in self.lyricsWithModels.listWords:
            countFirstState = word_.syllables[0].phonemes[0].numFirstState

            lastPhoneme = word_.syllables[-1].phonemes[-1]
            if lastPhoneme.ID != 'sp':
                sys.exit('In Decode. \n last state for word {} is not sp. Sorry - not implemented.'.format(word_.text))
            
            countLastState = lastPhoneme.numFirstState

            detectedWord = self._constructTimeStampsForWord( word_, countFirstState, countLastState)
           
            detectedWordList.append( detectedWord)
        return detectedWordList
    
    
    def _constructTimeStampsForWord(self,  word_, countFirstState, countLastState):
        currWordBeginFrame = self.indicesStateStarts[countFirstState]
        currWordEndFrame = self.indicesStateStarts[countLastState]
    #             # debug:
    #             print self.path[currWordBeginFrame]
    # timestamp:
        startTs = float(currWordBeginFrame) / NUM_FRAMES_PERSECOND
        endTs = float(currWordEndFrame) / NUM_FRAMES_PERSECOND
        
        detectedWord = startTs, endTs, word_.text
        print detectedWord
        
        return detectedWord
    
             
        