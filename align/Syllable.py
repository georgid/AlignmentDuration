'''
Created on Oct 8, 2014

@author: joro
'''
from Phoneme import Phoneme
import sys
from Phonetizer import Phonetizer
from Decoder import logger
from _SyllableBase import _SyllableBase

#     64 for 64th note
MINIMAL_DURATION_UNIT = 64

NUMFRAMESPESECOND = 100

#  consonant durationInMinUnit fixed 
CONSONANT_DURATION = NUMFRAMESPESECOND * 0.05
# CONSONANT_DURATION = MINIMAL_DURATION_UNIT / 64


class Syllable(_SyllableBase):
        ''' syllables class done because in symbolic file lyrics are represented as syllables
        BUT not meant to be used alone, instead Syllable is a part of a Word class
        '''
        def __init__(self, text, noteNum):
            _SyllableBase.__init__(self, text, noteNum)
           
            

        def expandToPhonemes(self):
            '''
            make sure text has no whitespaces
            '''
            
#             METUtext = PhonetizerOlder.turkishScriptWord2METUScriptWord(self.text)
#             phonemeIDs = PhonetizerOlder.grapheme2Phoneme(METUtext)
#           
            if not Phonetizer.lookupTable:
                sys.exit("Phonetizer.lookupTable not defined. do Phonetizer.initlookupTable at beginning of all code")   
            
            self.phonemes = []
            
            # instrument
            if self.text == '_SAZ_':
                # TODO: replace with other model instead of silence
                self.phonemes.append(Phoneme('sil'))
                # TODO: does sp at end of sp make sence? 
                self.phonemes.append(Phoneme('sp'))
            
            # text from lyrics
            else:
                phonemeIDs = Phonetizer.grapheme2Phoneme(self.text)
                
                for phonemeID in phonemeIDs:
                    self.phonemes.append(Phoneme(phonemeID))
            
                if self.hasShortPauseAtEnd:
                    self.phonemes.append(Phoneme('sp'))
            
        
        def calcPhonemeDurations(self):
            '''
            consonant handling policy
            all consonant durations set to 1 unit, the rest for the vowel.
            
                        '''
            ##############
            # prepare syllable : eg. find where is vowel and so on
            #####################
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
            
            # sanity check: 
            # Workaraound: reduce consonant durationInMinUnit for syllables with very short note value. 
            #copy to local var
            consonant_duration = CONSONANT_DURATION
            while (self.getNumPhonemes() - 1) * consonant_duration >= self.durationInNumFrames:
                logger.warn("Syllable {} has very short durationInMinUnit: {} . reducing the fixed durationInMinUnit of consonants".format(self.text, self.durationInMinUnit) )
                consonant_duration /=2
            
            #################
            ## assign durations 
            #############
            # if no vowel in syllable - equal division. just in case
            if vowelPos == -1:
                for phoneme in self.phonemes:
    #                     no vowel => equal durationInFrames for all
                    phoneme.durationInNumFrames = (self.durationInNumFrames / self.getNumPhonemes())
            else: # one vowel
                for phoneme in self.phonemes:
                       phoneme.durationInNumFrames = consonant_duration
                vowelDuration = self.durationInNumFrames - (self.getNumPhonemes() - 1) * consonant_duration
    
                self.phonemes[vowelPos].setDurationInNumFrames(vowelDuration)   