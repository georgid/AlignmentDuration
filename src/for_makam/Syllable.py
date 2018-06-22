# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/



'''
Created on Oct 8, 2014

@author: joro
'''
from PhonemeMakam import PhonemeMakam
import sys
from src.align.Decoder import logger
from src.align._SyllableBase import _SyllableBase
from PhonetizerMakam import grapheme2Phoneme
from src.align.Phonetizer import Phonetizer

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
            if self.text == '_SAZ_' or '_SAZ_' in self.text:
                # TODO: replace with other models_makam instead of silence
                self.phonemes.append(PhonemeMakam('sil'))
            
            # text from lyrics
            else:
                phonemeIDs = grapheme2Phoneme(self.text)
                
                for phonemeID in phonemeIDs:
                    self.phonemes.append(PhonemeMakam(phonemeID))
            
                if self.hasShortPauseAtEnd:
                    self.phonemes.append(PhonemeMakam('sp'))
            
        
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
