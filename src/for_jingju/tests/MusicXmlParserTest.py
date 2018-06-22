
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

from MusicXmlParser import MusicXMLParser
import os
import sys

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)


from Phonetizer import Phonetizer


if __name__=='__main__':
    
    aria = 'dan-xipi_02' 
    aria = 'laosheng-xipi_02'
    aria = 'laosheng-erhuang_04'
    
    URI = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/' 
      
    MusicXmlURI = URI + aria + '_score.xml'
    lyricsTextGrid =  URI + aria + '.TextGrid'
    
#     MusicXmlURI = 'dan-xipi_01_score.xml'
#     lyricsTextGrid = 'dan-xipi_01.TextGrid'
    

    musicXMLParser = MusicXMLParser(MusicXmlURI, lyricsTextGrid)
    
    Phonetizer.initLookupTable(True,  'phonemeMandarin2METUphonemeLookupTableSYNTH')

    for i in range(len(musicXMLParser.listSentences)):
        print i, " ",  musicXMLParser.getLyricsForSection(i)
    
#     for syll in musicXMLParser.listSyllables:
#         print syll    
