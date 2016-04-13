# -*- coding: utf-8 -*-
'''
Created on Jun 14, 2015

@author: joro
'''
from music21 import *
from SyllableJingju import SyllableJingju
from cjklib.reading import ReadingFactory
from cjklib.characterlookup import CharacterLookup

import logging

from Lyrics import Lyrics
from Word import Word
from lyricsParser import stripPunctuationSigns, \
     createSyllable
from Phonetizer import Phonetizer
import sys
import os.path
from SentenceJingju import SentenceJingju

# 64th of note
MIN_DUR_UNIT = 64

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 


# pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
# if pathEvaluation not in sys.path:
#     sys.path.append(pathEvaluation)


pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)

from parse.TextGrid_Parsing import readNonEmptyTokensTextGrid

class MusicXMLParser(object):
    '''
    infer duration of lyrics from score. 
    loops though all notes and rests sequentially
    a new syllable start, whenever a text is attached to a note (a pause after a note is considered a syllable with no text)
    if no text, add note values to current syllable  
    '''

    
    def __init__(self, MusicXmlURI, lyricsTextGrid):
        '''
        Constructor
        '''
        self.logger = logging.getLogger(__name__)
        self.logger.setLevel(logging.DEBUG)

        self._loadSyllables( MusicXmlURI, lyricsTextGrid)
        
#        lyrics for each sentence/line 
        self.listSentences = []
        self.divideIntoSections()
        
        # list of  section names and their lyrics. 
        self.sectionLyrics = []
    
    
    def _loadSyllables(self, MusicXmlURI, lyricsTextGrid):
        '''
        top=most method
        '''
        self.listSyllables = []
        
        if not os.path.isfile(MusicXmlURI):
            sys.exit("file {} does not exist, please name it so".format(MusicXmlURI))
        score = converter.parse(MusicXmlURI)
        notesAndRests = score.flat.notesAndRests
        currSyllable = None
        currSyllTotalDuration = None
        
        for noteOrRest in notesAndRests:
            currSyllable, currSyllTotalDuration = self.parseCurrTxtToken(currSyllable, currSyllTotalDuration, noteOrRest)
        
        # last syllable
        currSyllable.setDurationInMinUnit(currSyllTotalDuration)
        self.listSyllables.append(currSyllable)
        
        ##### here workaround when not able to  convert  lyrics from score into pinyin  
         
         
#         syllablesAllPinyin = createSyllables(lyricsTextGrid, -1, -1 )
#           
#         counter = 0
#         for syl in self.listSyllables:
#             if syl.text == 'REST':
#                 pass
#             else: 
#                 if counter == len(syllablesAllPinyin): # reached last syllable
#                     sys.exit(" syllable {} is last available from syllablesPinyin".format(syllablesAllPinyin[counter-1].text))
#                 print "mandarin:{} and pinyin: {} ".format(syl.text, syllablesAllPinyin[counter].text)
#                 syl.text = syllablesAllPinyin[counter].text
#                 counter +=1
#         print "len syllables in muicXML= {} and len syllables in TextGrid = {}".format(counter, len(syllablesAllPinyin))

        # end of workaround 
    
    def createSyllables(self, annotationURI, fromSyllable, toSyllable):
        '''
        @param refSyllableDuration: its value does not matter. important is that all syllables are assigned same relative duration.
        
        create Syllables, assign their durations in refSyllableDuration
        
        @return: lyrics - created lyrics oboject
        '''
        listSyllables = []
        
        annotationTokenList, annotationTokenListNoPauses =  readNonEmptyTokensTextGrid(annotationURI, 3, fromSyllable, toSyllable)
        
        # depending on token# change size
        
        for idx, tsAndSyll in enumerate(annotationTokenListNoPauses):
            syllableText = tsAndSyll[2]
            listSyllables = createSyllable(listSyllables, syllableText)
        
        return listSyllables
    
          


    def divideIntoSections(self):
        '''
        same as lyricsParser.divideIntoSections just class variable name self.listSyllable is different
        converts mandarin to pinyin
        divides into sections 
        '''
        
        currSectionLyrics =  []
        for syl in self.listSyllables:
                
                
            isEndOfSentence, syl.text = stripPunctuationSigns(syl.text)
                
                ### convert from mandarin to pinyin
            if not syl.text == 'REST':
                syl.text = mandarinToPinyin(syl.text)
                
            ### finish up sentence when punctuation present        
            if isEndOfSentence:
                
                currSectionLyrics.append(syl)
                self.listSentences.append(currSectionLyrics)
                currSectionLyrics =  []
            else:
                currSectionLyrics.append(syl)

        
    def parseCurrTxtToken(self, currSyllable, syllTotalDuration, noteOrRest):
        '''
        discriminate between cases with or without lyrics and rest and no rest
        '''
        currNoteDuration = noteOrRest.duration.quarterLength * MIN_DUR_UNIT / 4
