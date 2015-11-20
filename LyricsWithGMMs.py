'''
Created on Nov 18, 2015

@author: joro
'''


from Lyrics import Lyrics
import os
import sys
from Phoneme import Phoneme
from Constants import NUM_FRAMES_PERSECOND
import Queue
import math
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 
HMMDurationPath = os.path.join(parentDir, 'HMMDuration')
if not HMMDurationPath in sys.path:
    sys.path.append(HMMDurationPath)
    
from hmm.StateWithDur import StateWithDur

from htk_converter import HtkConverter
from Decoder import logger

from hmm.Parameters import MAX_SILENCE_DURATION

# htkModelParser = os.path.join(parentDir, 'htk2s3')
# sys.path.append(htkModelParser)

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)
from WordLevelEvaluator import readNonEmptyTokensTextGrid


pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )
from Utilz import loadDictFromTabFile


class LyricsWithGMMs(Lyrics):
    '''
    lyrics with each Phoneme having a link to a model of class type htkModel from htkModelParser
    No handling of durationInMinUnit information. For it see Decoder.Decoder.decodeAudio 
    '''


    def __init__(self, lyrics,  ONLY_MIDDLE_STATE, deviationInSec  ):
        '''
        being  linked to models, allows expansion to network of states 
        '''
        
#       flag to add a state 'sp' with exponential disrib at begining and end  
        self.withPaddedSilence = True
        

        Lyrics.__init__(self, lyrics.listWords)

        
        # list of class type StateWithDur
        self.statesNetwork = []
        
        if ONLY_MIDDLE_STATE=='True':
            ONLY_MIDDLE_STATE  = True
        elif ONLY_MIDDLE_STATE=='False':
            ONLY_MIDDLE_STATE  = False
        else:
            logger.error('LyricsWithHTKModels: param ONLY_MIDDLE_STATE ={}. ONly True/False expected'.format( ONLY_MIDDLE_STATE))
            sys.exit()
        
        self.ONLY_MIDDLE_STATE = ONLY_MIDDLE_STATE
        
        self._linkToModels()

        self.deviationInSec = deviationInSec

        self.duratioInFramesSet = False
    
        
    def loadModel(self, modelName):
        ''' load model'''
        
        thisDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__) ) )
        dictURI =  os.path.join(thisDir, 'model/modelName2FileNameDict') 
        modelName2FileNameDict = loadDictFromTabFile(dictURI)
        
        # table convert model names
        if modelName in modelName2FileNameDict:
            modelName = modelName2FileNameDict[modelName]
        
        modelsURI = '/model/scikitGMMs/' + str(modelName) + '.pkl'
        fileURI =  thisDir +   modelsURI 
        import pickle
        try:
            model = pickle.load(file(fileURI))
        except BaseException:
            logger.error("no model with name {}".format(modelName))
            model = None
        return model
        
        
    def _linkToModels(self):
        '''
        load links to trained models   
        '''
       
             
            #link each phoneme from transcript to a model
            # FIXME: DO A MORE OPTIMAL WAY like ismember()
        for phonemeFromTranscript in    self.phonemesNetwork:
                model = self.loadModel(phonemeFromTranscript.ID)
#                 if model == None:
                    
                phonemeFromTranscript.setGMM(model)
                if self.ONLY_MIDDLE_STATE:
                    phonemeFromTranscript.setNumStates(1)
                else:
                    phonemeFromTranscript.setNumStates(3)
            
    ########### no sp state
                 
               
    def _phonemes2stateNetworkOnlyMiddle(self):
        '''
        expand to self.statesNetwork . TAKE ONLY middle state for now
        @deprecated
        '''
        
        self.statesNetwork = []
        stateCount = 0
        
        for phoneme in self.phonemesNetwork:
            
            phoneme.setNumFirstState(stateCount)
            
            
             # update state counter
            if not hasattr(phoneme, 'gmm'):
                sys.exit("phoneme {} has no gmm assigned".format(phoneme.ID))
            stateCount += 1
            gmm = phoneme.gmm   
            idxMiddleState = 0
            
            currStateWithDur = StateWithDur(None, phoneme.__str__(), idxMiddleState, 'normal' , self.deviationInSec, gmm)
            currStateWithDur.setDurationInFrames(phoneme.durationInNumFrames)
            
            self.statesNetwork.append(currStateWithDur)
    
    
    
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

                numFramesInSyllable = round(float(syllable_.durationInMinUnit) * numFramesPerMinUnit)
                if numFramesInSyllable == 0.0:
                    sys.exit(" frames per syllable {} are 0.0. Check numFramesPerMinUnit={}".format(syllable_.text, numFramesPerMinUnit))
                    
                # TODO: set here syllables from score
                syllable_.setDurationInNumFrames(numFramesInSyllable)
        
        # consonant-handling policy
        self.calcPhonemeDurs()

        if self.ONLY_MIDDLE_STATE:
            self._phonemes2stateNetworkOnlyMiddle()
        else:
            self._phonemes2stateNetwork()
#             self._phonemes2stateNetworkWeights()
        
        self.duratioInFramesSet = True
    

        
    def setPhonemeNumFrameDurs(self,  phoenemeAnnotaions):
        '''
        set durations in num frame durations read directly from textGrid. Used in oracle. 
        does not consider empty tokens (silences) at beginning and end, but reads sp tokens
        double check if phoenemes are the same as in lyrics 
        '''
        
        queueAnnotationTokens = Queue.Queue()
        for annoPhoneme in phoenemeAnnotaions:
            if annoPhoneme.ID == '':
                annoPhoneme.ID ='sil' 
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
                    currDur = self.computeDurationInFrames( phonemeAnno)
                    phoneme_.durationInNumFrames = currDur
        
        
        # expand to states       
        if self.ONLY_MIDDLE_STATE:
            self._phonemes2stateNetworkOnlyMiddle()
        else:
            self._phonemes2stateNetwork()
#             self._phonemes2stateNetworkWeights()
        
        self.duratioInFramesSet = True
        
     
    def computeDurationInFrames(self, phonemeAnno):
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
        