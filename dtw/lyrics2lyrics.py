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
from doitOneChunk import HMM_LIST_URI, MODEL_URI
from FeatureExtractor import loadMFCCs

sys.path.append(pathUtils )

# parser of htk-build speech model
pathHtkModelParser = os.path.join(parentParentDir, 'pathHtkModelParser')
if pathHtkModelParser not in sys.path:
    sys.path.append(pathHtkModelParser)
from htk_converter import HtkConverter

from Utilz import writeListToTextFile, getBeginTsFromName

pathSearchByLyricsEval = os.path.join(parentParentDir, 'SearchByLyricsEval')
if pathSearchByLyricsEval not in sys.path:
    sys.path.append(pathSearchByLyricsEval)
from Evaluation import loadDatasetMappingToScores


from MakamScore import loadMakamScore

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
    deviationInSecDummy = 0.0
  
    queryLyricsWithModels = LyricsWithModels (lyricsQuery, htkParser, onyMiddleState,deviationInSecDummy )
    withSynthesis = False
#     observationFeatures, URIRecordingChunk = loadMFCCs(URIqueryRecordingNoExt, withSynthesis, -1, -1) #     observationFeatures = observationFeatures[0:1000]
    
    mappingURL = '/Users/joro/Documents/Phd/UPF/ISTANBUL/DatasetMappingToScores'
    dictMappings = loadDatasetMappingToScores(mappingURL)

    recordingMBID = dictMappings[URIqueryRecordingNoExt][3]
    
    queryLyricsWithModels.duration2numFrameDurationSertanTempo(recordingMBID, tempoCoefficient)                          
    
    # here expand lyrics
#     phonemeDurationsInFramesList = queryLyricsWithModels.phonemeDurationsInFrames2List()
    stateDurationsInFramesList = queryLyricsWithModels.stateDurations2Network()
    
    
    writeListToTextFile(stateDurationsInFramesList, None, output_statesURI + "_" + str(tempoCoefficient))   

def doit(argv):
    if len(argv) != 5:
            print ("usage: {} <dir of symbtTr.txt and symbTr.tsv> <whichSectionNumber> <URI_recordingQuery_to_get_tempo_from> <tempoCoefficient>".format(argv[0]) )
            sys.exit();
        
        
    pathToComposition = argv[1];   
    whichQuerySection = int(argv[2])
    

    
    
        ################################
    # get name of wav file for query 
    URI_recordingQuery_notFull =  argv[3];
    URI_recordingQuery_notFull += '_' + str(whichQuerySection); 
    
    recordingPath = os.path.dirname(URI_recordingQuery_notFull) 
    
    a = glob.glob(URI_recordingQuery_notFull + '*.wav')
    URIqueryRecordingNoExt =  a[0]
    URIqueryRecordingNoExt = os.path.splitext(URIqueryRecordingNoExt)[0]
    #  get query wav done
    #######################################
    
    tempoCoefficient = float (argv[4])  

    output_statesURI = os.path.join(pathToComposition, str(whichQuerySection) + '.states')
    
    parseScoreAndSerializeStatesWithRealTempo(pathToComposition, whichQuerySection, argv[3], output_statesURI,  tempoCoefficient)

if __name__ == '__main__':

    doit(sys.argv) 

# example usage: 

#     doit(["progName", \
#           '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/rast--sarki--curcuna--nihansin_dideden--haci_faik_bey', \
#            2, '/Users/joro/Documents/Phd/UPF/ISTANBUL/idil/Nurten_Demirkol', 1])
    
# /usr/local/bin/python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/dtw/lyrics2lyrics.py /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/ussak--sarki--aksak--bu_aksam_gun--tatyos_efendi/ 5 /Users/joro/Documents/Phd/UPF/ISTANBUL/idil/Sakin--Gec--Kalma 5