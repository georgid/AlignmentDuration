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
from Utilz import loadTextFile


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
        
