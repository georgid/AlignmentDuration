# -*- coding: utf-8 -*-

'''
Created on Dec 16, 2014
Utility class: logic for parsing statesNetwork, phoeneNetwork  
@author: joro
'''
import sys
from Constants import NUM_FRAMES_PERSECOND, NUMSTATES_SIL, NUMSTATES_PHONEME
from makam.Phoneme import Phoneme
import os
import logging
from parse.TextGrid_Parsing import tierAliases, readNonEmptyTokensTextGrid
from hmm.ParametersAlgo import ParametersAlgo
from onsets.OnsetDetector import frameNumberToTs



parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)
    


def loadOraclePhonemes(URIrecordingTextGrid, fromSyllableIdx, toSyllableIdx):
    '''
    LOAD ORACLE PHONEMES as annotatetd in TextGrid
    '''
    highLevel = tierAliases.pinyin # read syllable in pinyin
    if ParametersAlgo.WITH_SHORT_PAUSES:
        lowLevel = tierAliases.xsampadetails_with_sp
    else:
        lowLevel = tierAliases.xsampadetails # read phonemesAnno
    
    phonemesAnnoAll = []
    for syllableIdx in range(fromSyllableIdx, toSyllableIdx): # for each  syllable including non-lyrics (.e.g. _SAZ_) syllables
    # go through the phonemes. load all
        phonemesAnnoList, fromPhonemeIdx, toPhonemeIdx, syllableText, phonemesAnnoListNoPauses = parsePhonemes(URIrecordingTextGrid, syllableIdx, highLevel, lowLevel)
        phonemeTokensAnno = phonemesAnnoList[fromPhonemeIdx:toPhonemeIdx + 1]
        phonemesAnno = phonemeTokens2Classes(phonemeTokensAnno)
        phonemesAnnoAll.extend(phonemesAnno)
    
    return phonemesAnnoAll


def getOnsetsFromPhonemeAnnos(URIRecordingChunkResynthesizedNoExt):
    '''
    use oracle phonemes as if they were onsets, Deprecated
    '''
    onsetTimestamps = []
    highLevel = tierAliases.pinyin # read syllable in pinyin
    lowLevel = tierAliases.xsampadetails # read phonemesAnno
# go through the phonemes. load all
    phonemesAnnoList, fromPhonemeIdx, toPhonemeIdx, syllableText, phonemesAnnoListNoPauses = parsePhonemes(URIRecordingChunkResynthesizedNoExt + '.TextGrid', 0, highLevel, lowLevel)
    for phoneme in phonemesAnnoList:
        onsetTimestamps.append(phoneme[0])
    
    return onsetTimestamps


def expandlyrics2WordList (lyricsWithModels, path, totalDuration, func):
    '''
    expand @path to words and corresponding timestamps
    @param path stands for path or statesNetwork
    '''

    wordList = []


       
    for word_ in lyricsWithModels.listWords:
        countFirstState = word_.syllables[0].phonemes[0].numFirstState
        
        # word ends at first state of sp phonemene (assume it is sp)
        lastSyll = word_.syllables[-1]
        lastPhoneme = word_.syllables[-1].phonemes[-1]
        
        countLastState = getCountLastState(lyricsWithModels, word_, lastSyll, lastPhoneme)

        startNoteNumber = word_.syllables[0].noteNum

        currWord, totalDuration = func( word_, startNoteNumber, countFirstState, countLastState, path, totalDuration)

        wordList.append( currWord)
    return wordList


def getCountLastState(lyricsWithModels, word_, lastSyll, lastPhoneme):
    '''
    helper function
    '''
    if lastSyll.hasShortPauseAtEnd:
        if lastPhoneme.ID != 'sp':  # sanity check that last syllable is sp
            sys.exit(' \n last state for word {} is not sp. Sorry - not implemented.'.format(word_.text))
        countLastState = lastPhoneme.numFirstState
    else:
        countLastState_ = lastPhoneme.numFirstState + lastPhoneme.getNumStates()
        countLastState = min(countLastState_, len(lyricsWithModels.statesNetwork) - 1) # make sure not outside of state network
        
    return countLastState



def expandlyrics2SyllableList (lyricsWithModels, path, totalDuration, func):
    '''
    expand @path to words and corresponding timestamps
    @param path stands for path or statesNetwork
    '''

    syllableList = []


       
    for word_ in lyricsWithModels.listWords:
        
        lastSyll = word_.syllables[-1]
        
        for syllable_ in word_.syllables:
            
            countFirstState = syllable_.phonemes[0].numFirstState
            lastPhoneme = syllable_.phonemes[-1]
            countLastState = lastPhoneme.numFirstState + lastPhoneme.getNumStates()
            
            if syllable_ == lastSyll:
                countLastState = getCountLastState(lyricsWithModels, word_, lastSyll, lastPhoneme)
            
            currSyllAndTs, totalDuration = func( syllable_.text, syllable_.noteNum, countFirstState, countLastState, path, totalDuration)
       
            syllableList.append( currSyllAndTs)
        
        
            
    return syllableList


    
    
