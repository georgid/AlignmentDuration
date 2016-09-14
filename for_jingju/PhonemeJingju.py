'''
Created on Oct 8, 2014

@author: joro
'''
import sys
import numpy
from utilsLyrics.Utilz import loadTextFile
from align._PhonemeBase import _PhonemeBase
import os
from align.ParametersAlgo import ParametersAlgo

class PhonemeJingju(_PhonemeBase):
   
        

    

      
    
    

    

    
    def isVowel(self):
        URI_model_noFolds  = os.path.join(ParametersAlgo.MODELS_DIR, os.pardir)
        vowelListURI = URI_model_noFolds + '/hmmlistVowels'


        vowels = loadTextFile(vowelListURI)
        
        for vowel in vowels:
            vowel = vowel.strip()
            if self.ID == vowel:
                return True 
        return False
    

    

        