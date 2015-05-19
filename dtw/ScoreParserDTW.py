'''
matlab dtw with durations.
extractes the sylable-durationInMinUnit and wordend info from given makamScore
Created on Oct 21, 2014

@author: joro
'''
import sys
import os
print sys.getdefaultencoding()

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir,  os.path.pardir)) 

pathUtils = os.path.join(parentParentDir, 'utilsLyrics')

sys.path.append(parentDir )

import glob
from LyricsWithModels import LyricsWithModels
from doitOneChunk import loadMFCCs, HMM_LIST_URI, MODEL_URI

sys.path.append(pathUtils )

# parser of htk-build speech model
pathHtkModelParser = os.path.join(parentParentDir, 'pathHtkModelParser')
if pathHtkModelParser not in sys.path:
    sys.path.append(pathHtkModelParser)
from htk_converter import HtkConverter


from Constants import NUMSTATES_SIL, NUMSTATES_PHONEME

from MakamScore import MakamScore, loadMakamScore
import imp
from Utilz import writeListToTextFile, getBeginTsFromName
import Syllable




              
              
def getIndicesPhonemes(makamScore, whichSection ):
        '''
        getIndices of word begins in phoneme list expanded with states used in DTW alignment
        '''
        lyrics = makamScore.getLyricsForSection(whichSection)
        
#       consists of tuples startIndices and word identities
        indicesBeginWords = []
        

        
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
    
    
    
    
              
            
    
def getBeginIndicesWords_Withdurations(makamScore, whichSection):
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
# TODO: rewrite this line with getDurationInTimeFrame instead
                    currDuration = NUMSTATES_PHONEME * phoneme_.getDurationInMinUnit()

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
           indices =  getBeginIndicesWords_Withdurations(makamScore, whichSection)
             
    else:
 
           indices = getIndicesPhonemes(makamScore, whichSection)
        
    writeListToTextFile(indices, None,  URI_IndicesFile ) 


        

def parseScoreAndSerialize(pathToComposition, whichSection, withDurations):
        '''
        Main method for  DTW in matlab
        prints sequence of phonemes, sequence of durarions. indices of word start positions 
        '''
        
        makamScore = loadMakamScore(pathToComposition)
        
        # DEBUG
        makamScore.printSyllables(whichSection)
        
        # 1. phoneme IDs 
        listPhonemes = makamScore.serializePhonemesForSection(whichSection, pathToComposition + 'tmp.phn')
        listDurations = []
        
        # ... and durations 
        for phoneme_ in listPhonemes :
            listDurations.append(phoneme_.durationInMinUnit)
        writeListToTextFile(listDurations, None, pathToComposition + 'tmp.dur')
        
        # 2. indices
        
        
#         serializeIndices(makamScore, whichSection, withDurations, '/tmp/test.indices')
        
#       just for information   
#         makamScore.printSectionsAndLyrics()


def parseScoreAndSerializeWithRealTempo2(pathToComposition, whichQuerySection, URIrecordingNoExt):
    '''
    needs lyrics for target recording and that it does not have silence at begin and end 
    two mthods need to be implemented. 
    '''
    
    onyMiddleState = False
    makamScore = loadMakamScore(pathToComposition)
    
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    # tempo for target *
    targetLyrics = makamScore.getLyricsForSection(2)

    targetLyricsWithModels = LyricsWithModels(targetLyrics, htkParser, onyMiddleState )
    observationFeatures = loadMFCCs(URIrecordingNoExt) #     observationFeatures = observationFeatures[0:1000]
    targetLyricsWithModels.duration2numFrameDuration(observationFeatures, URIrecordingNoExt)                          
    
    # query
    lyricsQuery = makamScore.getLyricsForSection(whichQuerySection)
    
    # **
    LyricsWithModels.getLyricsWithModels(lyricsQuery);
   

def parseScoreAndSerializeWithRealTempo(pathToComposition, whichQuerySection, URIqueryRecordingNoExt, output_statesURI, output_durationsURI, tempoCoefficient):
    '''
    limitation is it needs wav for URIqueryRecordingNoExt
    '''
    onyMiddleState = 'False'
    makamScore = loadMakamScore(pathToComposition)
    
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    # query
    lyricsQuery = makamScore.getLyricsForSection(whichQuerySection)
  
    queryLyricsWithModels = LyricsWithModels (lyricsQuery, htkParser, onyMiddleState )
    observationFeatures = loadMFCCs(URIqueryRecordingNoExt) #     observationFeatures = observationFeatures[0:1000]
    queryLyricsWithModels.duration2numFrameDuration(observationFeatures, URIqueryRecordingNoExt, tempoCoefficient)                          
    
    # here expand lyrics
#     phonemeDurationsInFramesList = queryLyricsWithModels.phonemeDurationsInFrames2List()
    stateDurationsInFramesList = queryLyricsWithModels.stateDurationInFrames2List()
        
    writeListToTextFile(queryLyricsWithModels.statesNetwork, None, output_statesURI )    
    writeListToTextFile(stateDurationsInFramesList, None, output_durationsURI + "_" + str(tempoCoefficient))    



def mainDTWMatlab(argv):
        if len(argv) != 4:
            print ("usage: {} <dir of symbtTr.txt and symbTr.tsv> <whichSectionNumber> <hasDurations?>".format(argv[0]) )
            sys.exit();
        
        parseScoreAndSerialize(argv[1], int(argv[2]), int(argv[3]))

    

if __name__ == '__main__':
#     mainDTWMatlab(sys.argv)

        if len(sys.argv) != 5:
            print ("usage: {} <dir of symbtTr.txt and symbTr.tsv> <whichSectionNumber> <URI_recordingQuery_to_get_tempo_from> <tempoCoefficient>".format(sys.argv[0]) )
            sys.exit();
            
        URI_score_folder = sys.argv[1];   
        whichSection = int(sys.argv[2])
        
        ################################
        # get name of wav file for query 
        URI_recordingQuery_notFull =  sys.argv[3];
        URI_recordingQuery_notFull += '_' + str(whichSection); 
        
        recordingPath = os.path.dirname(URI_recordingQuery_notFull) 
        
        a = glob.glob(URI_recordingQuery_notFull + '*.wav')
        print URI_recordingQuery_notFull
        URI_recordingQuery_no_ext =  a[0]
        URI_recordingQuery_no_ext = os.path.splitext(URI_recordingQuery_no_ext)[0]
        #  get query wav done
        #######################################
        
        tempoCoefficient = int (sys.argv[4])  

        
        # 2. phonemesList and its corresponding durations to tsv
        output_statesURI = URI_score_folder + str(whichSection) + '.states'
        output_durationsURI = URI_score_folder + str(whichSection) + '.dur'
        parseScoreAndSerializeWithRealTempo(URI_score_folder, whichSection, URI_recordingQuery_no_ext , output_statesURI, output_durationsURI, tempoCoefficient)
        
        print output_statesURI
        print output_durationsURI
        