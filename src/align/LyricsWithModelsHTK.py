'''
Created on May 7, 2016

@author: joro
'''
from _LyricsWithModelsBase import _LyricsWithModelsBase

class LyricsWithModelsHTK(_LyricsWithModelsBase):
    '''
    classdocs
    '''

    
    def _linkToModels(self, htkParser):
        '''
        load links to trained models. 
        add  Phoneme('sp') with exponential distrib at beginning and end if withPaddedSilence 
        '''
       
        
        _LyricsWithModelsBase._addPaddedSilencePhonemes(self)   
        
        #####link each phoneme from transcript to a models_makam
            # FIXME: DO A MORE OPTIMAL WAY like ismember()
        for phonemeFromTranscript in    self.phonemesNetwork:
            for currHmmModel in htkParser.hmms:
                if currHmmModel.name == phonemeFromTranscript.ID:
                    
                    phonemeFromTranscript.setModel(currHmmModel)     
    
    
    
    

          
        