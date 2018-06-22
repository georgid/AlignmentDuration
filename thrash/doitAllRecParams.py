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
Created on Dec 5, 2014

@author: joro
'''
from thrash.doitAllRecordings import doit
import logging
import sys
import numpy

def runWithParameters(argv):
    
    if len(argv) != 4 and  len(argv) != 5 :
            print ("usage: {}  <pathToCompositions>  <pathToRecordings> <ONLY_MIDDLE_STATE>  <usePersistentFiles=True>".format(argv[0]) )
            sys.exit();
    
    ALPHAs = numpy.arange(0.91,1.0,0.01)
    
    for ALPHA in ALPHAs:
        logging.info("ALPHA = " + str(ALPHA))
        
        
        usePersistent = 'True'
        if len(argv) == 5:
            usePersistent = argv[4]

        doit([argv[0], argv[1], argv[2], ALPHA,  argv[3], usePersistent ]  )
        
            
            

if __name__ == '__main__':
    runWithParameters(sys.argv)