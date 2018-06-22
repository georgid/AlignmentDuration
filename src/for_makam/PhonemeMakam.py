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
Created on Oct 8, 2014

@author: joro
'''
import sys
import numpy
from src.align.ParametersAlgo import ParametersAlgo
from src.align._PhonemeBase import PhonemeBase
class PhonemeMakam(PhonemeBase):


      
    

    
#     def getStates(self):
#         try: self.htkModel
#         except NameError:
#             sys.exit(" phoneme {} has no models_makam assigned ", self.ID)
#         
#         return self.htkModel.states
        

            
            
    
 
    
    def isVowel(self):
        
        if (self.ID == 'AA' or
        self.ID == 'A' or
        self.ID == 'O' or
        self.ID == 'OE' or
        self.ID == 'E' or
        self.ID == 'IY' or
        self.ID == 'U' or
        self.ID == 'UE' or
        self.ID == 'I'
        ):
            return True
        
        return False
    
    def isVowelOrLiquid(self):
        
        if (self.isVowel() or
        self.ID == 'L' or
        self.ID == 'LL' or
        self.ID == 'N' or
        self.ID == 'NN' or
        self.ID == 'M' or
        self.ID == 'MM' or 
        self.ID == 'Y'):
            return True
        return False 
        
    
    

        