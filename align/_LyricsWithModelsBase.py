'''
Created on Oct 27, 2014

@author: joro
'''
from Lyrics import Lyrics
import os
import sys
from Constants import NUM_FRAMES_PERSECOND
import Queue
import math
from ParametersAlgo import ParametersAlgo
import logging
from for_makam.Phoneme import Phoneme
from for_jingju.PhonemeJingju import PhonemeJingju

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 
    
from hmm.StateWithDur import StateWithDur

from htkparser.htk_converter import HtkConverter
from Decoder import logger

from hmm.Parameters import MAX_SILENCE_DURATION

# htkModelParser = os.path.join(parentDir, 'htk2s3')
# sys.path.append(htkModelParser)

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)




class _LyricsWithModelsBase(Lyrics):
    '''
    lyrics with each Phoneme having a link to a models_makam of class type htkModel from htkModelParser
    No handling of durationInMinUnit information. For it see Decoder.Decoder.decodeAudio 
    '''


    def __init__(self,  lyrics, htkParserOrFold, deviationInSec,  withPaddedSilence=True ):
        '''
        being  linked to models, allows expansion to network of states 
        '''
        
#       flag to add a state 'sp' with exponential disrib at begining and end  
        self.withPaddedSilence = withPaddedSilence
        
        Lyrics.__init__(self, lyrics.listWords)
        
        self.deviationInSec = deviationInSec
        # list of class type StateWithDur
        self.statesNetwork = []
        
        self.duratioInFramesSet = False

        self._linkToModels(htkParserOrFold)
        
        

    
    
    def _addPaddedSilencePhonemes(self):
        
        
        if ParametersAlgo.FOR_MAKAM:
            phonemeSp =  Phoneme('sp');
        elif ParametersAlgo.FOR_JINGJU:
            phonemeSp =  PhonemeJingju('sp');
        
        if self.withPaddedSilence:    
            
            phonemeSp.setIsLastInSyll(True)
            self.phonemesNetwork.insert(0, phonemeSp)
            self.phonemesNetwork.append(phonemeSp)
       
    


    def _phonemes2stateNetwork(self):
        '''
        expand self.phonemeNetwork to self.statesNetwork
        assign phoneme a pointer <setNumFirstState> to its initial state in the state network (serves as link among the two)
        each state gets 1/n-th of total num of states. 
        '''
         
        
        self.statesNetwork = []
        stateCount = 0
        

        
        for phnIdx, phoneme in enumerate(self.phonemesNetwork):
            
            
            # set number of first state
            phoneme.setNumFirstState(stateCount)
            
      
            
            
            deviation = self.deviationInSec
            
            if not phoneme.isVowel(): # consonant
                    deviation = ParametersAlgo.CONSONANT_DURATION_DEVIATION
            
            if ParametersAlgo.WITH_DURATIONS:
                distributionType='normal'
                ### for Makam, lyrics are read from score and sp is considered a consonant with short deviation. 
                ### only first and last phonemes (which are sp) will get padded silence 
                if (phnIdx == 0 or phnIdx == len(self.phonemesNetwork)-1 ) and self.withPaddedSilence:
                    distributionType='exponential'
                
                if ParametersAlgo.FOR_JINGJU and phoneme.ID == 'sp':
                    distributionType='exponential'
            else:
                distributionType='exponential'
                
            
            stateIndices = range( phoneme.getNumStates())
            if ParametersAlgo.ONLY_MIDDLE_STATE and phoneme.getNumStates() == 3: # take only middle state. 1 is middle in 0,1,2
                stateIndices = [1]
                    
            for idxState in stateIndices :
          
                currStateWithDur = self._createStateWithDur(phoneme,  idxState, distributionType, deviation)
                self.statesNetwork.append(currStateWithDur)
                stateCount += 1
        
        
