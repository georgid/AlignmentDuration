'''
Created on Oct 27, 2014

@author: joro
'''
from Lyrics import Lyrics
import os
import sys
from StateWithDur import StateWithDur
from htk_converter import HtkConverter
from numpy.f2py.crackfortran import word_pattern

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

htkModelParser = os.path.join(parentDir, 'htk2s3')
sys.path.append(htkModelParser)



class LyricsWithModels(Lyrics):
    '''
    lyrics with each Phoneme having a link to a model of class type htkModel from htkModelParser
    '''


    def __init__(self, listWords, MODEL_URI, HMM_LIST_URI ):
        '''
        being  linked to models, allows expansion to network of states 
        '''
        Lyrics.__init__(self, listWords)
        
        self._linkToModels(MODEL_URI, HMM_LIST_URI)
        
        # list of class type StateWithDur
        self.statesNetwork = []
#         self._phonemes2stateNetwork()
        self._phonemes2stateNetworkOnlyMiddle()

        

        
    def _linkToModels(self, MODEL_URI, HMM_LIST_URI):
        '''
        load links to trained models   
        '''
        
        conv_before = HtkConverter()
        conv_before.load(MODEL_URI, HMM_LIST_URI)
        
        # FIXME: DO A MORE OPTIMAL WAY like ismember()
        for phonemeFromTranscript in    self.phonemesNetwork:
            for currHmmModel in conv_before.hmms:
                if currHmmModel.name == phonemeFromTranscript.ID:
                    phonemeFromTranscript.setHTKModel(currHmmModel) 
            
#         for phonemeFromTranscript in    self.phonemesNetwork:
#             phonemeFromTranscript.htkModel.display()
    #         (numState, state )  = phonemeFromTranscript.htkModel.states[1]
    #         state.display()
        ###### 
        
    def _phonemes2stateNetwork(self):
        '''
        expand to states network. 
        '''
        
        self.statesNetwork = []
        stateCount = 0
        
        for phoneme in self.phonemesNetwork:
            
            phoneme.setNumFirstState(stateCount)
            # update
            currStateCount = len(phoneme.htkModel.states)
            stateCount += currStateCount
            
            
            for (numState, state ) in phoneme.htkModel.states:
                 currStateWithDur = StateWithDur(state.mixtures)
                 currStateWithDur.setDuration(phoneme.getDuration()/currStateCount)
                 self.statesNetwork.append(currStateWithDur)
   
    def _phonemes2stateNetworkOnlyMiddle(self):
        '''
        expand to states network. TAKE ONLY middle state for now
        '''
        
        self.statesNetwork = []
        stateCount = 0
        
        for phoneme in self.phonemesNetwork:
            
            phoneme.setNumFirstState(stateCount)
            # update
            stateCount += 1
            
        
            if len( phoneme.htkModel.states) == 1:
                (numState, state ) = phoneme.htkModel.states[0]
            elif len( phoneme.htkModel.states) == 3:             
                (numState, state ) = phoneme.htkModel.states[1]
            else:
                sys.exit("not implemented. only 3 or 1 state per phoneme supported")
            
            currStateWithDur = StateWithDur(state.mixtures)
            currStateWithDur.setDuration(phoneme.getDuration())
            
            self.statesNetwork.append(currStateWithDur)
    
    def printWordsAndStates(self, resultPath):
        '''
        debug word begining states
        '''
        
        for word_ in self.listWords:
            print word_ , ":" 
            for syllable_ in word_.syllables:
                for phoneme_ in syllable_.phonemes:
                    print "\t phoneme: " , phoneme_
                    countPhonemeFirstState =  phoneme_.numFirstState
                    print "\t\t state: {} duration (in Frames): {} DERATION RESULT: {}, t_end: {}".format(countPhonemeFirstState, 
                                                                                                self.statesNetwork[countPhonemeFirstState].durationInFrames,
                                                                                                 resultPath.durations[countPhonemeFirstState], 
                                                                                                 resultPath.endingTimes[countPhonemeFirstState])
            
                
    def printStates(self):
        '''
        debug: print states 
        '''
        
        
        for i, state_ in enumerate(self.statesNetwork):
                print "{} : {}".format(i, state_.display()) 