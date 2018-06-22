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
Created on Nov 6, 2015

@author: joro
'''
from lyricsParser import splitThePhoneme, splitDuplicateSyllablePhonemes,\
    createSyllable
from PhonemeJingju import PhonemeJingju
from PhonetizerDict import tokenizePhonemes
from SyllableJingju import SyllableJingju


    
def testSplitThePhoneme():
    
    doublePhoneme = PhonemeJingju('En')
    doublePhoneme.setBeginTs(1.4)
    doublePhoneme.setEndTs(3.4)
    
    firstPhoeneme = PhonemeJingju('E')
    ph1 , ph2 = splitThePhoneme(doublePhoneme, firstPhoeneme)
    print ph1.beginTs, ph2.beginTs
    
def testMergeDuplicateSyllablePhonemes():
    phonemesAnno = []
    
    
    
    doublePhoneme = PhonemeJingju('eI^')
    doublePhoneme.setBeginTs(1.4)
    doublePhoneme.setEndTs(1.8)
    phonemesAnno.append(doublePhoneme)
    
    doublePhoneme2 = PhonemeJingju('eI^')
    doublePhoneme2.setBeginTs(2.4)
    doublePhoneme2.setEndTs(2.8)
    phonemesAnno.append(doublePhoneme2)
    
    phonemesDictSAMPA = 'eI^'
    phonemesDictSAMPAQueue = tokenizePhonemes(phonemesDictSAMPA)
    phonemesAnnoSplit = splitDuplicateSyllablePhonemes(phonemesAnno, phonemesDictSAMPAQueue)
    print phonemesAnnoSplit

def testMergeDuplicateSyllablePhonemes3():
    phonemesAnno = []
    
    
    doublePhoneme = PhonemeJingju('j')
    doublePhoneme.setBeginTs(1.4)
    doublePhoneme.setEndTs(1.8)
    phonemesAnno.append(doublePhoneme)
    
    doublePhoneme2 = PhonemeJingju('En')
    doublePhoneme2.setBeginTs(2.4)
    doublePhoneme2.setEndTs(2.8)
    phonemesAnno.append(doublePhoneme2)
    
    syllablesLIst = []
    syllablesLIst = createSyllable(syllablesLIst, 'yan')
    
    lyrics = syllables2Lyrics(syllablesLIst)
    syllable = lyrics.listWords[0].syllables[0]
   
    phonemesAnnoSplit = splitDuplicateSyllablePhonemes(phonemesAnno, syllable.phonemes)
    print phonemesAnnoSplit



def testMergeDuplicateSyllablePhonemes2():
    phonemesAnno = []
    
    
    
    doublePhoneme = PhonemeJingju('@')
    doublePhoneme.setBeginTs(1.4)
    doublePhoneme.setEndTs(1.8)
    phonemesAnno.append(doublePhoneme)
    
    doublePhoneme2 = PhonemeJingju("r\\'")
    doublePhoneme2.setBeginTs(2.4)
    doublePhoneme2.setEndTs(2.8)
    phonemesAnno.append(doublePhoneme2)
    
    doublePhoneme3 = PhonemeJingju('')
    doublePhoneme3.setBeginTs(2.9)
    doublePhoneme3.setEndTs(2.94)
    phonemesAnno.append(doublePhoneme3)
    
    doublePhoneme4 = PhonemeJingju("r\\'")
    doublePhoneme4.setBeginTs(3.1)
    doublePhoneme4.setEndTs(3.9)
    phonemesAnno.append(doublePhoneme4)
    
    syllablesLIst = []
    syllablesLIst = createSyllable(syllablesLIst, 'er')
    
    lyrics = syllables2Lyrics(syllablesLIst)
    syllable = lyrics.listWords[0].syllables[0]
    
    phonemesAnnoSplit = splitDuplicateSyllablePhonemes(phonemesAnno, syllable.phonemes)
    print phonemesAnnoSplit

if __name__ == '__main__':
    testSplitThePhoneme()
#     testMergeDuplicateSyllablePhonemes()
#     testMergeDuplicateSyllablePhonemes3()
#     assignReferenceDurationsTest()