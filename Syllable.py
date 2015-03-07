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

#  consonant duration fixed to  32-th note 
CONSONANT_DURATION = MINIMAL_DURATION_UNIT / 32

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
                self.phonemes.append(Phoneme('sil'))
                # TODO: does sp at end of sp make sence? 
                if self.hasShortPauseAtEnd:
                    self.phonemes.append(Phoneme('sp'))
            
            # text from lyrics
            else:
                phonemeIDs = Phonetizer.grapheme2Phoneme(self.text)
                
                for phonemeID in phonemeIDs:
                    self.phonemes.append(Phoneme(phonemeID))
            
                if self.hasShortPauseAtEnd:
                    self.phonemes.append(Phoneme('sp'))
           