# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling
# and is modified from https://github.com/guyz/HMM

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
Created on May 22, 2015

@author: joro
'''
import numpy

def areArraysEqual(B_map, B_mapSciKit):
    print "abs diff"
    arr = abs(B_map  - B_mapSciKit)
    print numpy.max(abs(B_map  - B_mapSciKit))
    
    # print vallues of top 10 most different values 

    indices = arr.ravel().argsort()[-10:]
    indices = (numpy.unravel_index(i, arr.shape) for i in indices)
    print [(B_map[i], B_mapSciKit[i], i) for i in indices]
    
    # compare with assertion exception
    try:
        res = numpy.testing.assert_array_almost_equal_nulp(B_map, B_mapSciKit, 10)
        
    except Exception:
        print res