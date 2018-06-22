# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/


'''
Created on Oct 6, 2015

@author: joro
'''

from lyricsParser import _findBeginEndIndices, stripPunctuationSigns,\
    divideIntoSentencesFromAnnoWithSil_andCreateLyrics, \
    splitDuplicateSyllablePhonemes
from lyricsParser import logger
import os
import sys
from collections import deque
from PhonetizerDict import loadXSAMPAPhonetizers, toXSAMPAPhonemes,\
    createDictSyll2XSAMPA, tokenizePhonemes
import logging

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)

from parse.TextGrid_Parsing import readNonEmptyTokensTextGrid, TextGrid2WordList, tierAliases


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 



from PhonemeJingju import PhonemeJingju


def validatePhonemesWholeAria(lyricsTextGrid):
    '''
    validates if annotated phonemes are corresponmding to automatically expanded from dict
    '''
    print "working on " + lyricsTextGrid + " ..."
    listSentences = divideIntoSentencesFromAnnoWithSil_andCreateLyrics(lyricsTextGrid, False) #uses TextGrid annotation to derive structure. 
    dictSyll2XSAMPA = createDictSyll2XSAMPA()
    
    for whichSentence, currSentence in  enumerate(listSentences):
#         if whichSentence <3: continue
        
        
        for i, syllableIdx in enumerate(range(currSentence.fromSyllableIdx, currSentence.toSyllableIdx+1)):
             
            validatePhonemesOneSyll(lyricsTextGrid, syllableIdx, dictSyll2XSAMPA, currSentence.listWords[i].syllables[0])






def parsePhonemes(lyricsTextGrid, syllableIdx):
    '''
    parse phonemes for given syllable
    '''
    highLevel = tierAliases.pinyin # read syllable in pinyin
    syllable, dummy = readNonEmptyTokensTextGrid(lyricsTextGrid, highLevel, syllableIdx, syllableIdx)

    
    lowLevel = tierAliases.xsampadetails # read phonemesAnno
    phonemesAnnoList, phonemesAnnoListNoPauses = readNonEmptyTokensTextGrid(lyricsTextGrid, lowLevel, 0, -1)
    
    beginSyllableTs = syllable[0][0]
    endSyllableTs = syllable[0][1]
    syllablePinYinRaw = syllable[0][2].strip()
    isEndOfSentence, syllableText = stripPunctuationSigns(syllablePinYinRaw)
    
#     if syllableText == '': # skip this syllable with no lyrics 
#         return phonemesAnnoList, -1, -1, syllableText 
    
    phonemesPointer = 0
    
    fromPhonemeIdx, toPhonemeIdx, dummy, dummy = _findBeginEndIndices(phonemesAnnoList, phonemesPointer, beginSyllableTs, endSyllableTs, highLevel)
    
    return phonemesAnnoList, fromPhonemeIdx, toPhonemeIdx, syllableText, phonemesAnnoListNoPauses



def mergeDuplicatePhonemes(phonemesList):
    '''
    
    input in tier details : x x x o o u -> 
    output: x o u (with corresponding timestamps at begining and end) 
    '''
    ################### find index where a new phoneme appears
    indicesStateStarts = deque([]) # indices of change of phoneme text
    
    currPhonemeTxt = '?'
    for i, phoneme in enumerate(phonemesList):
        
        if phoneme.ID == '?' or phoneme.ID == '':   continue # ? are not new phonemes
        
        if not currPhonemeTxt == phoneme.ID:
            if  phoneme.ID.startswith(currPhonemeTxt)  : #  part of the phoneme repeats -> e.g. 'i' followed by 'in' 
                if len(indicesStateStarts) != 0:
                    indicesStateStarts.pop() # keep 'in' and forget 'i'
            indicesStateStarts.append(i)
            currPhonemeTxt = phoneme.ID
#             if not currPhonemeTxt.endswith(phoneme.ID) : # new phoneme
    
    ################## get only unique phonemes from indices
    phonemesAnno = [] #  output: list of phonemesAnno read
    for i in range(len(indicesStateStarts) - 1):
        idx = indicesStateStarts[i]
        idxLast = indicesStateStarts[i + 1] - 1
        
        
        currPhn = phonemesList[idx]
        currPhn.setEndTs(phonemesList[idxLast].endTs) # merge ts
       
        phonemesAnno.append(currPhn)
    
    ######## add last phoneme
    lastTokenIdx = indicesStateStarts[-1]
    
    lastPhn = phonemesList[lastTokenIdx] 
    lastPhn.setEndTs(phonemesList[-1].endTs) # merge ts
    
    phonemesAnno.append(lastPhn)
    
    return phonemesAnno


def hasDuplicatedSyllables(phonemesAnno, phonemesDictSAMPA):
    
    '''
    x o x o -> x o
    '''
    phonemesAnnoStr = ''        
    for phoneme in phonemesAnno:
        phonemesAnnoStr += phoneme.ID
        
    phonemesDictSAMPAString = ''.join(phonemesDictSAMPA)
    phonemesDictSAMPAString += phonemesDictSAMPAString # concatenate twice string
    
    isDuplicated = 0
    if phonemesAnnoStr == phonemesDictSAMPAString:
        isDuplicated = 1
    return  isDuplicated






