'''
Created on Oct 27, 2014

@author: joro
'''
import os
import sys
import logging
from LyricsParsing import expandlyrics2WordList, _constructTimeStampsForTokenDetected,\
    expandlyrics2SyllableList
from Constants import numDimensions, numMixtures


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 



from utilsLyrics.Utilz import writeListOfListToTextFile, writeListToTextFile


import numpy

# use duraiton-based decoding (HMMDuraiton package) or just plain viterbi (HMM package) 
# if false, use transition probabilities from htkModels
WITH_DURATIONS= True

# WITH_DURATIONS= False



if not WITH_DURATIONS:
    pathHMM = os.path.join(parentDir, 'HMM')
    if pathHMM not in sys.path:    
        sys.path.append(pathHMM)


# if WITH_DURATIONS:
#     from hmm.continuous.DurationPdf import MINIMAL_PROB

from hmm.Path import Path
from hmm.continuous.GMHMM  import GMHMM

logger = logging.getLogger(__name__)
# loggingLevel = logging.WARNING
loggingLevel = logging.DEBUG
loggingLevel = logging.INFO

logging.basicConfig(format='%(levelname)s:%(funcName)30s():%(message)s')
logger.setLevel(loggingLevel)

# other logger set in _Continuous

class Decoder(object):
    '''
    holds structures used in decoding and decoding result
    '''


    def __init__(self, lyricsWithModels, URIrecordingNoExt, ALPHA, numStates=None, withModels=True):
        '''
        Constructor
        '''
        self.lyricsWithModels = lyricsWithModels
        self.URIrecordingNoExt = URIrecordingNoExt
        
        '''
        of class HMM
        '''
        self.hmmNetwork = []
        
        self._constructHmmNetwork(numStates, float(ALPHA), withModels)
        self.hmmNetwork.logger.setLevel(loggingLevel)
        
        # Path class object
        self.path = None
    
    
    def decodeAudio( self, observationFeatures, listNonVocalFragments, usePersistentFiles):
        ''' decode path for given exatrcted features for audio
        HERE is decided which decoding scheme: with or without duration (based on WITH_DURATION parameter)
        '''

        self.hmmNetwork.setPersitentFiles( usePersistentFiles, '' )
        self.hmmNetwork.setNonVocal(listNonVocalFragments)
        
        # double check that features are in same dimension as model
        if observationFeatures.shape[1] != numDimensions:
            sys.exit("dimension of feature vector should be {} but is {} ".format(numDimensions, observationFeatures.shape[1]) )
        
        
        self.hmmNetwork.initDecodingParameters(observationFeatures)

        # standard viterbi forced alignment
        if not WITH_DURATIONS:
            
            path_, psi, delta = self.hmmNetwork._viterbiForced(len(observationFeatures))
            self.path =  Path(None, None, None)
            self.path.setPatRaw(path_)
            
        
        else:   # duration-HMM
            lenObs = len(observationFeatures)
            chiBackPointer, psiBackPointer = self.hmmNetwork._viterbiForcedDur(lenObs)
            
#             writeListOfListToTextFile(chiBackPointer, None , PATH_CHI)
#             writeListOfListToTextFile(psiBackPointer, None , PATH_PSI)
            withOracle = 0    
            detectedWordList, self.path = self.backtrack(withOracle, chiBackPointer, psiBackPointer )
            
            print "\n"
         # DEBUG
#         self.path.printDurations()
        
            return detectedWordList
    
    def decodeWithOracle(self, lyricsWithModelsORacle, URIrecordingNoExt, fromTs, toTs):
        '''
        instead of bMap  set as oracle from annotation
        '''
   
        
        lenObservations = self.hmmNetwork.initDecodingParametersOracle(lyricsWithModelsORacle, URIrecordingNoExt, fromTs, toTs)
        
        chiBackPointer, psiBackPointer = self.hmmNetwork._viterbiForcedDur(lenObservations)
    #   
        withOracle = 1  
        detectedWordList, self.path = self.backtrack(withOracle, chiBackPointer, psiBackPointer)
        return detectedWordList 
    

        
    def _constructHmmNetwork(self,  numStates, ALPHA,  withModels ):
        '''
        top level-function: costruct self.hmmNEtwork that confirms to guyz's code 
        '''

        ######## construct transition matrix
        #######
        if not WITH_DURATIONS:
            transMAtrix = self._constructTransMatrixHMMNetwork(self.lyricsWithModels.phonemesNetwork)

        
        
        if  WITH_DURATIONS:
            self.hmmNetwork = GMHMM(self.lyricsWithModels.statesNetwork, numMixtures, numDimensions)
            self.hmmNetwork.setALPHA(ALPHA)
        
        else:
            if numStates == None:
                numStates = len(self.lyricsWithModels.statesNetwork) 
        
            # construct means, covars, and all the rest params
            #########
            means, covars, weights, pi = self._constructHMMNetworkParameters(numStates,  withModels)
            self.hmmNetwork = GMHMM(numStates,numMixtures,numDimensions,transMAtrix,means,covars,weights,pi,init_type='user',verbose=True)
        

        
    def  _constructTransMatrixHMMNetwork(self, sequencePhonemes):
        '''
        tranform other htkModel params to  format of gyuz's hmm class
        take from sequencePhonemes' attached htk models the transprobs.
        '''
        # just for initialization totalNumPhonemes
        totalNumStates = 0
        for phoneme in sequencePhonemes:
            currNumStates = phoneme.htkModel.tmat.numStates - 2
            totalNumStates += currNumStates
            
        transMAtrix = numpy.zeros((totalNumStates, totalNumStates), dtype=numpy.double)
        
        
        counterOverallStateNum = 0 
        
        for phoneme in sequencePhonemes:
            currNumStates =   phoneme.htkModel.tmat.numStates - 2
            
    #         disregard 1st and last states from transMat because they are the non-emitting states
            currTransMat = phoneme.getTransMatrix()
            
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
    

    
    def _constructHMMNetworkParameters(self,  numStates,  withModels=True, sequenceStates=None):
        '''
        tranform other htkModel params to  format of gyuz's hmm class.
        similar code in method _DurationHMM_constructNetworkParams. This left here for GMM class without duration
        '''
        
       
        
        means = numpy.empty((numStates, numMixtures, numDimensions))
        
        # init covars
        covars = [[ numpy.matrix(numpy.eye(numDimensions,numDimensions)) for j in xrange(numMixtures)] for i in xrange(numStates)]
        
        weights = numpy.ones((numStates,numMixtures),dtype=numpy.double)
        
        # start probs :
        pi = numpy.zeros((numStates), dtype=numpy.double)
        
        # avoid log(0) 
        pi.fill(sys.float_info.min)
