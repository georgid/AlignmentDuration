'''
Created on Oct 8, 2014

@author: joro
'''

from Syllable import Syllable
from Phoneme import Phoneme

class Word():
        ''' just a list of syllables. order  matters '''
        def __init__(self,syllables):
            self.syllables = syllables;
        
            wordText = ''
            for syllable in self.syllables:
                wordText = wordText + syllable.text
            self.text = wordText
            
#             # consequtive number of first phoneme from phonemeNetwork in Lyrics context
#             self.numFirstPhoneme = -1
#             
#         def setNumFirstPhoneme(self, numFirstPhoneme):
#             self.numFirstPhoneme = numFirstPhoneme

           
        def __str__(self):
                return self.text.encode('utf-8','replace')
        
        def getNumPhonemes(self):
            numPhonemes = 0
            for syllable in self.syllables:
                 numPhonemes += syllable.getNumPhonemes()
            return numPhonemes
            
            
            