'''
Created on Dec 16, 2014
Utility class: logic for parsing statesNetwork, phoeneNetwork  
@author: joro
'''
import sys
from Constants import NUM_FRAMES_PERSECOND, NUMSTATES_SIL, NUMSTATES_PHONEME

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
    if lastSyll.hasShortPauseAtEnd: # sanity check that last syllable is sp
        if lastPhoneme.ID != 'sp':
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
        currWordBeginFrame = path.indicesStateStarts[countFirstState]
        currWordEndFrame = path.indicesStateStarts[countLastState]
    #             # debug:
    #             print self.pathRaw[currWordBeginFrame]
    # timestamp:
        startTs = float(currWordBeginFrame) / NUM_FRAMES_PERSECOND
        endTs = float(currWordEndFrame) / NUM_FRAMES_PERSECOND
        
        detectedWord = [startTs, endTs, text, startNoteNumber]
#         print detectedWord
        
        return detectedWord, dummy
        
    
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