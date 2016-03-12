'''
Created on Oct 27, 2014

@author: joro
'''
import os
import sys
import logging
from LyricsParsing import expandlyrics2WordList, _constructTimeStampsForTokenDetected,\
    expandlyrics2SyllableList
from Constants import NUM_DIMENSIONS, numMixtures
from hmm.ParametersAlgo import ParametersAlgo
from scripts.OnsetDetector import parserNoteOnsets


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 


from utilsLyrics.Utilz import writeListOfListToTextFile, writeListToTextFile


import numpy

# use duraiton-based decoding (HMMDuraiton package) or just plain viterbi (HMM package) 
# if false, use transition probabilities from htkModels
WITH_DURATIONS= 0



if not WITH_DURATIONS:
    pathHMM = os.path.join(parentDir, 'HMM')
    if pathHMM not in sys.path:    
        sys.path.append(pathHMM)





logger = logging.getLogger(__name__)
# loggingLevel = logging.WARNING
loggingLevel = logging.DEBUG
loggingLevel = logging.INFO

logging.basicConfig(format='%(levelname)s:%(funcName)30s():%(message)s')
logger.setLevel(loggingLevel)

# other logger set in _Continuous

# level into which to segments decoded result stateNetwork
DETECTION_TOKEN_LEVEL= 'syllables'
DETECTION_TOKEN_LEVEL= 'words'

# in backtracking allow to start this much from end back
BACKTRACK_MARGIN_PERCENT= 0.2
# BACKTRACK_MARGIN_PERCENT= 0.0


class Decoder(object):
    '''
    decodes one audio segment/chunk. 
    holds structures used in decoding and decoding result
    '''


    def __init__(self, lyricsWithModels, URIrecordingChunkNoExt, ALPHA, numStates=None, withModels=True):
        '''
        Constructor
        '''
        self.lyricsWithModels = lyricsWithModels
        self.URIrecordingChunkNoExt = URIrecordingChunkNoExt
        
        '''
        of class HMM
        '''
        self.hmmNetwork = []
        
        self._constructHmmNetwork(numStates, float(ALPHA), withModels)
        self.hmmNetwork.logger.setLevel(loggingLevel)
        
        # Path class object
        self.path = None
    
    
    def decodeAudio( self, observationFeatures, listNonVocalFragments, usePersistentFiles, onsetTimestamps, fromTsTextGrid=0, toTsTextGrid=0):
        ''' decode path for given exatrcted features for audio
        HERE is decided which decoding scheme: with or without duration (based on WITH_DURATION parameter)
        '''
        
        
        if not ParametersAlgo.WITH_ORACLE_PHONEMES:
            self.hmmNetwork.setPersitentFiles( usePersistentFiles, '' )
            if  WITH_DURATIONS:
                self.hmmNetwork.setNonVocal(listNonVocalFragments)
            
            # double check that features are in same dimension as model
            if observationFeatures.shape[1] != NUM_DIMENSIONS:
                sys.exit("dimension of feature vector should be {} but is {} ".format(NUM_DIMENSIONS, observationFeatures.shape[1]) )
            
                
        self.hmmNetwork.initDecodingParameters(observationFeatures, onsetTimestamps, fromTsTextGrid, toTsTextGrid)

        # standard viterbi forced alignment
        if not WITH_DURATIONS:
            
            psiBackPointer = self.hmmNetwork.viterbi_fast_forced()
            chiBackPointer = None
        
        else:   # duration-HMM
            chiBackPointer, psiBackPointer = self.hmmNetwork._viterbiForcedDur()
            
#         visualizeMatrix(self.hmmNetwork.phi)
        visualizeMatrix(self.hmmNetwork.psi)

        
           
        detectedWordList, self.path = self.backtrack(chiBackPointer, psiBackPointer )
            
        print "\n"
         # DEBUG