#    def _phonemes2stateNetworkWeights(self):
#         '''
#         expand to self.statesNetwork. 
#         each state gets a durational proportional to  the weighting probs.
#        @deprecated: 
#         '''
#         
#         self.statesNetwork = []
#         stateCount = 0
#         
#         for phoneme in self.phonemesNetwork:
#             
#             phoneme.setNumFirstState(stateCount)
#             # update
#             currStateCount = len(phoneme.htkModel.states)
#             stateCount += currStateCount
#             
#             
#             currTransMatrix = phoneme.getTransMatrix()
#             currTransMatrix = currTransMatrix[1:-1,1:-1]
#             
#             # sanity check
#             if not currStateCount ==  currTransMatrix.shape[0]:
#                 sys.exit("Error on reading htk models_makam: transMatrix for phoneme {} has not same num states as states ", phoneme.ID)
#             
#             waitProbs = []
#             for currState in range(currStateCount):
#                 currWaitProb =  currTransMatrix[currState, currState]
#                 waitProbs.append(currWaitProb)
#             
#             statesList = phoneme.htkModel.states
#             # assign durations
#             for idxState, (numStateFromHtk, state ) in enumerate( phoneme.htkModel.states):
#                  currStateWithDur = StateWithDur(state.mixtures, phoneme, idxState)
#                  
#                  # normalize to sum to one
#                  weigthState = float(waitProbs[idxState]) / float(sum(waitProbs))
#                  dur = float(phoneme.durationInFrames) * float(weigthState)
#                  
#                  currStateWithDur.setDurationInFrames( dur )
#                  self.statesNetwork.append(currStateWithDur)
#         
#         

                
    
    
    
    def printWordsAndStatesAndDurations(self, resultPath):
        '''
        debug word begining states
        '''
        
        if resultPath == None:
            logger.warn("printitg current lyrics with results not possible. resultPath is None. Make sure you decoded correctly! ")
            return
        
        for word_ in self.listWords:
            print word_ , ":" 
            for syllable_ in word_.syllables:
                for phoneme_ in syllable_.phonemes:
                    print "\t phoneme: " , phoneme_
                    countPhonemeFirstState =  phoneme_.numFirstState

                    for nextState in range(phoneme_.getNumStates()):
                        print "\t\t state: {} durationInMinUnit (in Frames): {} DURATION RESULT: {}, t_end: {}".format(countPhonemeFirstState + nextState, 
                                                                                                self.statesNetwork[countPhonemeFirstState + nextState].durationInFrames,
                                                                                                 resultPath.durations[countPhonemeFirstState + nextState], 
                                                                                                 resultPath.endingTimes[countPhonemeFirstState + nextState])

                    
    def  printWordsAndStates(self):
        '''
        debug word begining states
        NOTE: code redundant with method  printWordsAndStatesAndDurations() 
        TODO: to reduce code: use lyrics parsing . or like previous
        '''
        
        for word_ in self.listWords:
            print word_ , ":" 
            for syllable_ in word_.syllables:
                for phoneme_ in syllable_.phonemes:
                    print "\t phoneme: " , phoneme_
                    countPhonemeFirstState =  phoneme_.numFirstState
                    
                    print " durationInMinUnit in min unit: {}".format(phoneme_.durationInMinUnit)
                    for nextState in range(phoneme_.getNumStates()):
                                    stateWithDur = self.statesNetwork[countPhonemeFirstState + nextState]
                                    try:
                                        currDurationInFrames = stateWithDur.durationInFrames
                                    except AttributeError:
                                        currDurationInFrames = 0
                                    print "\t\t state: {} durationInMinUnit (in Frames): {}".format(countPhonemeFirstState + nextState, currDurationInFrames)
                                                                                                           
                
                
    def duration2numFrameDuration(self, observationFeatures, URI_recording_noExt,  tempoCoefficient = 1.0):
        '''
        get relative tempo (numFramesPerMinUnit) for given audio chunk
        and
        setDuration HowManyFrames for each syllable based on tempo 
        and
        distribute phoneme durations in phonemesNetwork
        '''

        totalScoreDur = self.getTotalDuration()
#         numFramesPerMinUnit   = float(len(observationFeatures) - 2 * AVRG_TIME_SIL * NUM_FRAMES_PERSECOND) / float(totalScoreDur)
        lenObsFeatures = len(observationFeatures)
        numFramesPerMinUnit   = float(tempoCoefficient * lenObsFeatures ) / float(totalScoreDur)
        logger.debug("numFramesPerMinUnit = {} for audiochunk {} ".format( numFramesPerMinUnit, URI_recording_noExt))
        
        for word_ in self.listWords:
            for syllable_ in word_.syllables:
                
                if syllable_.durationInMinUnit == 0: # workaround for unknown values. better: if whole sentence unknown use withRules. 
                    logging.warning("syllable {} with duration = 0".format(syllable_))
                
                    syllable_.durationInMinUnit = 1
                
                numFramesInSyllable = round(float(syllable_.durationInMinUnit) * numFramesPerMinUnit)
                if numFramesInSyllable == 0.0:
                    sys.exit(" frames per syllable {} are 0.0. Check durationInMinUnit {} and numFramesPerMinUnit={}".format(syllable_.text, syllable_.durationInMinUnit,  numFramesPerMinUnit))
                    
                # TODO: set here syllables from score
                syllable_.setDurationInNumFrames(numFramesInSyllable)
        
        # consonant-handling policy
        self.calcPhonemeDurs()
        
        self._phonemes2stateNetwork()
