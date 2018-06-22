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
Created on May 9, 2016

@author: joro
'''
from align.SectionLink import _SectionLinkBase
from for_jingju.ParsePhonemeAnnotation import loadPhonemesAnnoOneSyll

class SectionLinkJingju(_SectionLinkBase):
    
    def __init__(self, URIWholeRecording, beginTs, endTs, isLastSyllLong, isNonKeySyllLong):
        
        _SectionLinkBase.__init__(self, URIWholeRecording, beginTs, endTs)
        self.isLastSyllLong = isLastSyllLong
        self.isNonKeySyllLong = isNonKeySyllLong
        
    
    
    def loadSmallAudioFragmentOracle(self, htkParser):
        
        lyricsTextGrid = self.section.lyricsTextGrid
        # get start and end phoneme indices from TextGrid
        self.lyricsWithModels = []
        for idx, syllableIdx in enumerate(range(self.section.fromSyllableIdx, self.section.toSyllableIdx+1)): # for each  syllable including silent syllables
            # go through the phonemes. load all 
            currSyllable = self.listWordsFromTextGrid[idx].syllables[0]
            phonemesAnno, syllableTxt = loadPhonemesAnnoOneSyll(lyricsTextGrid, syllableIdx, currSyllable)
            self.lyricsWithModels.extend(phonemesAnno)