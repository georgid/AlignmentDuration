'''
Created on May 7, 2016

@author: joro
'''
import sys
from align._LyricsWithModelsBase import _LyricsWithModelsBase
from align.ParametersAlgo import ParametersAlgo
from makam.Phoneme import Phoneme

class LyricsWithModelsHTK(_LyricsWithModelsBase):
    '''
    classdocs
    '''

    
    def _linkToModels(self, htkParser):
        '''
        load links to trained models. 
        add  Phoneme('sp') with exponential distrib at beginning and end if withPaddedSilence 
        '''
       
        if self.withPaddedSilence:    
            tmpPhoneme =  Phoneme('sp');
            tmpPhoneme.setIsLastInSyll(True)
            self.phonemesNetwork.insert(0, tmpPhoneme)
            self.phonemesNetwork.append(tmpPhoneme)
       
       
    #####link each phoneme from transcript to a model
            # FIXME: DO A MORE OPTIMAL WAY like ismember()
        for phonemeFromTranscript in    self.phonemesNetwork:
            for currHmmModel in htkParser.hmms:
                if currHmmModel.name == phonemeFromTranscript.ID:
                    
                    phonemeFromTranscript.setHTKModel(currHmmModel)     
    
    
    
    def _phonemes2stateNetwork(self):
        '''
        expand self.phonemeNetwork to self.statesNetwork
        assign phoneme a pointer <setNumFirstState> to its initial state in the state network (serves as link among the two)
        each state gets 1/n-th of total num of states. 
        '''
         
        
        self.statesNetwork = []
        stateCount = 0
        

        
        for phnIdx, phoneme in enumerate(self.phonemesNetwork):
            
            
            phonemeStates = phoneme.htkModel.states
            
            if ParametersAlgo.ONLY_MIDDLE_STATE:
                if len( phoneme.htkModel.states) == 1:
                    idxMiddleState = 0
                elif len( phoneme.htkModel.states) == 3:             
                    idxMiddleState = 1
                else:
                    sys.exit("not implemented. only 3 or 1 state per phoneme supported")
                phonemeStates = [phoneme.htkModel.states[idxMiddleState]]
            
            phoneme.setNumFirstState(stateCount)
            
            if not hasattr(phoneme, 'htkModel'):
                sys.exit("phoneme {} has no htkModel assigned".format(phoneme.ID))
            
            # update state counter
            currStateCount = len(phonemeStates)
            stateCount += currStateCount
            
            
            distributionType='normal'
            # assign durationInMinUnit and name to each state
            if (phnIdx == 0 or phnIdx == len(self.phonemesNetwork)-1 ) and self.withPaddedSilence:
                distributionType='exponential'
            
            for idxState, (numStateFromHtk, state ) in enumerate(phonemeStates):
                currStateWithDur = self._createStateWithDur(phoneme, currStateCount, idxState, state, distributionType)
                self.statesNetwork.append(currStateWithDur)
          
        