'''
Created on Oct 27, 2014

@author: joro
'''
from Lyrics import Lyrics
import os
import sys
from Phoneme import Phoneme

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
HMMDurationPath = os.path.join(parentDir, 'HMMDuration')
if not HMMDurationPath in sys.path:
    sys.path.append(HMMDurationPath)
    
from hmm.StateWithDur import StateWithDur

from htk_converter import HtkConverter
from Decoder import logger
from Constants import NUM_FRAMES_PERSECOND, AVRG_TIME_SIL, MAX_TIME_SIL


# htkModelParser = os.path.join(parentDir, 'htk2s3')
# sys.path.append(htkModelParser)



class LyricsWithModels(Lyrics):
    '''
    lyrics with each Phoneme having a link to a model of class type htkModel from htkModelParser
    No handling of durationInMinUnit information. For it see Decoder.Decoder.decodeAudio 
    '''


    def __init__(self, lyrics, htkParser, ONLY_MIDDLE_STATE  ):
        '''
        being  linked to models, allows expansion to network of states 
        '''
        
#       add a state 'sp' with exponential disrib at begining and end  
        self.withPaddedSilence = True
        
        Lyrics.__init__(self, lyrics.listWords)
        self._linkToModels(htkParser)
        
        # list of class type StateWithDur
        self.statesNetwork = []
        
        if ONLY_MIDDLE_STATE=='True':
            ONLY_MIDDLE_STATE  = True
        elif ONLY_MIDDLE_STATE=='False':
            ONLY_MIDDLE_STATE  = False
        else:
            logger.error('LyricsWithModels: param ONLY_MIDDLE_STATE ={}. ONly True/False expected'.format( ONLY_MIDDLE_STATE))
            sys.exit()
        
        self.ONLY_MIDDLE_STATE = ONLY_MIDDLE_STATE
        


        self.duratioInFramesSet = False

        
    def _linkToModels(self, htkParser):
        '''
        load links to trained models   
        '''
       
    #link each phoneme from transcript to a model
            # FIXME: DO A MORE OPTIMAL WAY like ismember()
        for phonemeFromTranscript in    self.phonemesNetwork:
            for currHmmModel in htkParser.hmms:
                if currHmmModel.name == phonemeFromTranscript.ID:
                    
                    phonemeFromTranscript.setHTKModel(currHmmModel) 
            
        ######## # create sp state
            for currHmmModel in htkParser.hmms:
                if currHmmModel.name == 'sp':
                    spmodel = currHmmModel
            
        (numStateFromHtk, state)  = spmodel.states[0]
        self.spState = StateWithDur(state.mixtures, 'sp', 0, distribType='exponential')

        tmpPhoneme =  Phoneme('sp')
        spTransMatrix = tmpPhoneme.getTransMatrix(spmodel)
        self.spState.setWaitProb(spTransMatrix[1,1])
        ######## end of create sp state   
      
        
           # DEBUG: 
