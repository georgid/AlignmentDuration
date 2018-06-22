
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
Created on Apr 27, 2016

@author: joro
'''

### include src folder
import os
import sys
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if parentDir not in sys.path:
    sys.path.append(parentDir)
    
from src.utilsLyrics.Utilz import readLookupTable


class Phonetizer(object):
    lookupTable = dict()
    withSynthesis = 0
    phoneticDict = dict() 
    
    @staticmethod
    def initLookupTable(withSynthesis, URItable):
        # if not yet created:
        if not Phonetizer.lookupTable:
            Phonetizer.lookupTable = readLookupTable(URItable)
            Phonetizer.withSynthesis = withSynthesis
    
    @staticmethod    
    def initPhoneticDict(URLdict):
        # if not yet created:
        if not Phonetizer.phoneticDict:
            Phonetizer.phoneticDict = readLookupTable(URLdict)