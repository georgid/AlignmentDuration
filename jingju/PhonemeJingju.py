'''
Created on Oct 8, 2014

@author: joro
'''
import sys
import numpy
from utilsLyrics.Utilz import loadTextFile
from align._PhonemeBase import _PhonemeBase

class PhonemeJingju(_PhonemeBase):
   
        

    

      
    
    

    

    
    def isVowel(self):
        vowelListURI = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/models/hmmlistVowels'
        

        vowels = loadTextFile(vowelListURI)
        
        for vowel in vowels:
            vowel = vowel.strip()
            if self.ID == vowel:
                return True 
        return False
    

    

        