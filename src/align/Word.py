'''
Created on Oct 8, 2014

@author: joro
'''
from ParametersAlgo import ParametersAlgo

class Word():
        ''' just a list of syllables. order  matters '''
        def __init__(self, syllables):
            self.syllables = syllables;
        
            wordText = ''
            for syllable in self.syllables:
                wordText = wordText + syllable.text
            self.text = wordText
            
#             # consequtive number of first phoneme from phonemeNetwork in Lyrics context
#             self.numFirstPhoneme = -1
#       
        def expandToPhonemes(self):
            for syllable_ in self.syllables:
                syllable_.expandToPhonemes()
                      
        def setNumFirstPhoneme(self, numFirstPhoneme):
            self.numFirstPhoneme = numFirstPhoneme

           
        def __str__(self):
                return self.text.encode('utf-8','replace')
        
        def __repr__(self):
            return self.text.encode('utf-8','replace')
        
        def getNumPhonemes(self):
            numPhonemes = 0
            for syllable in self.syllables:
                 numPhonemes += syllable.getNumPhonemes()
            return numPhonemes
        
        
        def getDurationForWord(self, statesNetwork):
            '''
            @deprecated
            '''
            
            durationNumFrames = 0
            for syllable_ in self.syllables:
                 for phoneme_ in syllable_:
                     
                     indexFirstSt = phoneme_.numFirstState
                     
                     for whichState in phoneme_.getNumStates():
                         stateDurInFrames = statesNetwork[indexFirstSt  + whichState].getDurationInFrames()
                         durationNumFrames += stateDurInFrames
 
                         

def createWord(syllablesInCurrWord, currSyllable):
        '''
        create a new word ending in currect syllable  
        '''        
        currSyllable.text = currSyllable.text.rstrip()
        currSyllable.setHasShortPauseAtEnd(ParametersAlgo.WITH_SHORT_PAUSES)
        syllablesInCurrWord.append(currSyllable)
    # create new word
        word = Word(syllablesInCurrWord)
        return word, syllablesInCurrWord
    
            
            
            