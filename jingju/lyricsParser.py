# -*- coding: utf-8 -*-
'''
Created on Mar 5, 2015
collection of metods for parsing textGrid and lyrics
Lyrics are parsed from textGrid

@author: joro
'''

import sys
import os
import json

import logging
from collections import deque


from PhonetizerDict import createDictSyll2XSAMPA
from LyricsJingju import LyricsJingju
from align.ScoreSection import LyricsSection
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

# pathUtils = os.path.join(parentDir, 'utilsLyrics')
# if pathUtils not in sys.path:
#     sys.path.append(pathUtils)

from utilsLyrics.Utilz import writeListToTextFile


pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)

from parse.TextGrid_Parsing import readNonEmptyTokensTextGrid, TextGrid2WordList

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)

from PhonemeJingju import PhonemeJingju
from align.Phonetizer import Phonetizer

from SyllableJingju import SyllableJingju

    
from parse.TextGrid_Parsing import tierAliases


    
            







def splitDuplicateSyllablePhonemes(phonemesAnno, phonemesDictSAMPA, syllableIdx):
    phonemesMerged = []

    # make queue from phoneme anno
    phonemesAnnoQueue = deque(phonemesAnno)
    phonemesDictSAMPAQueue = deque(phonemesDictSAMPA)
    
    while len(phonemesDictSAMPAQueue) != 0:
        
            dictPhoneme = phonemesDictSAMPAQueue.popleft()
            
            if len(phonemesAnnoQueue) == 0:
                logger.error("no phoenemes in annotation while there are more in dict")
                break
            currPhoneme = phonemesAnnoQueue.popleft()
            
            if not currPhoneme.ID == dictPhoneme.ID:
                 logger.debug("in annotation says {} but expected {} from dict".format(currPhoneme.ID, dictPhoneme.ID)) # todo: put the two new back in queue
                 
                 # split
                 splitPhoneme1, splitPhoneme2 = splitThePhoneme(currPhoneme, dictPhoneme, syllableIdx)
                 phonemesAnnoQueue.appendleft(splitPhoneme2)
                 phonemesAnnoQueue.appendleft(splitPhoneme1)
                 phonemesDictSAMPAQueue.appendleft(dictPhoneme)
            
            else: phonemesMerged.append(currPhoneme)
                
                 
    return phonemesMerged


def splitThePhoneme(doublePhoneme, firstPhoeneme, syllableIdx):
    '''
    split double-phone groups from annotation into its parts: first and second phoneme
    use rules: consonant gets ParametersAlgo.CONSONANT_DURATION_IN_SEC and the rest to vowels
    '''
    firstPhoenemeTxt = firstPhoeneme.ID
    idx = doublePhoneme.ID.find(firstPhoenemeTxt) # find substring
    secondPhonemeTxt = doublePhoneme.ID[idx + len(firstPhoenemeTxt):]

    splitPhoneme1 = PhonemeJingju(firstPhoenemeTxt)
    splitPhoneme2 = PhonemeJingju(secondPhonemeTxt)
    
    from ParametersAlgo import ParametersAlgo
    
    splitPhoneme1.setBeginTs(doublePhoneme.beginTs)
    if not splitPhoneme1.isVowel(): # first is consonant
        if not splitPhoneme2.isVowel():
            print "in syllable {}: two consecutive consonants {} and {} in annotation. Not implemented ".format(syllableIdx, splitPhoneme1, splitPhoneme2)
        durationPhoneme1 = ParametersAlgo.CONSONANT_DURATION_IN_SEC
    elif not splitPhoneme2.isVowel(): # second is consonant
        durationPhoneme1 = max(doublePhoneme.endTs - doublePhoneme.beginTs - ParametersAlgo.CONSONANT_DURATION_IN_SEC, (doublePhoneme.endTs - doublePhoneme.beginTs) / 2 )
    else: # both vowels
        durationPhoneme1 = (doublePhoneme.endTs-doublePhoneme.beginTs) /2
    ts = doublePhoneme.beginTs +  durationPhoneme1
    splitPhoneme1.setEndTs(ts)
    
    splitPhoneme2.setBeginTs(ts)
    splitPhoneme2.setEndTs(doublePhoneme.endTs)
    
    return splitPhoneme1, splitPhoneme2
    

