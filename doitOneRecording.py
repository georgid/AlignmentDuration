'''
Created on Nov 28, 2014

@author: joro
'''


import sys
import os
import glob
import logging
from doitOneChunk import HMM_LIST_URI, MODEL_URI, ANNOTATION_EXT, getSectionNumberFromName, alignDependingOnWithDuration,\
    AUDIO_EXT
from Utilz import getMeanAndStDevError
from genericpath import isfile
from Decoder import logger
from MakamRecording import _loadsectionTimeStampsLinksNew




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


from hmm.Parameters import Parameters
from hmm.ParametersAlgo import ParametersAlgo

def doitOneRecording(argv):
    '''
    for a list of recordings, select those which name contains pattern and evlauate total error 
    ''' 
    if len(argv) != 6 and  len(argv) != 7 :
            print ("usage: {}  <pathToComposition>  <URIRecording> <ALPHA>  <ONLY_MIDDLE_STATE> <evalLevel> <usePersistentFiles=True> ".format(argv[0]) )
            sys.exit();
    
        
    pathToComposition  = argv[1]
    URIrecordingNoExt = argv[2]
    withDuration = True
    withSynthesis = True

    
        
    ALPHA = float(argv[3])
    
     
    ONLY_MIDDLE_STATE = argv[4]
    
    params = Parameters(ALPHA, ONLY_MIDDLE_STATE)
    
    evalLevel = int(argv[5])
    
    usePersistentFiles = 'True'
    if len(argv) == 7:
        usePersistentFiles =  argv[6]
        
         
    totalErrors = []
    
    totalCorrectDurationsReference = 0
    totalCorrectDurations = 0
    
    totalDurations = 0
    
    
#     htkParser = None
#     if withDuration:
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    # TODO: fetch sectionLinks
    URIsectionLinks = '/Users/joro/Downloads/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya.sectionLinks.json' 
    # parse section links
    sections = _loadsectionTimeStampsLinksNew( URIsectionLinks) 
    
    for  currSection in sections :
            if currSection.melodicStructure.startswith('ARANAGME'):
                continue
            currAlignmentErrors,  detectedAlignedfileName, currCorrectDuration, currTotalDuration, currCorrectDurationRef, maxPhiScore = alignDependingOnWithDuration(URIrecordingNoExt, currSection, pathToComposition, withDuration, withSynthesis, evalLevel, params, usePersistentFiles, htkParser)

            totalErrors.extend(currAlignmentErrors)
            totalCorrectDurationsReference += currCorrectDurationRef
            totalCorrectDurations += currCorrectDuration
            totalDurations += currTotalDuration
#             visualiseInPraat(URIrecordingNoExt, withDuration, detectedWordList, grTruthDurationWordList)

    mean = []
    stDev =  []     
    if len(totalErrors) != 0:    
        mean, stDev, median = getMeanAndStDevError(totalErrors)
        infoA = "Total  mean: "  "," +  str(mean), ", st dev: " + str(stDev) +   " ALPHA: " +  str(ALPHA)
        logger.info(infoA)
        
        
    accuracy = totalCorrectDurations / totalDurations
    logger.info("accuracy: {:.2f}".format(accuracy))
    return mean, stDev, totalErrors, totalCorrectDurations, totalDurations, totalCorrectDurationsReference





if __name__ == '__main__':
    doitOneRecording(sys.argv)
    
