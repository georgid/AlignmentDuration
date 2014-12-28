'''
Created on Dec 16, 2014

@author: joro
'''
import sys
from Constants import NUM_FRAMES_PERSECOND, NUMSTATES_SIL, NUMSTATES_PHONEME

def expandlyrics2Words (lyricsWithModels, path, totalDuration, func):
    '''
    path stands for path or statesNetwork
    '''

    detectedWordList = []


       
    for word_ in lyricsWithModels.listWords:
        countFirstState = word_.syllables[0].phonemes[0].numFirstState

        lastPhoneme = word_.syllables[-1].phonemes[-1]
        if lastPhoneme.ID != 'sp':
            sys.exit(' \n last state for word {} is not sp. Sorry - not implemented.'.format(word_.text))
        
        countLastState = lastPhoneme.numFirstState

        detectedWord, totalDuration = func( word_, countFirstState, countLastState, path, totalDuration)
       
        detectedWordList.append( detectedWord)
    return detectedWordList





    
    
def _constructTimeStampsForWord(  word_, countFirstState, countLastState, statesNetwork, totalDuration):
        '''
        helper method. timestamps for word based on durations read from score 
        '''
        
        currWordBeginFrame = totalDuration
        for currState in range(countFirstState, countLastState + 1):                 
            totalDuration += statesNetwork[currState].getDurationInFrames()
        currWordEndFrame = totalDuration
        
            
    # timestamp:
        startTs = float(currWordBeginFrame) / NUM_FRAMES_PERSECOND
        endTs = float(currWordEndFrame) / NUM_FRAMES_PERSECOND
        
        detectedWord = [startTs, endTs, word_.text]
#         print detectedWord
        
        return detectedWord, totalDuration 


def _constructTimeStampsForWordDetected(  word_, countFirstState, countLastState, path, dummy):
        '''
        helper method. timestamps of detected word 
        '''
        currWordBeginFrame = path.indicesStateStarts[countFirstState]
        currWordEndFrame = path.indicesStateStarts[countLastState]
    #             # debug:
    #             print self.pathRaw[currWordBeginFrame]
    # timestamp:
        startTs = float(currWordBeginFrame) / NUM_FRAMES_PERSECOND
        endTs = float(currWordEndFrame) / NUM_FRAMES_PERSECOND
        
        detectedWord = [startTs, endTs, word_.text]
#         print detectedWord
        
        return detectedWord, dummy
        
    
def testT(lyricsWithModels):
    
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