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
Created on Jan 10, 2016

@author: joro
'''


class LyricsSection():
    '''
    Section from the composition: used only if section read from score. TODO: deprecate.

    '''
    
    def __init__(self, lyricsTextGrid,  fromSyllableIdx, toSyllableIdx  ):
        
        
        # text Grid of complete recording
        self.lyricsTextGrid = lyricsTextGrid
        self.fromSyllableIdx = fromSyllableIdx
        self.toSyllableIdx = toSyllableIdx
        

class ScoreSection():


    def __init__(self, name, startNote, endNote, melodicStructure, lyricStructure ):
        '''
        section from score, has as well musical notes related information
        '''
      
        
        
        self.name = name
        self.startNote = startNote
        self.endNote = endNote
        self.melodicStructure =  melodicStructure
        self.lyricStructure =  lyricStructure
        

        
        
    def __str__(self):
        
        return "{}\n melodic struct: {}\n lyrics struct: {}".format(self.name, self.melodicStructure, self.lyricStructure) 

