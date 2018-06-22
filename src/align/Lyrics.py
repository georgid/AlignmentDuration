# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration
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
Created on Oct 27, 2014

@author: joro
'''
import sys
import os


class Lyrics(object):
    '''
    Lyrics data structures
    represents lyrics for one structural section as list of words
    appends sil at start and end of sequence

    '''


    def __init__(self, listWords):
        '''
        Word[]
        '''
        self.listWords = listWords
        '''
        Phoneme [] : list of phonemes
        '''
        self.phonemesNetwork =  []
        
        self._graphemes2Phonemes()
        
    
    def _graphemes2Phonemes(self):
        ''' convert list of words (Word []) to 
        @return: self.phonemesNetwork: 
        '''
      
        ### loop through all words to combine phonemes network
        for word_ in self.listWords:
            word_.expandToPhonemes()
            for syllable_ in word_.syllables:
                phonemesInSyll = syllable_.getPhonemes()
                phonemesInSyll[-1].setIsLastInSyll(True)
                
                self.phonemesNetwork.extend(phonemesInSyll )
            
#             word_.setNumFirstPhoneme(currNumPhoneme)
            # update index
#             currNumPhoneme += word_.getNumPhonemes()
        

    
    def calcPhonemeDurs(self):
        '''
        distribute duraitions among phonemes within each syllable
        '''
        for word_ in self.listWords:
            for syllable in word_.syllables:
                syllable.calcPhonemeDurations()
    
         
    
    def printSyllables(self):
        '''
        debug: print syllables 
        '''
        for word_ in self.listWords:
                for syllable_    in word_.syllables:
                    print syllable_
                    for phoneme_ in syllable_.phonemes:
                        print "\t phoneme: " , phoneme_
                    
                    
    def getTotalDuration(self):
        '''
        total durationInMinUnit of phonemes according to score. no pauses considered.
        '''
        totalDuration = 0.0    
        if len(self.listWords) == 0:
            sys.exit("no words in lyrics set. No total duration can be get")    
        for word_ in self.listWords:
            for syllable_ in word_.syllables:
                totalDuration +=  syllable_.durationInMinUnit
        return totalDuration
            
    
    def printPhonemeNetwork(self):
        '''
        debug: score-derived phoneme  durationInMinUnit 
        '''
               
        for i, phoneme in enumerate(self.phonemesNetwork):
            print "{}: {} {}".format(i, phoneme.__str__(), phoneme.durationInMinUnit)
#                         print "{}".format(phoneme.ID)

                 
    def __str__(self):
        lyricsStr = ''
        for word_ in self.listWords:
            lyricsStr += word_.__str__()
            lyricsStr += ' '
        return lyricsStr.rstrip().encode('utf-8','replace')
    
    
    def getLenNoRests(self):
        lenWords = 0
        for word_ in self.listWords:
            if word_.syllables[0].text != 'REST':
                lenWords += 1
        return lenWords  
       
        
    def printDict(self, pathToOutputFile, isMLFfile):
        '''
        used in htk 
        print mlf file and dit file with same function 
        '''
        
        
        outputFileHandle = open(pathToOutputFile, 'w')
        
        if isMLFfile:
            outputFileHandle.write  ("#!MLF!#\n")
            pathToOutputFileBase = os.path.basename(pathToOutputFile)
            
            nameAndExt = os.path.splitext(pathToOutputFileBase)
            outputFileHandle.write  ("\"*/")
            outputFileHandle.write  (nameAndExt[0])
            outputFileHandle.write  (".lab\"")
        
    
    
    
        for word_ in self.listWords:
                for syllable_    in word_.syllables:
                    outputFileHandle.write("\n" + syllable_.text + "\t ")
                    
                    # add phonemes on right side as well 
                    if not isMLFfile:
                        for phoneme_ in syllable_.phonemes:
                            outputFileHandle.write( phoneme_.model.modelName + " ")               
        outputFileHandle.close()
        print " written file "  + pathToOutputFile