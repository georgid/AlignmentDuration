'''
Created on Oct 27, 2014

@author: joro
'''
import logging

### include src folder
import os
import sys
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

from LyricsParsing import expandlyrics2WordList, _constructTimeStampsForTokenDetected,\
    expandlyrics2SyllableList
from ParametersAlgo import ParametersAlgo
from visualize import visualizeMatrix, visualizeBMap, visualizePath,\
    visualizeTransMatrix
from src.onsets.OnsetSmoothing import OnsetSmoothingFunction
import subprocess
from src.onsets.OnsetDetector import frameNumberToTs

sys.path.append(os.path.join(os.path.dirname(__file__), '../test'))
from ParametersAlgo import ParametersAlgo


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 


from src.utilsLyrics.Utilz import writeListToTextFile


import numpy


if not ParametersAlgo.WITH_DURATIONS:
    pathHTKParser = os.path.join(parentDir, 'HMM')
    if pathHTKParser not in sys.path:    
        sys.path.append(pathHTKParser)



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 


logger = logging.getLogger(__name__)
loggingLevel = logging.WARNING
loggingLevel = logging.DEBUG
# loggingLevel = logging.INFO

logging.basicConfig(format='%(levelname)s:%(funcName)30s():%(message)s')
logger.setLevel(loggingLevel)

# other logger set in _Continuous



# in backtracking allow to start this much from end back`
BACKTRACK_MARGIN_PERCENT= 0.2
# BACKTRACK_MARGIN_PERCENT= 0.0


class Decoder(object):
    '''
    decodes one audio segment/chunk. 
    holds structures used in decoding and decoding result
    '''


    def __init__(self, sectionLink, lyricsWithModels, URIrecordingChunkNoExt, numStates=None, withModels=True):
        '''
        Constructor
        '''
        self.lyricsWithModels = lyricsWithModels
        self.URIrecordingChunkNoExt = URIrecordingChunkNoExt
        self.sectionLink = sectionLink
        
        '''
        of class HMM
        '''
        self.hmmNetwork = []
        
        self.onsetSmoothingFunction = OnsetSmoothingFunction(ParametersAlgo.ONSET_SIGMA_IN_FRAMES)
        self._constructHmmNetwork(numStates, withModels)
        self.hmmNetwork.logger.setLevel(ParametersAlgo.LOGGING_LEVEL)
        
        # Path class object
        self.path = None
    
    

#     def serializePosteriograms(self):
#         import pickle
#         URI_tmp = self.URIrecordingChunkNoExt + '.' + ParametersAlgo.OBS_MODEL + '.PPG.pkl'
#         if ParametersAlgo.OBS_MODEL == 'MLP' or ParametersAlgo.OBS_MODEL == 'MLP_fuzzy':
#             with open(URI_tmp, 'w') as f:
#                 pickle.dump(self.hmmNetwork.mlp_posteriograms.T, f)
#             
#         elif ParametersAlgo.OBS_MODEL == 'GMM':
#             with open(URI_tmp, 'w') as f:
#                 pickle.dump(self.hmmNetwork.B_map, f)


    def decodeAudio( self, featureExtractor, onsetDetector, listNonVocalFragments, fromTsTextGrid=0, toTsTextGrid=0):
        ''' decode path for given exatrcted features for audio
        HERE is decided which decoding scheme: with or without duration (based on WITH_DURATION parameter)
        '''
        if ParametersAlgo.DECODE_WITH_HTK:
            detectedWordList = self.decodeAudioWithHTK()
            return detectedWordList
        
        if not ParametersAlgo.WITH_ORACLE_PHONEMES:
            obs_model_type = ParametersAlgo.OBS_MODEL 
            if ParametersAlgo.OBS_MODEL == 'MLP_fuzzy':
                obs_model_type = 'MLP'
            
            self.hmmNetwork.set_PPG_filename(self.URIrecordingChunkNoExt + '.' + obs_model_type + '.PPG.pkl' )
            if  ParametersAlgo.WITH_DURATIONS:
                self.hmmNetwork.setNonVocal(listNonVocalFragments)
            
         
            
                
        self.hmmNetwork.initDecodingParameters(featureExtractor, onsetDetector, fromTsTextGrid, toTsTextGrid)

        

        # standard viterbi forced alignment
        if not ParametersAlgo.WITH_DURATIONS:
            
            psiBackPointer = self.hmmNetwork.viterbi_fast_forced()
            chiBackPointer = None
#            for kimseye region with note onsets for ISMIR poster SHi-KA-YET:
#             self.hmmNetwork.visualize_trans_probs(self.lyricsWithModels, 685,1095, 13,19)
        
        else:   # duration-HMM
            chiBackPointer, psiBackPointer = self.hmmNetwork._viterbiForcedDur()
            
           
        detectedWordList, self.path = self.backtrack(chiBackPointer, psiBackPointer )


        if ParametersAlgo.VISUALIZE:
            ax = visualizeBMap(self.hmmNetwork.B_map)        
