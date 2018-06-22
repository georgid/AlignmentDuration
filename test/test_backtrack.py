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
Created on Feb 16, 2017

@author: joro
'''
import os
import numpy
import sys
import json

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)
from src.align.ParametersAlgo import ParametersAlgo

testDir = os.path.dirname(os.path.realpath(__file__))

from src.hmm.Path import Path



def run_backtrack():
    '''
    helper method: load phi and psi, create a Path object and backtrack
    '''
    absPathPsi = os.path.join(testDir, 'psi_umbrella_line.txt' )
    psiBackPointer = numpy.loadtxt(absPathPsi)

    
    if ParametersAlgo.WITH_DURATIONS: path = None # TODO
    else: path =  Path( psiBackPointer)
    
    return path

def test_BackTrack():  
    
    path = run_backtrack()
#     print "path is {}".format(path.pathRaw)
    
    URI_persistent_path = os.path.join(testDir, 'path_umbrella_line.json')
    
#     with open(URI_persistent_path, 'w') as f:
#         json.dump(path.pathRaw.tolist(), f )
       
#     with open('persistent/state_indices_umbrella_line.json', 'w') as f:
#        json.dump(path.indicesStateStarts, f )

    with open(URI_persistent_path, 'r') as f:
        path_persistent = json.load(f)
    assert path_persistent == path.pathRaw
    


     

if __name__ == '__main__':
    test_BackTrack()
#     test_path_to_tokenlist()
#     test_decode_phonemes()
#     test_get_segment_path()
#     test_calc_phi_indices()