#         for phonemeFromTranscript in    self.phonemesNetwork:
#             phonemeFromTranscript.htkModel.display()
    #         (numState, state )  = phonemeFromTranscript.htkModel.states[1]
    #         state.display()
        ###### 
        
    def _phonemes2stateNetwork(self):
        '''
        expand self.phonemeNetwork to self.statesNetwork
        assign phoneme a pointer to its initial state in the state network (serves as link among the two)
        each state gets 1/n-th of total num of states. 
        '''
        
        self.statesNetwork = []
        stateCount = 0
        
        if self.withPaddedSilence:           
            self.statesNetwork.append(self.spState)
            stateCount+=1
        
        for phoneme in self.phonemesNetwork:
            
            phoneme.setNumFirstState(stateCount)
            
            # update state counter
            if not hasattr(phoneme, 'htkModel'):
                sys.exit("phoneme {} has no htkModel assigned".format(phoneme.ID))
            currStateCount = len(phoneme.htkModel.states)
            stateCount += currStateCount
            
            # assign durationInMinUnit and name to each state
            for idxState, (numStateFromHtk, state ) in enumerate( phoneme.htkModel.states):
                currStateWithDur = StateWithDur(state.mixtures, phoneme.__str__(), idxState)
                 
                dur = float(phoneme.durationInNumFrames) / float(currStateCount)
                    
                currStateWithDur.setDurationInFrames( dur )
                self.statesNetwork.append(currStateWithDur)
          
        if self.withPaddedSilence:           
            self.statesNetwork.append(self.spState)      
                 
    def _phonemes2stateNetworkWeights(self):
        '''
        expand to self.statesNetwork. 
        each state gets a part proportional to  the weighting probs.
       @deprecated: 
        '''
        
        self.statesNetwork = []
        stateCount = 0
        
        for phoneme in self.phonemesNetwork:
            
            phoneme.setNumFirstState(stateCount)
            # update
            currStateCount = len(phoneme.htkModel.states)
            stateCount += currStateCount
            
            
            currTransMatrix = phoneme.getTransMatrix()
            currTransMatrix = currTransMatrix[1:-1,1:-1]
            
            # sanity check
            if not currStateCount ==  currTransMatrix.shape[0]:
                sys.exit("Error on reading htk model: transMatrix for phoneme {} has not same num states as states ", phoneme.ID)
            
            waitProbs = []
            for currState in range(currStateCount):
                currWaitProb =  currTransMatrix[currState, currState]
                waitProbs.append(currWaitProb)
            
            statesList = phoneme.htkModel.states
            # assign durations
            for idxState, (numStateFromHtk, state ) in enumerate( phoneme.htkModel.states):
                 currStateWithDur = StateWithDur(state.mixtures, phoneme.__str__(), idxState)
                 
                 # normalize to sum to one
                 weigthState = float(waitProbs[idxState]) / float(sum(waitProbs))
                 dur = float(phoneme.durationInFrames) * float(weigthState)
                 
                 currStateWithDur.setDurationInFrames( dur )
                 self.statesNetwork.append(currStateWithDur)
        
        

                 
               
    def _phonemes2stateNetworkOnlyMiddle(self):
        '''
        expand to self.statesNetwork . TAKE ONLY middle state for now
        '''
        
        self.statesNetwork = []
        stateCount = 0
        
        for phoneme in self.phonemesNetwork:
            
            phoneme.setNumFirstState(stateCount)
            # update
            stateCount += 1
            
        
            if len( phoneme.htkModel.states) == 1:
                idxMiddleState = 0
            elif len( phoneme.htkModel.states) == 3:             
                idxMiddleState = 1
            else:
                sys.exit("not implemented. only 3 or 1 state per phoneme supported")
            
            (numState, state ) = phoneme.htkModel.states[idxMiddleState]
            currStateWithDur = StateWithDur(state.mixtures, phoneme.__str__(), idxMiddleState)
            currStateWithDur.setDurationInFrames(phoneme.getDurationInFrames())
            
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
        setDuration HowManyFrames for each phoneme in phonemesNetwork
        '''
        # TODO: read from score
#         self.bpm = 60
#         durationMinUnit = (1. / (self.bpm/60) ) * (1. / MINIMAL_DURATION_UNIT) 
#         numFramesPerMinUnit = NUM_FRAMES_PERSECOND * durationMinUnit
        totalScoreDur = self.getTotalDuration()
#         numFramesPerMinUnit   = float(len(observationFeatures) - 2 * AVRG_TIME_SIL * NUM_FRAMES_PERSECOND) / float(totalScoreDur)
        numFramesPerMinUnit   = float(tempoCoefficient * len(observationFeatures) ) / float(totalScoreDur)
        logger.debug("numFramesPerMinUnit = {} for audiochunk {} ".format( numFramesPerMinUnit, URI_recording_noExt))
        
        for word_ in self.listWords:
            for syllable_ in word_.syllables:

                numFramesInSyllable = round(float(syllable_.durationInMinUnit) * numFramesPerMinUnit)
                syllable_.setDurationInNumFrames(numFramesInSyllable)
        
        # consonant-handling policy
        self.calcPhonemeDurs()

        
        if self.ONLY_MIDDLE_STATE:
            self._phonemes2stateNetworkOnlyMiddle()
        else:
            self._phonemes2stateNetwork()
#             self._phonemes2stateNetworkWeights()
        
        self.duratioInFramesSet = True
        
            
    
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