#             visualizePath(ax,self.path.pathRaw, self.hmmNetwork.B_map)

#             ax = visualizeMatrix(self.hmmNetwork.phi, 'phi' )
#             ax = visualizeMatrix(self.hmmNetwork.psi, 'psi' )
            visualizePath(ax,self.path.pathRaw, self.hmmNetwork.B_map)

            
        print "\n"
#         DEBUG
#         self.path.printDurations()
        
        return detectedWordList
    
    def decodeAudioWithHTK(self):
                    dict_ = self.URIrecordingChunkNoExt + '.dict'
                    mlf = self.URIrecordingChunkNoExt + '.mlf'
                    self.lyricsWithModels.printDict(dict_, 0)
                    self.lyricsWithModels.printDict(mlf, 1)
    
            
                    outputHTKPhoneAlignedURI = alignWithHTK(self.URIrecordingChunkNoExt, dict_, mlf)
                    # TODO: parse output
                    pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
                    if pathEvaluation not in sys.path:
                        sys.path.append(pathEvaluation)
                    from WordLevelEvaluator import loadDetectedTokenListFromMlf
                    
                    detectedTokenList = loadDetectedTokenListFromMlf( outputHTKPhoneAlignedURI, whichLevel=2 )
                    return detectedTokenList
    

    
        
    def _constructHmmNetwork(self,  numStates,  withModels ):
        '''
        top level-function: costruct self.hmmNEtwork that confirms to guyz's code 
        '''

        ######## construct transition matrix
        #######
        
        transMatrices = None
        if not ParametersAlgo.WITH_DURATIONS:
            if ParametersAlgo.FOR_JINGJU:
                sys.exit("trying to run viterbi with no duration modeling for Jingju. Not implemented.")
            # construct means, covars, and all the rest params
            #########    
            transMatrices = list()
            for onsetDist in range(ParametersAlgo.ONSET_SIGMA_IN_FRAMES + 1):
                transMatrices.append( self._constructTransMatrix(self.lyricsWithModels, onsetDist) )
            
            transMatrices.append( self._constructTransMatrix(self.lyricsWithModels,  onsetDist = ParametersAlgo.ONSET_SIGMA_IN_FRAMES + 1) )
        

        
        if ParametersAlgo.OBS_MODEL == 'GMM': 
            from src.hmm.continuous.GMHMM  import GMHMM
            self.hmmNetwork = GMHMM(self.lyricsWithModels.statesNetwork,  transMatrices)
#             print self.hmmNetwork.__class__.__bases__[0]
        elif ParametersAlgo.OBS_MODEL == 'MLP':
            from src.hmm.continuous.MLPHMM  import MLPHMM
            self.hmmNetwork = MLPHMM(self.lyricsWithModels.statesNetwork,  transMatrices)
        elif ParametersAlgo.OBS_MODEL == 'MLP_fuzzy':
            from src.hmm.continuous.MLP_fuzzyMappedHMM  import MLP_fuzzyMappedHMM
            self.hmmNetwork = MLP_fuzzyMappedHMM(self.lyricsWithModels.statesNetwork,  transMatrices)

    

    
    def  _constructTransMatrix(self, lyricsWithModels, onsetDist=0):
        '''
        iterate over states and put their wait probs in a matrix 
        '''
        # just for initialization totalNumPhonemes
        totalNumStates = len(lyricsWithModels.statesNetwork)
        transMAtrix = numpy.zeros((totalNumStates, totalNumStates), dtype=numpy.double)
