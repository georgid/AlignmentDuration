'''
Created on Oct 8, 2014

@author: joro
'''
from Phonetizer import Phonetizer
from Phoneme import Phoneme
import sys

#     64 for 64th note
MINIMAL_DURATION_UNIT = 64
#  consonant duration fixed to  32-th 
CONSONANT_DURATION = MINIMAL_DURATION_UNIT / 32

class Syllable():
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
            
            METUtext = Phonetizer.turkishScriptWord2METUScriptWord(self.text)
            phonemeIDs = Phonetizer.grapheme2Phoneme(METUtext)
            
            self.phonemes = []
            for phonemeID in phonemeIDs:
                self.phonemes.append(Phoneme(phonemeID))
            if self.hasShortPauseAtEnd:
                self.phonemes.append(Phoneme('sp'))
           
            
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
            for i, phoneme in enumerate(self.phonemes):
                if phoneme.isVowel():
                    return i
            return -1
        
        def calcPhonemeDurations(self):
            '''
            all consonant durations set to 1 unit, the rest for the vowel.
            
            '''
            if self.phonemes is None:
                self.expandToPhonemes()
                
            vowelPos = self.getPositionVowel()
            
            # if no vowel in syllable - equal division. just in case
            if vowelPos == -1:
                for phoneme in self.phonemes:
#                     no vowel => equal duration for all
                    phoneme.setDuration(self.duration / self.getNumPhonemes())
            else: # one vowel
                for phoneme in self.phonemes:
                       phoneme.duration = CONSONANT_DURATION
                vowelDuration = self.duration - (self.getNumPhonemes() - 1) * CONSONANT_DURATION
                # sanity check
                if vowelDuration <= 0:
                    sys.exit("phoneme {} of syllable {} has duration of zero or less units. ".format(phoneme.ID, self.text)  )
                self.phonemes[self.getPositionVowel()].setDuration(vowelDuration)
                
        def __str__(self):
                syllalbeTest = self.text.encode('utf-8','replace')
                return syllalbeTest + " duration: " + str(self.duration) + "\n" 