#             self._phonemes2stateNetworkWeights()
        
        self.duratioInFramesSet = True
    
    
    def duration2numFrameDurationSertanTempo(self, recordingMBID,  tempoCoefficient = 1.0):
        '''
        get relative tempo (numFramesPerMinUnit) for given audio chunk
        and
        setDuration HowManyFrames for each syllable based on tempo 
        and
        distribute phoneme durations in phonemesNetwork
        '''

        numFramesPerMinUnit  = float(tempoCoefficient) *  getTempo(recordingMBID)
        logger.debug("numFramesPerMinUnit = {} for recording {} ".format( numFramesPerMinUnit, recordingMBID))
        
        for word_ in self.listWords:
            for syllable_ in word_.syllables:

                numFramesInSyllable = round(float(syllable_.durationInMinUnit) * numFramesPerMinUnit)
                if numFramesInSyllable == 0.0:
                    sys.exit(" frames per syllable {} are 0.0. Check numFramesPerMinUnit={}".format(syllable_.text, numFramesPerMinUnit))
                    
                # TODO: set here syllables from score
                syllable_.setDurationInNumFrames(numFramesInSyllable)
        
        # consonant-handling policy
        self.calcPhonemeDurs()

        self._phonemes2stateNetwork()
#             self._phonemes2stateNetworkWeights()
        
        self.duratioInFramesSet = True   
    
    
    def setPhonemeNumFrameDurs(self,  phoenemeAnnotaions):
        '''
        set durations in num frame durations read directly from textGrid. Used in oracle. 
        does not consider empty tokens (silences) at beginning and end, but reads sp tokens
        double check if phoenemes are the same as in lyrics 
        '''
        
        ##### put all annotated phonemes in queue
        queueAnnotationTokens = Queue.Queue()
        for annoPhoneme in phoenemeAnnotaions:
            if annoPhoneme.ID == '':
                annoPhoneme.ID ='sil'
        # WORKAROUND: needed for phonemes with strange names in Jingju. Uncomment only if need this  code WITH_ORACLE=1
#             self._renamePhonemeNames(annoPhoneme) 
            queueAnnotationTokens.put(annoPhoneme)
        # only first word
#         self.listWords = [self.listWords[0]]
        
        
        # used for debug tracking
        idxTotalPhonemeAnno = 0
        for word_ in self.listWords:
            for syllable in word_.syllables:
#                 listDurations = []
#                 if syllable.text == 'REST':
#                     continue
                for idx, phoneme_ in enumerate(syllable.phonemes): # current syllable
                    
                    idxTotalPhonemeAnno += idx
                    if queueAnnotationTokens.empty():
                        sys.exit("not enough phonemes in annotation at sylable {}".format(syllable.text))
                    phonemeAnno = queueAnnotationTokens.get()
                    logger.debug("phoneme from annotation {} and  phoneme from lyrics {} ".format(phonemeAnno.ID, phoneme_.ID ) )
                    if phonemeAnno.ID != phoneme_.ID:
                        sys.exit( " phoneme idx from annotation {} and  phoneme from lyrics  {} are  different".format( phonemeAnno.ID, phoneme_.ID ))

                    phoneme_.setBeginTs(float(phonemeAnno.beginTs))
                    currDur = self._computeDurationInFrames( phonemeAnno)
                    phoneme_.durationInNumFrames = currDur
        
        
        # expand to states       
        self._phonemes2stateNetwork()
