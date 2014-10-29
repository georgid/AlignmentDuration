'''
Created on Oct 27, 2014

@author: joro
'''
from Phoneme import Phoneme

NUMSTATES_SIL = 3

class Lyrics(object):
    '''
    Lyrics data structures
    appends sil at start and end of sequence
    '''


    def __init__(self, listWords):
        '''
        Word[]
        '''
        self.listWords = listWords
        
        '''
        Phoneme []
        '''
        self.phonemesNetwork =  []
        
        self._words2Phonemes()
    
    def _words2Phonemes(self):
        ''' list of words (Word []) to list of phonemes (Phoneme [])
        '''
      
        phonemeSil = Phoneme("sil"); phonemeSil.setDuration('1')
        self.phonemesNetwork.append(phonemeSil)
        
        # start word after sil phoneme
#         currNumPhoneme = 1
        
        for word_ in self.listWords:
            for syllable_ in word_.syllables:
                syllable_.expandToPhonemes()
                self.phonemesNetwork.extend(syllable_.getPhonemes() )
            
#             word_.setNumFirstPhoneme(currNumPhoneme)
            # update index
#             currNumPhoneme += word_.getNumPhonemes()
        
        phonemeSil2 = Phoneme("sil"); phonemeSil2.setDuration('1')
        self.phonemesNetwork.append(phonemeSil2)

    def printSyllables(self):
        '''
        debug: print syllables 
        '''
        
        
        for word_ in self.listWords:
                for syll in word_.syllables:
                    print syll
                    
    def printPhonemeNetwork(self):
        '''
        debug:  
        '''
               
        for i, phoneme in enumerate(self.phonemesNetwork):
            print "{} : {}".format(i, phoneme.ID)
                 

        
        