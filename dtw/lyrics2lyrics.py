'''
Created on Apr 9, 2015

@author: joro
'''

import sys
import os

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

from Utilz import writeListToTextFile, getBeginTsFromName



from MakamScore import loadMakamScore
from doitOneChunk import HMM_LIST_URI, MODEL_URI, loadMFCCs
from LyricsWithModels import LyricsWithModels

def parseScoreAndSerializeStatesWithRealTempo(pathToComposition, whichQuerySection, URIqueryRecordingNoExt, output_statesURI,  tempoCoefficient):
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
    stateDurationsInFramesList = queryLyricsWithModels.stateDurations2Network()
        
    writeListToTextFile(stateDurationsInFramesList, None, output_statesURI + "_" + str(tempoCoefficient))   


if __name__ == '__main__':

    if len(sys.argv) != 5:
            print ("usage: {} <dir of symbtTr.txt and symbTr.tsv> <whichSectionNumber> <URI_recordingQuery_to_get_tempo_from> <tempoCoefficient>".format(sys.argv[0]) )
            sys.exit();
        
        
    pathToComposition = sys.argv[1];   
    whichQuerySection = int(sys.argv[2])
    

    
    
        ################################
    # get name of wav file for query 
    URI_recordingQuery_notFull =  sys.argv[3];
    URI_recordingQuery_notFull += '_' + str(whichQuerySection); 
    
    recordingPath = os.path.dirname(URI_recordingQuery_notFull) 
    
    a = glob.glob(URI_recordingQuery_notFull + '*.wav')
    print URI_recordingQuery_notFull
    URIqueryRecordingNoExt =  a[0]
    URIqueryRecordingNoExt = os.path.splitext(URIqueryRecordingNoExt)[0]
    #  get query wav done
    #######################################
    
    tempoCoefficient = float (sys.argv[4])  

    output_statesURI = pathToComposition + str(whichQuerySection) + '.states'
    
    parseScoreAndSerializeStatesWithRealTempo(pathToComposition, whichQuerySection, URIqueryRecordingNoExt, output_statesURI,  tempoCoefficient)
