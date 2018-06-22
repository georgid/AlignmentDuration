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
Created on Apr 5, 2016

@author: joro
'''

from scipy.stats import norm
from numpy.core.function_base import linspace
import numpy

class OnsetSmoothingFunction(object):
    '''
    Smooths/distributes the probability to gradually decay with increasing distance from onset (or event in generally), 
     uses half lobe of normal distribution
      
    '''


    def __init__(self, ONSET_SIGMA_IN_FRAMES):
        '''
        Constructor
        ONSET_SIGMA_IN_FRAMES: 
            the distance to onset, unit: number of frames, zero means at an onset frame
        '''
        
        minVal = norm.ppf(0.01)
        maxVal= norm.ppf(0.5)
    
        quantileVals  = linspace(maxVal, minVal, ONSET_SIGMA_IN_FRAMES + 1 )
        self.liks = numpy.zeros((ONSET_SIGMA_IN_FRAMES + 1,1)) 
        
        for onsetDist in range(ONSET_SIGMA_IN_FRAMES + 1):
            self.liks[onsetDist] = norm.pdf(quantileVals[onsetDist])
    
    def calcOnsetWeight(self, onsetDist):
        '''
        according to noraml distribution
        '''
#         g = 1.0/(onsetDist + 1)
    
        
        return self.liks[onsetDist]
    
if __name__ == '__main__':
    
    osf = OnsetSmoothingFunction(7)
    for i in range(8):    
        print osf.calcOnsetWeight(i)