#         self.logger.debug("currNoteDuration: {}".format(currNoteDuration))
#         print "currNoteDuration: {}".format(currNoteDuration)
        if noteOrRest.isRest:
            if not (currSyllable is None) and not (syllTotalDuration is None):
                if currSyllable.text == 'REST':
                    if not (currSyllable is None) and not (syllTotalDuration is None):
                        syllTotalDuration = syllTotalDuration + currNoteDuration
                else:
                    textPinYin = 'REST'
                    currSyllable, syllTotalDuration = self.finishCurrentAndCreateNewSyllable(textPinYin, currSyllable, syllTotalDuration, currNoteDuration)

                
        # '' (no lyrics at note) so still at same syllable
        elif noteOrRest.isNote:
            if (not noteOrRest.hasLyrics()) or (noteOrRest.hasLyrics() and noteOrRest.lyrics[0].text.strip().startswith('（') or noteOrRest.lyrics[0].text.strip()==''): # has no lyrics token. '(' is ignored
                if not (currSyllable is None) and not (syllTotalDuration is None):
                    syllTotalDuration = syllTotalDuration + currNoteDuration
        
            else: # has lyrics => has end of curr syllable
                lyrics = noteOrRest.lyrics
                if len(lyrics) > 1: # sanity check
                    self.logger.warn("syllable {} has {} characters".format(lyrics, len(lyrics)))
                # convert to pinyin: maybe use this instead: https://pypi.python.org/pypi/pinyin/0.2.5
                if len(lyrics) != 0: # skip lyrics of len 0
                    
                    mandarinText = lyrics[0].text

                    currSyllable, syllTotalDuration = self.finishCurrentAndCreateNewSyllable(mandarinText, currSyllable, syllTotalDuration, currNoteDuration)
        
        return currSyllable, syllTotalDuration


    def finishCurrentAndCreateNewSyllable(self, textSyllable, currSyllable, syllTotalDuration, noteValue):
        if not (currSyllable is None) and not (syllTotalDuration is None): # save last syllable and duration
            currSyllable.setDurationInMinUnit(syllTotalDuration)
            self.listSyllables.append(currSyllable)
        
         # init next syllable and its duration
        dummyNote = -1
        currSyllable = SyllableJingju(textSyllable, dummyNote)
        syllTotalDuration = noteValue
        return currSyllable, syllTotalDuration
    
    
    def getLyricsForSection(self, whichSection):
        syllables = self.listSentences[whichSection]
        
        currSentence = SentenceJingju(syllables,  -1, -1, -1, -1, 'noneBanshi', False)

        return currSentence



        


def createWord(syllablesInCurrWord, currSyllable):
        '''
        create a new word ending in currect syllable  
        '''        
        currSyllable.text = currSyllable.text.rstrip()
        currSyllable.setHasShortPauseAtEnd(True)
        syllablesInCurrWord.append(currSyllable)
    # create new word
        word = Word(syllablesInCurrWord)
        return word, syllablesInCurrWord   
    
    

def mandarinToPinyin(mandarinChar):
        cjk = CharacterLookup('C')
        textPinYinList = cjk.getReadingForCharacter(mandarinChar, 'Pinyin', toneMarkType='none')
        if len(textPinYinList) > 1:
            print "converted syllable {} has {} parts".format(textPinYinList, len(textPinYinList)) 
        pinyin = textPinYinList[0] # take only first variant of pinyin interpretations
        return pinyin