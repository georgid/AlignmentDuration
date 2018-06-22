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
Created on Jan 13, 2015

@author: joro
'''
import unittest
import Phonetizer
import os
import sys

# parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 
# pathUtils = os.path.join(parentDir, 'utilsLyrics')
#  
# if not pathUtils in sys.path:
#     sys.path.append(pathUtils )
from utilsLyrics.Utilz import loadTextFile


class Tests(unittest.TestCase):
    
    def testReadTable(self):
        lookupTable = Phonetizer.readLookupTable('syl2phn46.txt')
        for pinyinSyll in lookupTable:
            pass
#             print pinyinSyll
        
        mapDict = createTable()
        print mapDict['jiu']
        
        self.assertEquals(2, 2, 'blah')
    
def createTable():
        '''
        create table pinyin Syllables -> phonemes XSAMPA 
        '''
        
        # load pinyin lyllables
        pinyinSyllDict = Phonetizer.readLookupTable('syl2phn46.txt')

        # load mappings for consonants, vowels, specials
        consonants = Phonetizer.readLookupTable('/Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/syl2phoneme.consonants.txt')
        vocals = Phonetizer.readLookupTable('/Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/syl2phoneme.vowels.txt')
        specials = Phonetizer.readLookupTable('/Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/syl2phoneme.specials.txt')
        
        mapDict = {}
        
        for pinyinSyll in pinyinSyllDict:
            
            xSampaPhonemes = []
            if pinyinSyll in specials:
               xSampaPhonemes = specials[pinyinSyll] 
               mapDict[pinyinSyll] = xSampaPhonemes
               continue # specials are whole syllable, so we are done
            
            for consonant in consonants:  # initial is consonant
                if pinyinSyll.startswith(consonant):
                    xSampaPhonemes.append(consonants[consonant])     
                    break # cannot start with other consonant
            
            for vocal in vocals:
                if pinyinSyll.endswith(vocal):
                    xSampaPhonemes.append(vocals[vocal])
                    break # cannot end with other vocal
                
            mapDict[pinyinSyll] = xSampaPhonemes       
                    

        return mapDict
        