def loadPhonemesAnnoOneSyll(lyricsTextGrid, syllableIdx, syllable):
    '''
     For one syllable, load list of phonemes from annotation TextGrid, 
     1. merge duplicate  phonemes
     2.  split double-phoneme groups   
     '''
    
    phonemesAnnoList, fromPhonemeIdx, toPhonemeIdx, syllableText, phonemesAnnoListNoPauses = parsePhonemes(lyricsTextGrid, syllableIdx)
    
    if syllableText == '': # skip empty syllables
         
        phoenemeSil = PhonemeJingju('sil')
        phoenemeSil.setBeginTs(phonemesAnnoList[fromPhonemeIdx][0])
        phoenemeSil.setEndTs(phonemesAnnoList[fromPhonemeIdx][1])
        phonemesAnno = [phoenemeSil]
        return phonemesAnno,syllableText
    
    # 1. details tier has same phoneme or phoneme group duplicated
    phonemeTokensAnno =  phonemesAnnoList[fromPhonemeIdx: toPhonemeIdx+1]
    phonemesAnno = phonemeTokens2Classes( phonemeTokensAnno) 
    
    # run twice to handle special cases
    phonemesAnno = mergeDuplicatePhonemes(phonemesAnno)
    phonemesAnno = mergeDuplicatePhonemes(phonemesAnno)

    
    
    # 2. duplicate phoneme sequences, hack: take first repetition only
    # split 2 phonemes from annotaion
    # TODO: for 2 phonemes

    phonemesAnno = splitDuplicateSyllablePhonemes(phonemesAnno, syllable.phonemes, syllableIdx)
   
  
    return phonemesAnno, syllableText
    
    


def phonemeTokens2Classes( phonemeTokensAnno):
    phonemesAnnoList = []
    for phonemeAnno in phonemeTokensAnno:
        currPhn = PhonemeJingju(phonemeAnno[2].strip())
        currPhn.setBeginTs(phonemeAnno[0])
        currPhn.setEndTs(phonemeAnno[1])
        phonemesAnnoList.append(currPhn)
    
    return phonemesAnnoList



def validatePhonemesOneSyll(lyricsTextGrid, syllableIdx, dictSyll2XSAMPA, syllable):
   
    phonemesDictSAMPAQueue, phonemesDictSAMPA = text2Phonemes(dictSyll2XSAMPA, syllable.text)
    
    phonemesAnno, syllableText = loadPhonemesAnnoOneSyll(lyricsTextGrid, syllableIdx, syllable)
    

    
    if syllableText == '': # nothing to validate. empty syll
        return
    
    
    ### CHECK if phonemes from annotation correspond to dictionary:
    
      #check phoneme identities
    phonemesAnnoStr = "".join(map(str,phonemesAnno))
    phonemesDictSAMPAQueueStr = "".join(phonemesDictSAMPAQueue)
    if phonemesAnnoStr != phonemesDictSAMPAQueueStr:
            logger.info("At  syllable {}. Phonemes in annotaion are {} and they shoud be {}".format(syllableText, phonemesAnno, phonemesDictSAMPAQueue))

    
#     if len(phonemesAnno) > len(phonemesDictSAMPAQueue):
#         if hasDuplicatedSyllables(phonemesAnno, phonemesDictSAMPA):
#             logger.debug(" syllables in annotaion  {} is duplicated".format(phonemesAnno, phonemesDictSAMPAQueue))
#         else:
#             logger.info(" More phonemes annotated for syllable {}. Phonemes in annotaion are {} and they shoud be {}".format(syllableText, phonemesAnno, phonemesDictSAMPAQueue))
#           
#         
#                 
#     else: 
#         if len(phonemesAnno) < len(phonemesDictSAMPAQueue):
# #         logger.warning(" Less phonemes annotated")
# #          syllables in annotaion are {} and they shoud be {}".format(phonemesAnno, phonemesDictSAMPAQueue))
# 
#         
#             for currPhoneme in phonemesAnno:
#                 dictPhoneme = phonemesDictSAMPAQueue.popleft()
#                 
#                 if not currPhoneme.ID == dictPhoneme:
#                     # divide into two
#                     logger.info("in annotation says {} but expected {} from dict".format(currPhoneme.ID, dictPhoneme)) # todo: put the two new back in queue
#     #                 pass
#                   
#             # missing phoneme
#             while not len(phonemesDictSAMPAQueue) == 0:
#                 phoneme = phonemesDictSAMPAQueue.popleft()
#                 logger.info( "in annotation phoneme {} is missing".format(phoneme))
#         
#       

def text2Phonemes(dictSyll2XSAMPA, syllableText):
    '''
    load list of phonemes from annotation TextGrid, sieve out duplicate  phonemes 
    return queue 
    '''
  
    
    if syllableText in dictSyll2XSAMPA:
        phonemesDictSAMPA = dictSyll2XSAMPA[syllableText]
    else:
        logger.warning(" syllable  {} not in dict".format(syllableText))
        consonants, consonants2, vocals, specials = loadXSAMPAPhonetizers()
        phonemesDictSAMPA = toXSAMPAPhonemes(syllableText, consonants, consonants2, vocals, specials)
        dictSyll2XSAMPA[syllableText] = phonemesDictSAMPA # add syllable to dict
    
    phonemesDictSAMPAQueue = tokenizePhonemes(phonemesDictSAMPA)
    
    return  phonemesDictSAMPAQueue, phonemesDictSAMPA
