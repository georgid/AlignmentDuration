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
Created on Nov 5, 2015

@author: joro
'''
import os
import sys
from utilsLyrics.Utilz import readLookupTable

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)



from collections import deque


def createDictSyll2XSAMPA():
        '''
        create table pinyin Syllables -> phonemes in XSAMPA 
        '''
        
        ##### load pinyin syllables
        currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )
        
        # use only list of pinyin syllables, does not use their phonemes (they are in MandarinIPA)
        pinyinSyllDict = readLookupTable(os.path.join(currDir, 'syl2phn46.txt'))

        ###### load mappings for consonants, vowels, specials
        consonants, consonants2, vocals, specials = loadXSAMPAPhonetizers()
        
        mapDict = {}
        
        ###### look up loaded phoneme syllables
        for pinyinSyll in pinyinSyllDict:
            
            xSampaPhonemes = toXSAMPAPhonemes( pinyinSyll, consonants, consonants2, vocals, specials)
            mapDict[pinyinSyll] = xSampaPhonemes       
                    
        return mapDict
    
    
def toXSAMPAPhonemes( pinyinSyll, consonants, consonants2, vocals, specials):
    xSampaPhonemes = []
    if pinyinSyll in specials:
        xSampaPhonemes = specials[pinyinSyll]
        return xSampaPhonemes # specials are whole syllable, so we are done
    
    # init
    foundConsonant = 0
    pinyinSyllRest = pinyinSyll
    
    for consonant in consonants2: # initial is consonant of two chars
        if pinyinSyll.startswith(consonant):
            pinyinSyllRest = pinyinSyll[len(consonant):]
            xSampaPhonemes.append(consonants2[consonant])
            foundConsonant = 1 
            break # cannot start with other consonant
    
    if not foundConsonant: # initial is consonant of one char
        for consonant in consonants:
            if pinyinSyll.startswith(consonant):
                pinyinSyllRest = pinyinSyll[len(consonant):]
                xSampaPhonemes.append(consonants[consonant])
                break # cannot start with other consonant
    
    for vocal in vocals:
        if pinyinSyllRest == vocal:
            xSampaPhonemes.append(vocals[vocal])
            break # cannot end with other vocal
    
    return xSampaPhonemes


  

def loadXSAMPAPhonetizers():
    '''
    
    '''
    currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )

    consonants = readLookupTable(os.path.join(currDir, 'syl2phoneme.consonants.txt'))
    consonants2 = readLookupTable(os.path.join(currDir, 'syl2phoneme.consonants2.txt'))
    vocals = readLookupTable(os.path.join(currDir, 'syl2phoneme.vowels.txt'))
    specials = readLookupTable(os.path.join(currDir, 'syl2phoneme.specials.txt'))
    return consonants, consonants2, vocals, specials



def tokenizePhonemes(phonemesSAMPA):
    '''
    convert string phoneme representation of a syllable to a python list
    phonemes has initial and rest parts
    '''
    
    phonemesSAMPAQueue = deque([])

    #initial part
    if len(phonemesSAMPA) == 2:
        
        phonemesSAMPAQueue.append(phonemesSAMPA[0])
        phonemesSAMPARest = phonemesSAMPA[1]
    else:
        phonemesSAMPARest = phonemesSAMPA
    
    # tokenize
    charsSAMPA = list(phonemesSAMPARest)
    
    for char in charsSAMPA:
        if char == '^' or char == '"' or char=='\\' or char=="'":
            charsSAMPALast = phonemesSAMPAQueue.pop()
            charsSAMPALast += char
            phonemesSAMPAQueue.append(charsSAMPALast)
        
        else:
            phonemesSAMPAQueue.append(char)
    
#     if last == ''
    return phonemesSAMPAQueue

