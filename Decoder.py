'''
Created on Oct 27, 2014

@author: joro
'''
import os
import sys
import logging
from LyricsParsing import expandlyrics2WordList, _constructTimeStampsForWordDetected
from Constants import numDimensions, numMixtures


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )
from Utilz import writeListOfListToTextFile, writeListToTextFile


import numpy

# use duraiton-based decoding (HMMDuraiton package) or just plain viterbi (HMM package) 
# if false, use transition probabilities from htkModels
WITH_DURATIONS= True

# WITH_DURATIONS= False



if WITH_DURATIONS:
    pathHMM = os.path.join(parentDir, 'HMMDuration')
else:
    pathHMM = os.path.join(parentDir, 'HMM')


if pathHMM not in sys.path:    
    sys.path.append(pathHMM)

# if WITH_DURATIONS:
#     from hmm.continuous.DurationPdf import MINIMAL_PROB

from hmm.Path import Path
from hmm.continuous.GMHMM  import GMHMM

logger = logging.getLogger(__name__)
loggingLevel = logging.DEBUG
loggingLevel = logging.INFO

logging.basicConfig(format='%(levelname)s:%(funcName)30s():%(message)s')
logger.setLevel(loggingLevel)



class Decoder(object):
    '''
    holds structures used in decoding and decoding result
    '''


    def __init__(self, lyricsWithModels, ALPHA,  numStates=None, withModels=True):
        '''
        Constructor
        '''
        self.lyricsWithModels = lyricsWithModels
        
        '''
        of class HMM
        '''
        self.hmmNetwork = []
                
        
        self._constructHmmNetwork(numStates, float(ALPHA), withModels)
        self.hmmNetwork.logger.setLevel(loggingLevel)
        
        # Path class object
        self.path = None
    
    def decodeAudio( self, observationFeatures, usePersistentFiles, URI_recording_noExt, listDurations):
        ''' decode path for given exatrcted features for audio
        HERE is decided which decoding scheme: with or without duration (based on WITH_DURATION parameter)
        '''
        if self.lyricsWithModels.ONLY_MIDDLE_STATE:
            URI_bmap = URI_recording_noExt + '.bmap_onlyMiddleState'
        else:             
            URI_bmap = URI_recording_noExt + '.bmap'
        
        
        
        self.hmmNetwork.setPersitentFiles( usePersistentFiles, URI_bmap )
        
        # double check that features are in same dimension as model
        if observationFeatures.shape[1] != numDimensions:
            sys.exit("dimension of feature vector should be {} but is {} ".format(numDimensions, observationFeatures.shape[1]) )
#         observationFeatures = observationFeatures[0:100,:]
        
        if  WITH_DURATIONS:
            
            # transMatrix for 0 state which is silence
            transMatrix = self.lyricsWithModels.phonemesNetwork[0].getTransMatrix()
            self.hmmNetwork.setWaitProbSilState(transMatrix[2,2])
            
            self.hmmNetwork.setDurForStates(listDurations)
        
#         if os.path.exists(PATH_CHI) and os.path.exists(PATH_PSI): 
#             chiBackPointer = numpy.loadtxt(PATH_CHI)
#             psiBackPointer = numpy.loadtxt(PATH_PSI)
#                
#         else:

        # standard viterbi forced alignment
        if not WITH_DURATIONS:
            path_, psi, delta = self.hmmNetwork._viterbiForced(observationFeatures)
            self.path =  Path(None, None)
            self.path.setPatRaw(path_)
            
        # duration-HMM
        else:
        
            chiBackPointer, psiBackPointer = self.hmmNetwork._viterbiForcedDur(observationFeatures)
            
#             writeListOfListToTextFile(chiBackPointer, None , PATH_CHI)
#             writeListOfListToTextFile(psiBackPointer, None , PATH_PSI)
                
            self.path =  Path(chiBackPointer, psiBackPointer)
            print "\n"
         # DEBUG
#         self.path.printDurations()
#         writeListToTextFile(self.path.pathRaw, None , '/tmp/path')
        
    
    
    
    
        
    def _constructHmmNetwork(self,  numStates, ALPHA, withModels ):
        '''
        top level-function: costruct self.hmmNEtwork that confirms to guyz's code 
        '''
        
    #     sequencePhonemes = sequencePhonemes[0:4]
        
        
        ######## construct transition matrix
        #######
        if not WITH_DURATIONS:
            transMAtrix = self._constructTransMatrixHMMNetwork(self.lyricsWithModels.phonemesNetwork)

#        DEBUG
#  writeListOfListToTextFile(transMAtrix, None , '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentStep/transMatrix')
        
        # construct means, covars, and all the rest params
        #########
       
        if numStates == None:
            numStates = len(self.lyricsWithModels.statesNetwork) 
        
        means, covars, weights, pi = self._constructHMMNetworkParameters(numStates,  withModels)
        
        if  WITH_DURATIONS:
            self.hmmNetwork = GMHMM(numStates,numMixtures,numDimensions,None,means,covars,weights,pi,init_type='user',verbose=True)
            self.hmmNetwork.setALPHA(ALPHA)
        else:
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
        tranform other htkModel params to  format of gyuz's hmm class
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
    
            
      
        
        
    def path2ResultWordList(self):
        '''
        makes sense of path indices : maps numbers to states and phonemes, uses self.lyricsWithModels.statesNetwork and self.lyricsWithModels.listWords) 
        to be called after decoding
        '''
        # indices in pathRaw
        self.path._path2stateIndices()
        
        #sanity check
        numStates = len(self.lyricsWithModels.statesNetwork)
        numdecodedStates = len(self.path.indicesStateStarts)
        
        if numStates != numdecodedStates:
            logging.warn("detected path has {} states, but stateNetwork transcript has {} states".format( numdecodedStates, numStates ) )
            # num misssed states in the beginning of the path
            howManyMissedStates = numStates - numdecodedStates
            # WORKAROUND: assume missed states start at time 0
            for i in range(howManyMissedStates):
                self.path.indicesStateStarts[:0] = [0]
        dummy= 0
        detectedWordList = expandlyrics2WordList (self.lyricsWithModels, self.path, dummy, _constructTimeStampsForWordDetected)
        
        return detectedWordList 
        
    
    

    

        
