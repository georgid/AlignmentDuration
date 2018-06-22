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
Created on Mar 21, 2016

@author: joro
'''
from hmm.Path import Path
from docutils.parsers.rst.directives import path
from align.LyricsParsing import getBoundaryFrames


def getBoundaryFramesTest():
    
    path = Path(None, None, 'dummy', 'dummy')
    path.setPathRaw([0,0,1,1,1,3,3,5])
    path.path2stateIndices()
    countFirstState = 3
    countLastState = 4
    currWordBeginFrame, currWordEndFrame  = getBoundaryFrames(countFirstState, countLastState, path)
    
    # shoudl be 5 and 7
    print currWordBeginFrame
    print currWordEndFrame

if __name__ == '__main__':
    getBoundaryFramesTest()