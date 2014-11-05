'''
matlab dtw with durations.
extractes the sylable-duration and wordend info from given makamScore
Created on Oct 21, 2014

@author: joro
'''
import sys
import os
import glob

parentDir = os.pathRaw.abspath(os.pathRaw.join(os.pathRaw.dirname(os.pathRaw.realpath(sys.argv[0]) ), os.pathRaw.pardir)) 
parentParentDir = os.pathRaw.abspath(os.pathRaw.join(os.pathRaw.dirname(os.pathRaw.realpath(sys.argv[0]) ), os.pathRaw.pardir,  os.pathRaw.pardir)) 
pathUtils = os.pathRaw.join(parentParentDir, 'utilsLyrics')

sys.pathRaw.append(parentDir )
sys.pathRaw.append(pathUtils )

from MakamScore import MakamScore
import MakamScore
import imp
from Utilz import writeListToTextFile
import Syllable

              
              
def getIndicesPhonemes(makamScore, whichSection ):
        '''
        getIndices of word begins in phoneme list expanded with states used in DTW alignment
        '''
        lyrics = makamScore.getLyricsForSection(whichSection)
        
#       consists of tuples startIndices and word identities
        indicesBeginWords = []
        
        NUMSTATES_SIL = 3
        NUMSTATES_PHONEME = 3
        
        # start with sil, +1 to satisfy indexing in matlab
        currBeginIndex = NUMSTATES_SIL + 1
         
        
        for word_ in lyrics.listWords:
            
#             indicesBeginWords.append( (currBeginIndex, word_.text) )
            indicesBeginWords.append(currBeginIndex )
            # sp has one state only
            currBeginIndex  = currBeginIndex + NUMSTATES_PHONEME * (word_.getNumPhonemes() - 1) + 1
        # last word sil
        indicesBeginWords.append(currBeginIndex )
        
        return  indicesBeginWords
    
    
    
    
              
            
    
def getIndicesPhonemes_durations(makamScore, whichSection):
        ''' same as getIndicesPhonemes but with durations.
        Assume phoneme.Durations are calculated.  
        '''
        
        makamScore._calcPhonemeDurations(whichSection)
        
        lyrics = makamScore.getLyricsForSection(whichSection)
        
#       consists of tuples startIndices and word identities
        indicesBeginWords = []
        
        NUMSTATES_SIL = 3
        NUMSTATES_PHONEME = 3
        
        currBeginIndex = NUMSTATES_SIL + 1
         
        
        for word_ in lyrics.listWords:
            
#             indicesBeginWords.append( (currBeginIndex, word_.text) )
            indicesBeginWords.append( currBeginIndex )

            wordTotalDur = 0 
            for syllable_ in word_.syllables:
                for phoneme_ in syllable_.phonemes:
                    currDuration = NUMSTATES_PHONEME * phoneme_.getDuration()
                    wordTotalDur = wordTotalDur + currDuration  
            
            currBeginIndex  = currBeginIndex + wordTotalDur
        
        # last word sil
        indicesBeginWords.append( currBeginIndex )

        
        return  indicesBeginWords
 
 
#        end of class

              
                    
def serializeIndices( makamScore, whichSection, withDurations, URI_IndicesFile):
    '''
    helper method
    '''
    if withDurations:
           indices =  getIndicesPhonemes_durations(makamScore, whichSection)
             
    else:
 
           indices = getIndicesPhonemes(makamScore, whichSection)
        
    writeListToTextFile(indices, None,  URI_IndicesFile ) 


        

def parseScoreAndSerialize(pathToComposition, whichSection, withDurations):
        '''
        Main method for  DTW in matlab
        prints sequence of phonemes, sequence of durarions. indices of word start positions 
        '''
        
        makamScore = MakamScore.loadScore(pathToComposition)
        
        # DEBUG
        makamScore.printSyllables(whichSection)
        
        # 1. phoneme IDs
        listPhonemes = makamScore.serializePhonemesForSection(whichSection, '/tmp/test.phn')
        listDurations = []
        
        # 2. phoneme Durations
        makamScore._calcPhonemeDurations(whichSection)

        for phoneme_ in listPhonemes :
            listDurations.append(phoneme_.duration)
        writeListToTextFile(listDurations, None, '/tmp/test.durations')
        
        # 3. indices
        
        
        serializeIndices(makamScore, whichSection, withDurations, '/tmp/test.indices')
        
#       just for information   
#         makamScore.printSectionsAndLyrics()

                               
     


def mainDTWMatlab(argv):
        if len(argv) != 4:
            print ("usage: {} <dir of symbtTr.txt and symbTr.tsv> <whichSectionNumber> <hasDurations?>".format(argv[0]) )
            sys.exit();

        parseScoreAndSerialize(argv[1], int(argv[2]), int(argv[3]))   

if __name__ == '__main__':
    mainDTWMatlab(sys.argv)