#         self.path.printDurations()
        
        return detectedWordList
    
    

        
    def _constructHmmNetwork(self,  numStates, ALPHA,  withModels ):
        '''
        top level-function: costruct self.hmmNEtwork that confirms to guyz's code 
        '''

        ######## construct transition matrix
        #######
        
        
        if  WITH_DURATIONS:
            from hmm.continuous.DurationGMHMM  import DurationGMHMM
            # note: no trans matrix because only forced Viterbi implemented 
            self.hmmNetwork = DurationGMHMM(self.lyricsWithModels.statesNetwork, numMixtures, NUM_DIMENSIONS)
            self.hmmNetwork.setALPHA(ALPHA)
        
        else: # with no durations standard Viterbi
        
            # construct means, covars, and all the rest params
            #########    
            
            transMAtrix = self._constructTransMatrix(self.lyricsWithModels, atNoteOnsets = 0)
            transMAtrixOnsets = self._constructTransMatrix(self.lyricsWithModels, atNoteOnsets = 1)
            from hmm.continuous.GMHMM  import GMHMM
            self.hmmNetwork = GMHMM(self.lyricsWithModels.statesNetwork, numMixtures, NUM_DIMENSIONS, transMAtrix, transMAtrixOnsets)
    
    

    
    def  _constructTransMatrix(self, lyricsWithModels, atNoteOnsets=0):
        '''
        iterate over states and put their wait probs in a matrix 
        '''
        # just for initialization totalNumPhonemes
        totalNumStates = len(lyricsWithModels.statesNetwork)
        transMAtrix = numpy.zeros((totalNumStates, totalNumStates), dtype=numpy.double)
        
        for idxCurrState in range(len(lyricsWithModels.statesNetwork)):
             
            stateWithDur = lyricsWithModels.statesNetwork[idxCurrState]
            if atNoteOnsets:
                forwProb = defineForwardTransProb(lyricsWithModels.statesNetwork, idxCurrState)
            else:
                forwProb = 1 - stateWithDur.waitProb
            
            transMAtrix[idxCurrState, idxCurrState] = 1- forwProb # waitProb
            if (idxCurrState+1) < transMAtrix.shape[1]:
                transMAtrix[idxCurrState, idxCurrState+1] = forwProb
         
        # avoid log(0) 
        indicesZero = numpy.where(transMAtrix==0)
        transMAtrix[indicesZero] = sys.float_info.min
        
        ###### normalize
        from sklearn.preprocessing import normalize
        transMAtrix = normalize(transMAtrix, axis=1, norm='l1')
             
#         visualizeMatrix(transMAtrix, atNoteOnsets+1)
        return numpy.log(transMAtrix)   
            
        

    

            
      
        
        
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
    
    
    
    def backtrack(self, chiBackPointer, psiBackPointer):
        ''' 
        backtrack optimal path of states from backpointers
        interprete states to words      
        '''
        
        # self.hmmNetwork.phi is set in decoder.decodeAudio()
        from hmm.Path import Path
        self.path =  Path(chiBackPointer, psiBackPointer, self.hmmNetwork.phi, self.hmmNetwork )
        
        pathUtils = os.path.join(parentDir, 'utilsLyrics')
        if pathUtils not in sys.path:
            sys.path.append(pathUtils )
    

        if ParametersAlgo.WITH_ORACLE_PHONEMES:
            outputURI = self.URIrecordingChunkNoExt + '.path_oracle'
        else:
            outputURI = self.URIrecordingChunkNoExt + '.path'
        
        writeListToTextFile(self.path.pathRaw, None , outputURI)
        
        detectedTokenList = self.path2ResultWordList(self.path, DETECTION_TOKEN_LEVEL)
        
        # DEBUG info
    #     decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)
        
    #     if self.logger.level == logging.DEBUG:
    #         path.printDurations()
        return detectedTokenList, self.path

def defineForwardTransProb(statesNetwork, idxState):
    '''
    change trasna probs based on rules 
    '''
    q = 0.01
    r = 0.99
    if not ParametersAlgo.ONLY_MIDDLE_STATE:
        sys.exit("align.Decoder.defineWaitProb  implemented only for 1-state phonemes ")
    
    currStateWithDur = statesNetwork[idxState]
    if idxState == len(statesNetwork)-1: # ignore onset at last phonemes
        return currStateWithDur.waitProb
    
    nextStateWithDur =  statesNetwork[idxState+1]
    currPhoneme = currStateWithDur.phoneme
    nextPhoneme = nextStateWithDur.phoneme
    
    if currPhoneme.isLastInSyll(): # inter-syllable
        if currPhoneme.isVowel() and not nextPhoneme.isVowelOrLiquid(): # rule 1
            return q
        elif not currPhoneme.isVowel() and nextPhoneme.isVowelOrLiquid(): # rule 2
            return r 
    else: # not last in syllable, intra-syllable
        if currPhoneme.isVowel() and not nextPhoneme.isVowel(): # rule 3
            return q
        elif not currPhoneme.isVowelOrLiquid() and nextPhoneme.isVowel(): # rule 4:
            return r
        elif currPhoneme.isVowel() and nextPhoneme.isVowel():
            logging.warning("two consecutive vowels in a syllable. not implemented! {} and {}".format(currPhoneme.ID, nextPhoneme.ID))
            return 1
            
        
    #  onset has no contribution in other cases    
    return currStateWithDur.waitProb
    
def visualizeMatrix(psi, figNum=1):
#         psi = numpy.flipud(psi)
#         psi = numpy.rot90(psi)
        import matplotlib.pyplot as plt
        plt.figure(figNum)
        ax = plt.imshow(psi, interpolation='none')
        plt.colorbar(ax)
        plt.grid(True)
#         plt.tight_layout()
        plt.show()  
        
