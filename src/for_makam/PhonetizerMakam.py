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

    phonetizer class used to do the expansion of the graphemes in a syllable to phonemes
    For all entities of lyrics the g2p rules are the same, so Phonetizer.lookupTable should be instantiated only once on highest level  
@author: joro
'''
import sys
from src.align.Phonetizer import Phonetizer




      
def combineDiacriticsChars( listA, utfCode):
    '''
    if there are diaresis expressed as two chars in utf, combines them together
       @param - listA - list with letters of a word
       @return listWithCombined  
    '''
    diaresisIndeces = []
    for i, j in enumerate(listA): 
        if j == utfCode:
           diaresisIndeces.append(i)
    
    # transform diaresis
    for indexL in diaresisIndeces:
        diaresisLetter = listA.pop(indexL - 1)
        newLetter = diaresisLetter + utfCode
        listA.insert(indexL - 1, newLetter)

    # remove diaresis    
    counter = 0
    for indexL in diaresisIndeces:
         indexL = indexL - counter;  listA.pop(indexL); counter = counter + 1
    return  listA



        
    
       

#     @staticmethod
def grapheme2phonemeList(grapheme, phonemesList):
        '''
        map a grapheme to a list of phonemes. used in JingJu 
        '''
        if grapheme in Phonetizer.lookupTable:
            currPhoneme = Phonetizer.lookupTable[grapheme]
            if currPhoneme != "":
                if isinstance(currPhoneme, list):
                    phonemesList.extend(currPhoneme)
                else:
                    phonemesList.append(currPhoneme)
        else:
            sys.exit("grapheme {0} not in graheme-to-phoneme lookup table".format(grapheme))
        return phonemesList
    
#     @staticmethod
def grapheme2Phoneme(word):
        '''
        grapheme2phoneme for a whole word
        '''
        
    #     wprd = word.lower()
        s = list(word)
    
        #@@@ combine two-char diacritics: 
        # TODO: not optimal has too loop in word for each diacritic type 
        
        # turkish diaeresis
        s = combineDiacriticsChars(s, u'\u0308')
         
        # telugu macron
        s = combineDiacriticsChars(s, u'\u0304')
         
        # telugu acute
        s = combineDiacriticsChars(s, u'\u0301') 
         
        # telugu dot below
        s = combineDiacriticsChars(s, u'\u0323')                      
         
        # telugu dot above
        s = combineDiacriticsChars(s, u'\u0307')                      
     
    
        phonemesList = []

        for i in range(len(s)):
            s[i] = s[i].lower()
            phonemesList = grapheme2phonemeList(s[i], phonemesList)
        
                
        return phonemesList



if __name__=="__main__":
#      Phonetizer.initLookupTable(True, 'grapheme2METUphonemeLookupTableSYNTH' )
    Phonetizer.initLookupTable(False, 'phonemeMandarin2METUphonemeLookupTable' )
    print Phonetizer.lookupTable
    