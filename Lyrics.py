'''
Created on Oct 27, 2014

@author: joro
'''
from Phoneme import Phoneme


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
        Phoneme [] : list of phonemes
        '''
        self.phonemesNetwork =  []
        
        self._graphemes2Phonemes()
        
    
    def _graphemes2Phonemes(self):
        ''' convert list of words (Word []) to 
        @return: self.phonemesNetwork: 
        '''
  
        # start word after sil phoneme
#         currNumPhoneme = 1
        
        for word_ in self.listWords:
            for syllable_ in word_.syllables:
                syllable_.expandToPhonemes()
                self.phonemesNetwork.extend(syllable_.getPhonemes() )
            
#             word_.setNumFirstPhoneme(currNumPhoneme)
            # update index
#             currNumPhoneme += word_.getNumPhonemes()
        

    
    def calcPhonemeDurs(self):
        '''
        distribute duraitions among phonemes within each syllable
        '''
        for word_ in self.listWords:
            for syllable in word_.syllables:
                syllable.calcPhonemeDurations()
    
         
    
    def printSyllables(self):
        '''
        debug: print syllables 
        '''
        for word_ in self.listWords:
                for syllable_    in word_.syllables:
                    print syllable_
                    for phoneme_ in syllable_.phonemes:
                        print "\t phoneme: " , phoneme_
                    
                    
    def getTotalDuration(self):
        '''
        total durationInMinUnit of phonemes according to score. no pauses considered.
        '''
        totalDuration = 0    
        for word_ in self.listWords:
            for syllable_ in word_.syllables:
                totalDuration +=  int(syllable_.durationInMinUnit)
        return totalDuration
            
    
    def printPhonemeNetwork(self):
        '''
        debug: score-derived phoneme  durationInMinUnit 
        '''
               
        for i, phoneme in enumerate(self.phonemesNetwork):
            print "{}: {} {}".format(i, phoneme.ID, phoneme.durationInMinUnit)
#                         print "{}".format(phoneme.ID)

                 
    def __str__(self):
        lyricsStr = ''
        for word_ in self.listWords:
            lyricsStr += word_.__str__()
            lyricsStr += ' '
        return lyricsStr.rstrip().encode('utf-8','replace')
        
        