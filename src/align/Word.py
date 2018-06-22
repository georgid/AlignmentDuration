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
    
            
            
            