#             self._phonemes2stateNetworkWeights()
        
        self.duratioInFramesSet = True    
        
    
    
    
    
    
    
            
            
     
     
    def _createStateWithDur(self, phoneme,  idxState, distributionType, deviationInSec):
        
        ''' 
        assign durationInMinUnit and name to each state.
        
        NOTE: StateWithDur is not needed when WITH_DURATION = 0, could be replaced by State object for simplicity of code, 
        but StateWithDur with wait prob is superset of State, so it serves the goal
        '''
        
        if distributionType == 'normal':
            currStateWithDur = StateWithDur( phoneme, idxState, distributionType, deviationInSec)
            dur = float(phoneme.durationInNumFrames) / float( phoneme.getNumStates() ) 
            if dur < 0:
                sys.exit("duration for phoneme {}={}. please decrease fixed consonant duration or make sure audio fragment is not too short".format(dur, phoneme.ID))
            currStateWithDur.setDurationInFrames(dur)
        
        elif distributionType == 'exponential':
            currStateWithDur = StateWithDur( phoneme, idxState, distributionType )
            currStateWithDur.setDurationInFrames( MAX_SILENCE_DURATION  * NUM_FRAMES_PERSECOND)
            
            
            ############# set wait prob
            if phoneme.isModelTypeHTK:
                transMatrix = phoneme.getTransMatrix()
                waitProb = transMatrix[idxState + 1, idxState + 1]
            else:
                waitProb = ParametersAlgo.GLOBAL_WAIT_PROB
            currStateWithDur.setWaitProb(waitProb)
        
        
        return currStateWithDur 
    

        
        
     
    def _computeDurationInFrames(self, phonemeAnno):
        '''
        compute Duration from annotation token 
        '''
        durationInSec = float(phonemeAnno.endTs) - float(phonemeAnno.beginTs)
        durationInFrames = math.floor(durationInSec * NUM_FRAMES_PERSECOND)
        return durationInFrames
            
    
    def stateDurationInFrames2List(self):
        '''
        get Duration list for states ( in NumFrames)
        '''
        numFramesDurationsList = []
        
        if not self.duratioInFramesSet:
            logger.warn("no durationInMinUnit in frames set. Please call first duration2numFrameDuration()")
            return numFramesDurationsList
        
        
        for  i, stateWithDur_ in enumerate (self.statesNetwork):
            numFramesDurationsList.append(stateWithDur_.getDurationInFrames()) 
        
        return numFramesDurationsList
    
        
        
    def phonemeDurationsInFrames2List(self):
        '''
        get Duration list for phonemes (in NumFrames)
        '''
        
        listDurations = []
        totalDur = 0
        for phoneme_ in self.phonemesNetwork:
            
            # print phoneme
            
            # get total dur of phoneme's states
            phonemeDurInFrames = 0
            countPhonemeFirstState= phoneme_.numFirstState
            
            for nextState in range(phoneme_.getNumStates()):
                        stateWithDur = self.statesNetwork[countPhonemeFirstState + nextState]
                        try:
                            phonemeDurInFrames += stateWithDur.durationInFrames
                        except AttributeError:
                            print "no durationInFrames Attribute for stateWithDur"
            
            
            listDurations.append(phonemeDurInFrames)
            totalDur += phonemeDurInFrames
        return listDurations
        
    def stateDurations2Network(self):
        '''
        make list with phoonemes and states (with so many repetition as durations)
        '''
        
        stateNetworkWithDurs = []
        if not self.duratioInFramesSet:
            logger.warn("no durationInMinUnit in frames set. Please call first duration2numFrameDuration()")
            return stateNetworkWithDurs
        
        
        for  i, stateWithDur_ in enumerate (self.statesNetwork):
            
            durInFrames = stateWithDur_.getDurationInFrames()
            for j in range(int(durInFrames)):
                 stateNetworkWithDurs.append(stateWithDur_)
        
        return stateNetworkWithDurs
     
        
    def printStates(self):
        '''
        debug: print states 
        '''
        
        
        for i, state_ in enumerate(self.statesNetwork):
                print "{} : {}".format(i, state_.display())



def getTempo(recordingMBID):
    '''
    from Sertans algo
    '''
    
    import json
    URItempi = os.path.join(  os.path.dirname(os.path.realpath(__file__)) + '/tempi/', recordingMBID + ".json")
    with  open(URItempi) as tempoFileHandle:
        tempoData = json.load(tempoFileHandle)
        data = tempoData['scoreInformed']
        beatUnit = int(data['average']['BeatUnit']['value'])
        avrgBpm = float(data['average']['Value'])
#         relativeCoeff = float(data['relative']['Value'])
               
    # TODO: read from score
    from Syllable import MINIMAL_DURATION_UNIT
    bps = avrgBpm/60.0
    timeMinUnit = beatUnit / (bps * MINIMAL_DURATION_UNIT) 
    numFramesPerMinUnit = NUM_FRAMES_PERSECOND * timeMinUnit
    return numFramesPerMinUnit

if __name__=="__main__":
#     numFramesPerMinUnit = getTempo('1701ceba-bd5a-477e-b883-5dacac67da43')
    numFramesPerMinUnit = getTempo('9c26ff74-8541-4282-8a6e-5ba9aa5cc8a1')

    
    print numFramesPerMinUnit
        