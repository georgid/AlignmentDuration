'''
Created on Nov 28, 2014

@author: joro
'''


import sys
import os
import glob
import logging
from doitOneChunk import HMM_LIST_URI, MODEL_URI, ANNOTATION_EXT, getSectionNumberFromName, alignDependingOnWithDuration,\
    AUDIO_EXT, deviationInSec
from Utilz import getMeanAndStDev
from genericpath import isfile
from Decoder import logger




parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
# parser of htk-build speech model
pathHtkModelParser = os.path.join(parentDir, 'pathHtkModelParser')
sys.path.append(pathHtkModelParser)
from htkparser.htk_converter import HtkConverter

pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )

#  evaluation  
pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
sys.path.append(pathEvaluation)

pathDuration = os.path.join(parentDir, 'HMMDuration')
if not pathDuration in sys.path:
    sys.path.append(pathDuration)

from hmm.Parameters import Parameters


def doitOneRecording(argv):
    '''
    for a list of recordings, select those which name contains pattern and evlauate total error 
    ''' 
    if len(argv) != 9 and  len(argv) != 10 :
            print ("usage: {}  <pathToComposition>  <pathToRecordings> <pattern> <withDuration=True/False> <withSynthesis> <ALPHA>  <ONLY_MIDDLE_STATE> <evalLevel> <usePersistentFiles=True> ".format(argv[0]) )
            sys.exit();
    
    os.chdir(argv[2])
    
    
        
# get annot files with starting pattern
    pattern = argv[3] + '*'   + AUDIO_EXT
    listAudioFilesAll = glob.glob(pattern) 
        

    for i in range(len(listAudioFilesAll)) :
        listAudioFilesAll[i] = os.path.join(argv[2], listAudioFilesAll[i])
        
#     listAudioFiles = []
#         if not isfile( os.path.splitext(listAudioFilesAll[i])[0] +  ".notUsed"):
#             listAudioFiles.append(listAudioFilesAll[i])
    listAudioFiles = listAudioFilesAll
    
    for file in listAudioFiles:
        logger.debug(file)
        
    pathToComposition  = argv[1]
    withDuration = argv[4]
    if withDuration=='True':
        withDuration = True
    elif withDuration=='False':
        withDuration = False
    else: 
        sys.exit("withDuration can be only True or False")  
    
    withSynthesis = argv[5]
    if withSynthesis=='True':
        withSynthesis = True
    elif withSynthesis=='False':
        withSynthesis = False
    else: 
        sys.exit("withSynthesis can be only True or False")  

    
        
    ALPHA = float(argv[6])
    
     
    ONLY_MIDDLE_STATE = argv[7]
    
    params = Parameters(ALPHA, ONLY_MIDDLE_STATE, deviationInSec)
    
    evalLevel = int(argv[8])
    
    usePersistentFiles = 'True'
    if len(argv) == 10:
        usePersistentFiles =  argv[9]
        
         
    totalErrors = []
    
    totalCorrectDurationsReference = 0
    totalCorrectDurations = 0
    
    totalDurations = 0
    
    
#     htkParser = None
#     if withDuration:
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    for  URI_annotation in listAudioFiles :
            URIrecordingNoExt  = os.path.splitext(URI_annotation)[0]
            logger.debug("PROCESSING {}".format(URIrecordingNoExt) )
            whichSection = getSectionNumberFromName(URIrecordingNoExt) 
            
            currAlignmentErrors,  detectedAlignedfileName, currCorrectDuration, currTotalDuration, currCorrectDurationRef = alignDependingOnWithDuration(URIrecordingNoExt, whichSection, pathToComposition, withDuration, withSynthesis, evalLevel, params, usePersistentFiles, htkParser)

            totalErrors.extend(currAlignmentErrors)
            totalCorrectDurationsReference += currCorrectDurationRef
            totalCorrectDurations += currCorrectDuration
            totalDurations += currTotalDuration
#             visualiseInPraat(URIrecordingNoExt, withDuration, detectedWordList, grTruthDurationWordList)

    mean = []
    stDev =  []     
    if len(totalErrors) != 0:    
        mean, stDev, median = getMeanAndStDev(totalErrors)
        infoA = "Total  mean: "  "," +  str(mean), ", st dev: " + str(stDev) +   " ALPHA: " +  str(ALPHA)
        logger.info(infoA)
        
        
    accuracy = totalCorrectDurations / totalDurations
    logger.info("accuracy: {:.2f}".format(accuracy))
    return mean, stDev, totalErrors, totalCorrectDurations, totalDurations, totalCorrectDurationsReference



if __name__ == '__main__':
    doitOneRecording(sys.argv)
    