def divideIntoSentencesFromAnnoWithSil(annotationURI, syllRefDurations):
    '''
    infer section/line timestamps from annotation-textgrid, 
    parse divison into sentences from Tier 'lines' and load its syllables corresponding by timestamps 
    '''
    
    highLevel = tierAliases.line # read lines (sentences) tier
    dummy, annotationLinesListNoPauses =  readNonEmptyTokensTextGrid(annotationURI, highLevel, 0, -1)
    
    lowLevel = tierAliases.pinyin # read syllables in pinyin 
    syllablesList, dummy =  readNonEmptyTokensTextGrid(annotationURI, lowLevel, 0, -1)
    
    

    
    syllablePointer = 0
    
    lyricsSections = []
    
    for currSentence in annotationLinesListNoPauses:
        
        currSentenceBeginTs = currSentence[0]
        currSentenceEndTs = currSentence[1]

        fromSyllableIdx, toSyllableIdx, syllablePointer, currSectionSyllables = \
         _findBeginEndIndices(syllablesList, syllablePointer, currSentenceBeginTs, currSentenceEndTs, highLevel )
        
        banshiType = 'none'
        lyrics = LyricsJingju( currSectionSyllables, banshiType, syllRefDurations )
        
        currLyricsSection = LyricsSection(annotationURI, fromSyllableIdx, toSyllableIdx)
        currLyricsSection.setLyrics(lyrics)
        lyricsSections.append(currLyricsSection)
      
    
    
     
    return lyricsSections, annotationLinesListNoPauses



def createSyllable(currSentenceSyllables, syllableText, duration=1):
    isEndOfSentence, syllableTxt = stripPunctuationSigns(syllableText)
    if syllableTxt == '':
        syllableTxt = 'REST'
    currSyllable = SyllableJingju(syllableTxt, -1)
    currSyllable.setDurationInMinUnit(duration)
    
    currSentenceSyllables.append(currSyllable)
    return currSentenceSyllables



def _findBeginEndIndices(lowLevelTokensList, lowerLevelTokenPointer, highLevelBeginTs, highLevelEndTs, highLevel):
    ''' 
    find indices of lower level tier whihc align with indices of highLevel tier
    @return: fromLowLevelTokenIdx, toLowLevelTokenIdx
    @param lowerLevelTokenPointer: being updated, and returned 
    '''
    currSentenceSyllablesLIst = []
    
    
    while lowLevelTokensList[lowerLevelTokenPointer][0] < highLevelBeginTs: # search for beginning
        lowerLevelTokenPointer += 1
    
    currTokenBegin = lowLevelTokensList[lowerLevelTokenPointer][0]
    if not currTokenBegin == highLevelBeginTs: # start Ts has to be aligned
        logger.warning("token of lower layer has starting time {}, but expected {} from higher layer ".format(currTokenBegin, highLevelBeginTs))
    fromLowLevelTokenIdx = lowerLevelTokenPointer
    while lowerLevelTokenPointer < len(lowLevelTokensList) and float(lowLevelTokensList[lowerLevelTokenPointer][1]) <= highLevelEndTs: # syllables in currSentence
        
        if highLevel == tierAliases.line:
            syllableText = lowLevelTokensList[lowerLevelTokenPointer][2]
            createSyllable(currSentenceSyllablesLIst, syllableText)
        
        lowerLevelTokenPointer += 1
    
    currTokenEnd = lowLevelTokensList[lowerLevelTokenPointer - 1][1]
    if not currTokenEnd == highLevelEndTs: # end Ts has to be aligned
        logger.warning(" token of lower layer has ending time {}, but expected {} from higher layer ".format(currTokenEnd, highLevelEndTs))
    toLowLevelTokenIdx = lowerLevelTokenPointer - 1
    return  fromLowLevelTokenIdx, toLowLevelTokenIdx, lowerLevelTokenPointer, currSentenceSyllablesLIst



  
def stripPunctuationSigns(string_):
    isEndOfSentence = False
    if string_.endswith(u'\u3002') or string_.endswith(u'\uff0c') \
             or string_.endswith('？') or string_.endswith('！') or string_.endswith('：') \
             or string_.endswith(':') or string_.endswith(',') : # syllable at end of line/section
                string_  = string_.replace(u'\u3002', '') # comma 
                string_  = string_.replace(',','')
                string_  = string_.replace(u'\uff0c', '') # point
                string_  = string_.replace('？', '')
                string_  = string_.replace('！', '')
                string_  = string_.replace('：', '')
                string_  = string_.replace(':', '')
                                
                isEndOfSentence = True
    string_ = string_.strip()
    return isEndOfSentence, string_

def serializeLyrics(lyrics, outputFileNoExt):
    '''
    @deprecated
    '''
    writeListToTextFile(lyrics.phonemesNetwork, None,  outputFileNoExt + '.phn')
    
    listDurations = []  
    for phoneme_ in lyrics.phonemesNetwork :
        listDurations.append(phoneme_.duration)
    writeListToTextFile(listDurations, None, outputFileNoExt + '.dur')
    
    
#     lyrics.printSyllables()
    lyrics.printPhonemeNetwork()

     
if __name__ == '__main__':
    rootURI = '/Users/joro/Documents/Phd/UPF/arias/'
    listSectionLinks = divideIntoSentencesFromAnnoOld(rootURI + 'laosheng-erhuang_04.TextGrid')
#     for section in listSectionLinks:
#         print section[0],  section[1], section[2], section[3]
#         for syll in section[4]:
#             print syll.text
        
        
    
#     serializeLyrics(lyrics, rootURI + 'laosheng-erhuang_04')

