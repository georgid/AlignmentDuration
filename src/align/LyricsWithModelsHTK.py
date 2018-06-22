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
Created on May 7, 2016

@author: joro
'''
from _LyricsWithModelsBase import _LyricsWithModelsBase

class LyricsWithModelsHTK(_LyricsWithModelsBase):
    '''
    classdocs
    '''

    
    def _linkToModels(self, htkParser):
        '''
        load links to trained models. 
        add  Phoneme('sp') with exponential distrib at beginning and end if withPaddedSilence 
        '''
       
        
        _LyricsWithModelsBase._addPaddedSilencePhonemes(self)   
        
        #####link each phoneme from transcript to a models_makam
            # FIXME: DO A MORE OPTIMAL WAY like ismember()
        for phonemeFromTranscript in    self.phonemesNetwork:
            for currHmmModel in htkParser.hmms:
                if currHmmModel.name == phonemeFromTranscript.ID:
                    
                    phonemeFromTranscript.setModel(currHmmModel)     
    
    
    
    

          
        