#          allow to start only at first state
        pi[0] = 1
        
        # equal prob. for states to start
#         pi = numpy.ones( (numStates)) *(1.0/numStates)
        
        if not withModels:
            return None, None, None, pi

        
        sequenceStates = self.lyricsWithModels.statesNetwork
         
        if sequenceStates==None:
            sys.exit('no state sequence')
               
        for i in range(len(sequenceStates) ):
            state  = sequenceStates[i] 
            
            for (numMixture, weight, mixture) in state.mixtures:
                
                weights[i,numMixture-1] = weight
                
                means[i,numMixture-1,:] = mixture.mean.vector
                
                variance_ = mixture.var.vector
                for k in  range(len( variance_) ):
                    covars[i][numMixture-1][k,k] = variance_[k]
        return means, covars, weights, pi
    
            
      
        
        
    def path2ResultWordList(self, path, tokenLevel='words'):
        '''
        makes sense of path indices : maps numbers to states and phonemes.
        uses self.lyricsWithModels.statesNetwork and self.lyricsWithModels.listWords) 
        to be called after decoding
        '''
        # indices in pathRaw
        self.path = path
        self.path._path2stateIndices()
        
        #sanity check
        numStates = len(self.lyricsWithModels.statesNetwork)
        numdecodedStates = len(self.path.indicesStateStarts)
        
        if numStates != numdecodedStates:
            logging.warn("detected path has {} states, but stateNetwork transcript has {} states \n \
            WORKAROUND: adding missing states at beginning of path. This should not happen often ".format( numdecodedStates, numStates ) )
            # num misssed states in the beginning of the path
            howManyMissedStates = numStates - numdecodedStates
            # WORKAROUND: assume missed states start at time 0. Append zeros
            for i in range(howManyMissedStates):
                self.path.indicesStateStarts[:0] = [0]
        dummy= 0
        if tokenLevel == 'words':
            detectedTokenList = expandlyrics2WordList (self.lyricsWithModels, self.path, dummy, _constructTimeStampsForTokenDetected)
        elif tokenLevel == 'syllables':
            detectedTokenList = expandlyrics2SyllableList (self.lyricsWithModels, self.path, dummy, _constructTimeStampsForTokenDetected)
        else:
            detectedTokenList = []
            logger.warning( 'parsing of detected  {} not implemented'.format( tokenLevel) )
            
        return detectedTokenList 
    
    
    
    def backtrack(self, withOracle, chiBackPointer, psiBackPointer):
        ''' 
        backtrack optimal path of states from backpointers
        interprete states to words      
        '''
        
        # if not set, segments into words
        TOKEN_LEVEL= 'syllables'
        
        # self.hmmNetwork.phi is set in decoder.decodeAudio()
        self.path =  Path(chiBackPointer, psiBackPointer, self.hmmNetwork.phi )
        
        pathUtils = os.path.join(parentDir, 'utilsLyrics')
        if pathUtils not in sys.path:
            sys.path.append(pathUtils )
    

        if withOracle:
            outputURI = self.URIrecordingNoExt + '.path_oracle'
        else:
            outputURI = self.URIrecordingNoExt + '.path'
        
        writeListToTextFile(self.path.pathRaw, None , outputURI)
        
        detectedTokenList = self.path2ResultWordList(self.path, TOKEN_LEVEL)
        
        # DEBUG info
    #     decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)
        
    #     if self.logger.level == logging.DEBUG:
    #         path.printDurations()
        return detectedTokenList, self.path

    

        
