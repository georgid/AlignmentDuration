'''
Created on Oct 8, 2014

@author: joro
'''
import sys
import numpy
from src.utilsLyrics.Utilz import loadTextFile
from src.align._PhonemeBase import PhonemeBase
import os
from src.align.ParametersAlgo import ParametersAlgo

class PhonemeJingju(PhonemeBase):
   
        

    

      
    
    

    

    
    def isVowel(self):
        URI_model_noFolds  = os.path.join(ParametersAlgo.MODELS_DIR, os.pardir)
        vowelListURI = URI_model_noFolds + '/hmmlistVowels'


        vowels = loadTextFile(vowelListURI)
        
        for vowel in vowels:
            vowel = vowel.strip()
            if self.ID == vowel:
                return True 
        return False
    

    

        