'''
Created on Dec 9, 2015

@author: joro
'''
from PhonetizerDict import createDictSyll2XSAMPA

from align.Phonetizer import Phonetizer
from align.Lyrics import Lyrics
import numpy
from align.Word import createWord
import os
import logging
import sys

class LyricsJingju(Lyrics):
    '''
    classdocs
    '''


    def __init__(self, listSyllables,  banshiType, refSyllableDurations=None):
        '''
        '''
        
        listWords = []    
        #### for Oracle    
        self.listWordsFromTextGrid = []
        for syllable in listSyllables:
            # word of only one syllable
            word, dummy = createWord([], syllable)
            if syllable.text != 'REST':
                listWords.append(word)
            self.listWordsFromTextGrid.append(word)
        
        # TODO add syllable rest after each each read syllable
        
        currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )    
        URIlookupTable  = os.path.join(currDir, 'XSAMPA2METUphonemeLookupTableSYNTH')
        Phonetizer.initLookupTable(True, URIlookupTable )

        # load phonetic dict 
#         Phonetizer.initPhoneticDict('syl2phn46.txt')
        Phonetizer.phoneticDict = createDictSyll2XSAMPA() 
        
        
        Lyrics.__init__(self, listWords)
        
        self.assignReferenceDurations(refSyllableDurations)
        
        self.banshiType = banshiType
 
        
    
    def assignReferenceDurations(self, refSyllableDurations):
    
        ####### set durations according rules
    
        if refSyllableDurations == None:
            logging.info('no reference syllable durations given for line with words {} \n Using hard-coded ref. durs '.format(self.listWords) )
            durations = self._computeReferenceDurations()
        elif len(self.listWords) != 10:
                logging.info('no reference durations for lines <10 or >10 syllables. \n Using hard-coded ref. durs '.format(self.listWords) )

                durations = self._computeReferenceDurations()
        else:
            if len(refSyllableDurations) != len(self.listWords):
                sys.exit('given ref durations are {}, but syllables in sentence are {}'.format( len(refSyllableDurations), len(self.listWords) ) )
            durations = refSyllableDurations
        
        ##### set them
        for idx, word in enumerate(self.listWords):
                word.syllables[0].setDurationInMinUnit(durations[idx])
                
                
                

    def _computeReferenceDurations(self):
        '''
        use musicological rules depending on number of syllables
        '''
        
        lenSyllables = len(self.listWords)
        durations = [0 for x in range(lenSyllables)]
        
        #### duration ratio of whole sentence. empirically decided
        THIRD_DOU_DURATION_RATIO = 1 / 3.0
        FIRST_DOU_DURATION_RATIO = 1 / 4.0
        SECOND_DOU_DURATION_RATIO = 1 / 5.0
        
        durations[-1] = THIRD_DOU_DURATION_RATIO
        
        lenSyllablesNoRests = self.getLenNoRests()
        
        if lenSyllablesNoRests >=6:
            if lenSyllablesNoRests <= 8:
                firstDouCount = 2
                secondDouCount = 4
            elif lenSyllablesNoRests >= 9:
                firstDouCount = 3
                secondDouCount = 6
            
            firstDouIdx, secondDouIdx = self._findIndicesFirstAndSecondDou(lenSyllables, firstDouCount, secondDouCount)
                     
            durations[firstDouIdx] = FIRST_DOU_DURATION_RATIO 
            durations[secondDouIdx] = SECOND_DOU_DURATION_RATIO
        
        
        arr = numpy.array(durations)
        lenSyllablesDiffThan0 = len(numpy.where(arr != 0)[0])
        
    # the rest of sylable durations are equal -> assigned durRest
        totalAssignedDurations = sum(durations)
        durRest = 0
        if lenSyllables - lenSyllablesDiffThan0:
            durRest = (1 - totalAssignedDurations) / float(lenSyllables - lenSyllablesDiffThan0)
        for i in range(len(durations)):
            if durations[i] == 0: durations[i] = durRest
            
        durations = numpy.multiply( durations, lenSyllablesNoRests)
        
        return durations
    
    
    def _findIndicesFirstAndSecondDou(self, lenSyllables, firstDouCount, secondDouCount):
        '''
        utility method. have to skip rests in counting syllables 
        '''
        count = 0
        for idx in range(lenSyllables):
            if self.listWords[idx].syllables[0].text != 'REST':
                count += 1
            if count == firstDouCount:
                firstDouIdx = idx 
            if count == secondDouCount:
                secondDouIdx = idx 
        
        return firstDouIdx, secondDouIdx
