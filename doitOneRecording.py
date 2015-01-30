'''
Created on Nov 28, 2014

@author: joro
'''


import sys
from Parameters import Parameters
import os
import glob
import logging
from doitOneChunk import alignOneChunk, HMM_LIST_URI, MODEL_URI, ANNOTATION_EXT,\
    visualiseInPraat, getSectionNumberFromName, alignDependingOnWithDuration,\
    AUDIO_EXT
from Utilz import getMeanAndStDevError
from genericpath import isfile
from Decoder import logger




parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
# parser of htk-build speech model
pathHtkModelParser = os.path.join(parentDir, 'pathHtkModelParser')
sys.path.append(pathHtkModelParser)
from htk_converter import HtkConverter

pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )

#  evaluation  
pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
sys.path.append(pathEvaluation)


def doitOneRecording(argv):
    '''
    for a list of recordings, select those which name contains pattern and evlauate total error 
    ''' 
    if len(argv) != 8 and  len(argv) != 9 :
            print ("usage: {}  <pathToComposition>  <pathToRecordings> <pattern> <withDuration=True/False> <ALPHA>  <ONLY_MIDDLE_STATE> <evalLevel> <usePersistentFiles=True> ".format(argv[0]) )
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

    ALPHA = float(argv[5])
    
     
    ONLY_MIDDLE_STATE = argv[6]
    
    params = Parameters(ALPHA, ONLY_MIDDLE_STATE)
    
    evalLevel = int(argv[7])
    
    usePersistentFiles = 'True'
    if len(argv) == 9:
        usePersistentFiles =  argv[8]
        
         
    totalErrors = []
    
    htkParser = None
    if withDuration:
        htkParser = HtkConverter()
        htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    for  URI_annotation in listAudioFiles :
            URIrecordingNoExt  = os.path.splitext(URI_annotation)[0]
            logger.debug("PROCESSING {}".format(URIrecordingNoExt) )
            whichSection = getSectionNumberFromName(URIrecordingNoExt) 
            
            currAlignmentErrors, detectedWordList, grTruthDurationWordList = alignDependingOnWithDuration(URIrecordingNoExt, whichSection, pathToComposition, withDuration, evalLevel, params, usePersistentFiles, htkParser)

            totalErrors.extend(currAlignmentErrors)
            
            visualiseInPraat(URIrecordingNoExt, withDuration, detectedWordList, grTruthDurationWordList)

    mean = []
    stDev =  []     
    if len(totalErrors) != 0:    
        mean, stDev, median = getMeanAndStDevError(totalErrors)
        infoA = "Total  mean: "  "," +  str(mean), ", st dev: " + str(stDev) +   " ALPHA: " +  str(ALPHA)

        logger.info(infoA)
    return mean, stDev, totalErrors



if __name__ == '__main__':
    doitOneRecording(sys.argv)
    