#         transMAtrix.fill(0.1)
        
        for idxCurrState in range(len(lyricsWithModels.statesNetwork)):
             
            stateWithDur = lyricsWithModels.statesNetwork[idxCurrState]
            
            
            if (idxCurrState+2) < transMAtrix.shape[1]: # MAIN CASE
           
                    nextState = lyricsWithModels.statesNetwork[idxCurrState+1]
                    
                    if onsetDist <= ParametersAlgo.ONSET_SIGMA_IN_FRAMES:
                        forwProb1, forwProb2 = self.defineForwardTransProbs(lyricsWithModels.statesNetwork, idxCurrState, onsetDist)
                    else: # going to next phoneme=sp or skipping it is equaly likely 
                        
                        
                        if  nextState.phoneme.ID == 'sp':
                            forwProb1 = 1 - stateWithDur.getWaitProb() / 2.0
                            forwProb2 = 1 - stateWithDur.getWaitProb() / 2.0
                        else: # no note onset and no sp: use transition trained from models_makam
                            forwProb1 = 1 - stateWithDur.getWaitProb() 
                            forwProb2 = 0
                   
                    while (forwProb1 + forwProb2 >= 1): # waitProb = 1-forw-forw2
                       forwProb1 /= 2.0
                       forwProb2 /= 2.0
                    transMAtrix[idxCurrState, idxCurrState] = 1 - forwProb1 - forwProb2 # waitProb
                    transMAtrix[idxCurrState, idxCurrState + 1] = forwProb1
                    transMAtrix[idxCurrState, idxCurrState + 2] = forwProb2  
                    
                    
            elif (idxCurrState+1) < transMAtrix.shape[1]: # SPECIAL CASE: two last states
                       
                if onsetDist <= ParametersAlgo.ONSET_SIGMA_IN_FRAMES:
                    # forwProb = 0
                        forwProb1, forwProb2 = self.defineForwardTransProbs(lyricsWithModels.statesNetwork, idxCurrState, onsetDist)
                else:
                                       
                    forwProb1 = 1 - stateWithDur.getWaitProb()
                
                transMAtrix[idxCurrState, idxCurrState] = 1 - forwProb1
                transMAtrix[idxCurrState, idxCurrState+1] = forwProb1
            
            else: #  SPECIAL CASE: at very last state
                
                transMAtrix[idxCurrState, idxCurrState] = stateWithDur.getWaitProb() # waitProb
            

        
        # avoid log(0) 
        indicesZero = numpy.where(transMAtrix==0)
        transMAtrix[indicesZero] = sys.float_info.min
        
        ###### normalize trans probs to sum to 1.
        from sklearn.preprocessing import normalize
        transMAtrix = normalize(transMAtrix, axis=1, norm='l1')
        
        if ParametersAlgo.VISUALIZE:   
            figureTitle = "onsetDist = {}".format(onsetDist)  
            visualizeTransMatrix(transMAtrix, figureTitle, lyricsWithModels.phonemesNetwork )
        return numpy.log(transMAtrix)   
            
        

    

            
      
        
        
    def path2ResultTokenList(self, path, tokenLevel='words'):
        '''
        makes sense of path indices : maps numbers to states and phonemes.
        uses self.lyricsWithModels.statesNetwork and self.lyricsWithModels.listWords) 
        to be called after decoding
        
        Parameters:
        path of type hmm.Path
        '''
        # indices in pathRaw
        self.path = path
        self.path.path2stateIndices()
        
        #sanity check
        numStates = len(self.lyricsWithModels.statesNetwork)
        numdecodedStates = len(self.path.indicesStateStarts)
        
        if ParametersAlgo.WITH_DURATIONS:
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
        elif tokenLevel == 'phonemes':
            
            detectedTokenList = []
            for i,(state, count_first_state) in enumerate(zip(self.lyricsWithModels.statesNetwork, self.path.indicesStateStarts)):
                if i == len(self.path.indicesStateStarts)-1:
                    count_last_state = len(path.pathRaw)
                else:
                    count_last_state = self.path.indicesStateStarts[i+1]
                
                startTs = frameNumberToTs(count_first_state)
                endTs = frameNumberToTs(count_last_state)
                detectedPhoneme = [startTs, endTs, state.phoneme.ID, -1]
                
                detectedTokenList.append(  detectedPhoneme)
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
        from src.hmm.Path import Path
        self.path =  Path(chiBackPointer, psiBackPointer, self.hmmNetwork.phi, self.hmmNetwork )
        
        pathUtils = os.path.join(parentDir, 'utilsLyrics')
        if pathUtils not in sys.path:
            sys.path.append(pathUtils )
    

        if ParametersAlgo.WITH_ORACLE_PHONEMES:
            outputURI = self.URIrecordingChunkNoExt + '.path_oracle'
        else:
            outputURI = self.URIrecordingChunkNoExt + '.path'
        
        writeListToTextFile(self.path.pathRaw, None , outputURI)
        
        detectedTokenList = self.path2ResultTokenList(self.path, ParametersAlgo.DETECTION_TOKEN_LEVEL)
        
        # DEBUG info
    #     decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)
        
    #     if self.logger.level == logging.DEBUG:
    #         path.printDurations()
        return detectedTokenList, self.path

    def defineForwardTransProbs(self, statesNetwork, idxCurrState, onsetDist):
        '''
        at onset present, change trasna probs based on rules.
        consider special case sp
        '''
        
        nextStateWithDur = statesNetwork[idxCurrState+1]
        currStateWithDur = statesNetwork[idxCurrState]
                    
     
        if not ParametersAlgo.ONLY_MIDDLE_STATE:
            sys.exit("align.Decoder.defineWaitProb  implemented only for 1-state phonemes ")
        
    #     if idxState == len(statesNetwork)-1: # ignore onset at last phonemes
    #         return currStateWithDur.getWaitProb()
        
        currPhoneme = currStateWithDur.phoneme
        nextPhoneme = nextStateWithDur.phoneme
        
        # normally should go to only next state as in forced alignment
        forwProb1 = self.calcForwProbWithRules(currStateWithDur, nextStateWithDur, onsetDist )
        forwProb2 = 0
        
        if nextPhoneme.ID == 'sp' and (idxCurrState+2) < len(statesNetwork):   #### add skipping forward trans prob
            
            ### skipping sp to next state
            nextNextStateWithDur = statesNetwork[idxCurrState+2]
            currPhoneme.setIsLastInSyll(1) # 
            forwProb2 = self.calcForwProbWithRules(currStateWithDur, nextNextStateWithDur, onsetDist )
            currPhoneme.setIsLastInSyll(0)
            
    
    
        return forwProb1, forwProb2
        
 
        


    def calcForwProbWithRules(self, currStateWithDur, followingStateWithDur, onsetDist):  
        currPhoneme = currStateWithDur.phoneme
        followingPhoneme = followingStateWithDur.phoneme
        forwProb = 1 - currStateWithDur.getWaitProb()
        onsetWeight = self.onsetSmoothingFunction.calcOnsetWeight(onsetDist)
        
        if currPhoneme.isLastInSyll(): # inter-syllable
                if currPhoneme.isVowel() and not followingPhoneme.isVowelOrLiquid(): # rule 1
                    return max(forwProb - onsetWeight * ParametersAlgo.Q_WEIGHT_TRANSITION, 0.01) # 0.1 instead of 0 becasue log(0) will give -inf
                elif not currPhoneme.isVowelOrLiquid() and followingPhoneme.isVowelOrLiquid(): # rule 2
                    return forwProb + onsetWeight * ParametersAlgo.Q_WEIGHT_TRANSITION 
        else: # not last in syllable, intra-syllable
                if currPhoneme.isVowel() and not followingPhoneme.isVowel(): # rule 3
                    return max(forwProb - onsetWeight * ParametersAlgo.Q_WEIGHT_TRANSITION, 0.01)
                elif not currPhoneme.isVowelOrLiquid() and followingPhoneme.isVowelOrLiquid(): # rule 4
                    return forwProb + onsetWeight * ParametersAlgo.Q_WEIGHT_TRANSITION
                elif currPhoneme.isVowel() and followingPhoneme.isVowel():
                    logging.warning("two consecutive vowels {} and {} in a syllable. not implemented! Make sure ONLY_MIDDLE_STATE is set true. 3-state models not implemented".format(currPhoneme.ID, followingPhoneme.ID))
                    return forwProb
        
        #  onset has no contribution in other cases    
        return forwProb


    
