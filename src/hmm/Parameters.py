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
Created on Dec 8, 2014

@author: joro
'''

DEVIATION_IN_SEC = 0.1


# max  duration for silence state (with exp distrib.) in seconds.
MAX_SILENCE_DURATION = 1.0

class Parameters(object):
    '''
    classdocs
    '''
    

    def __init__(self, ALPHA,  ONLY_MIDDLE_STATE ):
        '''
        Constructor
        '''
        
        self.ALPHA = ALPHA
        
        self.ONLY_MIDDLE_STATE = ONLY_MIDDLE_STATE
        
        
     
        
        