def _constructTimeStampsForToken(  text, startNoteNumber, countFirstState, countLastState, statesNetwork, totalDuration):
        '''
        helper method. timestamps for word/syllable based on durations read from score 
        '''
        
        currWordBeginFrame = totalDuration
        for currState in range(countFirstState, countLastState + 1):                 
            totalDuration += statesNetwork[currState].getDurationInFrames()
        currWordEndFrame = totalDuration
        
            
    # timestamp:
        
        
        startTs = float(currWordBeginFrame) / NUM_FRAMES_PERSECOND
        endTs = float(currWordEndFrame) / NUM_FRAMES_PERSECOND
        
        detectedWord = [startTs, endTs, text , startNoteNumber]
#         print detectedWord
        
        return detectedWord, totalDuration 






def _constructTimeStampsForTokenDetected(  text, startNoteNumber, countFirstState, countLastState, path, dummy):
        '''
        helper method. timestamps of detected word/syllable , read frames from path
        '''
        currWordBeginFrame, currWordEndFrame = getBoundaryFrames(countFirstState, countLastState, path)    
        
    #             # debug:
    #             print self.pathRaw[currWordBeginFrame]
    # timestamp:

        startTs = frameNumberToTs(currWordBeginFrame)
        endTs = frameNumberToTs(currWordEndFrame)
        detectedWord = [startTs, endTs, text, startNoteNumber]
#         print detectedWord
        
        return detectedWord, dummy


def getBoundaryFrames(countFirstState, countLastState, path):
    i = 0
    while countFirstState > path.pathRaw[path.indicesStateStarts[i]]:
        i += 1
    
    currWordBeginFrame = path.indicesStateStarts[i]
    while i < len(path.indicesStateStarts) and countLastState > path.pathRaw[path.indicesStateStarts[i]]:
        i += 1
    
    currWordEndFrame = path.indicesStateStarts[i]
    
#     currWordBeginFrame = path.indicesStateStarts[countFirstState]
#     currWordEndFrame = path.indicesStateStarts[countLastState]
    
    return currWordBeginFrame, currWordEndFrame


def parsePhonemes(lyricsTextGrid, syllableIdx, highLevel, lowLevel):
    '''
    parse phoneme ground truth timestamps for given syllable
    @highlevel - tier name syllable/word
    @lowLevel tier name phonemes
    '''

    syllable, dummy = readNonEmptyTokensTextGrid(lyricsTextGrid, highLevel, syllableIdx, syllableIdx)

    
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


def _findBeginEndIndices(lowLevelTokensList, lowerLevelTokenPointer, highLevelBeginTs, highLevelEndTs, highLevel, durationsList=None):
    ''' 
    find indices of lower level tier whihc align with indices of highLevel tier
    @return: fromLowLevelTokenIdx, toLowLevelTokenIdx
    @param lowerLevelTokenPointer: being updated, and returned 
    '''
    if durationsList != None:
        if len(durationsList) != len(lowLevelTokensList):
            sys.exit(" len(durationsList) {} != lowLevelTokensList {} ".format(len(durationsList), len(lowLevelTokensList)))
    
    currSentenceSyllablesLIst = []
    
    
    while lowLevelTokensList[lowerLevelTokenPointer][0] < highLevelBeginTs: # search for beginning
        lowerLevelTokenPointer += 1
    
    currTokenBegin = lowLevelTokensList[lowerLevelTokenPointer][0]
    if not currTokenBegin == highLevelBeginTs: # start Ts has to be aligned
        logging.warning("token of lower layer has starting time {}, but expected {} from higher layer ".format(currTokenBegin, highLevelBeginTs))
    fromLowLevelTokenIdx = lowerLevelTokenPointer
    
    while lowerLevelTokenPointer < len(lowLevelTokensList) and float(lowLevelTokensList[lowerLevelTokenPointer][1]) <= highLevelEndTs: # syllables in currSentence
        lowerLevelTokenPointer += 1
    
    currTokenEnd = lowLevelTokensList[lowerLevelTokenPointer - 1][1]
    if not currTokenEnd == highLevelEndTs: # end Ts has to be aligned
        logging.warning(" token of lower layer has ending time {}, but expected {} from higher layer ".format(currTokenEnd, highLevelEndTs))
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


def phonemeTokens2Classes( phonemeTokensAnno):
    phonemesAnnoList = []
    for phonemeAnno in phonemeTokensAnno:
        currPhn = Phoneme(phonemeAnno[2].strip())
        currPhn.setBeginTs(phonemeAnno[0])
        currPhn.setEndTs(phonemeAnno[1])
        phonemesAnnoList.append(currPhn)
    
    return phonemesAnnoList
        
    
def testT(lyricsWithModels):
        '''
        parsing of words template function 
        '''
    
        indicesBeginWords = []
        
        currBeginIndex = NUMSTATES_SIL 
        for word_ in lyricsWithModels.listWords:
            
#             indicesBeginWords.append( (currBeginIndex, word_.text) )
            indicesBeginWords.append( currBeginIndex )

            wordTotalDur = 0 
            for syllable_ in word_.syllables:
                for phoneme_ in syllable_.phonemes:
                    currDuration = NUMSTATES_PHONEME * phoneme_.getDurationInMinUnit()
                    wordTotalDur = wordTotalDur + currDuration  
            
            currBeginIndex  = currBeginIndex + wordTotalDur
        
        # last word sil
        indicesBeginWords.append( currBeginIndex )

        
        return  indicesBeginWords  