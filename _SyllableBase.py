'''
Created on Mar 5, 2015

@author: joro
'''
'''
Created on Oct 8, 2014

@author: joro
'''
from Phoneme import Phoneme
import sys
from Phonetizer import Phonetizer
from Decoder import logger

#     64 for 64th note
MINIMAL_DURATION_UNIT = 64

#  consonant duration fixed to  32-th note 
CONSONANT_DURATION = MINIMAL_DURATION_UNIT / 32

class _SyllableBase():
        ''' syllables class done because in symbolic file lyrics are represented as syllables
        BUT not meant to be used alone, instead Syllable is a part of a Word class
        '''
        def __init__(self, text, noteNum):
            self.text = text
            
#             corresponding note num
            self.noteNum = int(noteNum)
            self.phonemes = None
            self.duration = None
            self.hasShortPauseAtEnd = False
            
        def setHasShortPauseAtEnd (self,hasShortPauseAtEnd): 
            '''
            set if this is last syllable in word
            '''
            self.hasShortPauseAtEnd = hasShortPauseAtEnd
        def setDuration(self, duration):
            self.duration = duration
        
        def expandToPhonemes(self):
            '''
            make sure text has no whitespaces
            '''
            
            raise NotImplementedError("in class SyllableBase. expoandToPhoenemes not implemented")
           
            
        def getPhonemes(self):
            return self.phonemes
        
        def getNumPhonemes(self):
            if self.phonemes == None:
                self.expandToPhonemes()
            return len(self.phonemes)
        
        def getPositionVowel(self):
            '''
            which is the vowel phoneme. 
            check vowels in lookup table
            NOTE: assume only one vowel in syllable. this is true if no diphtongs in language 
            '''
            if self.getNumPhonemes() == 0:
                return -1
            for i, phoneme in enumerate(self.phonemes):
                if phoneme.isVowel():
                    return i
            return -1
        
        def calcPhonemeDurations(self):
            '''
            consonant handling policy
            all consonant durations set to 1 unit, the rest for the vowel.
            
            '''
            if self.phonemes is None:
                self.expandToPhonemes()
            
            if self.getNumPhonemes() == 0:
                logger.warn("syllable with no phonemes!")
                return
            
            # vowel pos.    
            if self.phonemes[0].ID == 'sil':
                vowelPos = 0
            else:    
                vowelPos = self.getPositionVowel()
            
            # sanity check: Workaraound: reduce consonant duration for syllables with very short note value. 
            #copy to local var
            consonant_duration = CONSONANT_DURATION
            while (self.getNumPhonemes() - 1) * consonant_duration >= self.duration:
                logger.warn("Syllable {} has very short duration: {} . reducing the fixed duration of consonants".format(self.text, self.duration) )
                consonant_duration /=2
            
            # if no vowel in syllable - equal division. just in case
            if vowelPos == -1:
                for phoneme in self.phonemes:
#                     no vowel => equal duration for all
                    phoneme.duration = (self.duration / self.getNumPhonemes())
            else: # one vowel
                for phoneme in self.phonemes:
                       phoneme.duration = consonant_duration
                vowelDuration = self.duration - (self.getNumPhonemes() - 1) * consonant_duration

                self.phonemes[vowelPos].setDurationInMinUnit(vowelDuration)
                
        def __str__(self):
                syllalbeTest = self.text.encode('utf-8','replace')
                return syllalbeTest + " duration: " + str(self.duration) + "\n" 