def alignWithHTK(URIRecordingChunkNoExt, dict_, mlf):
    #     
    #     pipe = subprocess.Popen([PATH_TO_HVITE, '-l', "'*'", '-A', '-D', '-T', '1', '-b', 'sil', '-C', PATH_TO_CONFIG_FILES + 'config_singing', '-a', \
    #                                  '-H', self.pathToHtkModel, '-H',  DUMMY_HMM_URI , '-H',  MODEL_NOISE_URI , '-i', '/tmp/phoneme-level.output', '-m', \
    #                                  '-w', wordNetwURI, '-y', 'lab', dictName, PATH_TO_HMMLIST, mfcFileName], stdout=self.currLogHandle)
        
        logName = '/tmp/log_all'
        currLogHandle = open(logName, 'w')
        currLogHandle.flush()
        decodedWordlevelMLF = URIRecordingChunkNoExt + '.out.mlf'    
            
        
        path, fileName = os.path.split(URIRecordingChunkNoExt)
        path, fold = os.path.split(path) # which Fold
        
        PATH_HTK_MODELS = '/home/georgid/Documents/JingjuSingingAnnotation-master/lyrics2audio/models/hmmdefs_' + fold 
        PATH_TO_HMMLIST = ' /home/georgid/Documents/JingjuSingingAnnotation-master/lyrics2audio/models/hmmlist'
           
        command = [ParametersAlgo.PATH_TO_HVITE, '-a', '-m', '-I', mlf, '-C', ParametersAlgo.PATH_TO_CONFIG_FILES + 'config',  \
                                     '-H', PATH_HTK_MODELS,  '-i', decodedWordlevelMLF,  \
                                      dict_, PATH_TO_HMMLIST, URIRecordingChunkNoExt + '.wav']   
        pipe = subprocess.Popen(command, stdout = currLogHandle)
            
        pipe.wait()      
        return decodedWordlevelMLF

