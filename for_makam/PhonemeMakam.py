'''
Created on Oct 8, 2014

@author: joro
'''
import sys
import numpy
from align.ParametersAlgo import ParametersAlgo
from align._PhonemeBase import PhonemeBase
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
        
    
    

        