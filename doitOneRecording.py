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
    visualiseInPraat
from Utilz import getMeanAndStDevError




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

def getSectionNumberFromName(URIrecordingNoExt):

    underScoreTokens  = URIrecordingNoExt.split("_")
    index = -1
    while (-1 * index) <= len(underScoreTokens):
        token = str(underScoreTokens[index])
        if token.startswith('meyan') or token.startswith('zemin') or \
        token.startswith('nakarat'):
            break
        index -=1
    
    try:
        whichSection = underScoreTokens[index-1]
    except Exception:
        sys.exit("please put the number of section before its name: e.g. *_2_meyan_* in the file name ")
    return int(whichSection)

def doitOneRecording(argv):
    '''
    for a list of recordings, select those which name contains pattern and evlauate total error 
    ''' 
    if len(argv) != 6 and  len(argv) != 7 :
            print ("usage: {}  <pathToComposition>  <pathToRecordings> <pattern> <ALPHA>  <ONLY_MIDDLE_STATE> <usePersistentFiles=True> ".format(argv[0]) )
            sys.exit();
    
    os.chdir(argv[2])
    
    
        
# get annot files with starting pattern
    pattern = argv[3] + '*'   + ANNOTATION_EXT
    listAnnoFiles = glob.glob(pattern) 
        
    for i in range(len(listAnnoFiles)) :
        listAnnoFiles[i] = os.path.join(argv[2], listAnnoFiles[i])
    
    for file in listAnnoFiles:
        print file
        
    pathToComposition  = argv[1]
    
    ALPHA = float(argv[4])
    
     
    ONLY_MIDDLE_STATE = argv[5]
    
    params = Parameters(ALPHA, ONLY_MIDDLE_STATE)
    
    usePersistentFiles = 'True'
    if len(argv) == 7:
        usePersistentFiles =  argv[6]
        
     
    totalErrors = []
    
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    for  URI_annotation in listAnnoFiles :
            URIrecordingNoExt  = os.path.splitext(URI_annotation)[0]
            logging.info("PROCESSING {}".format(URIrecordingNoExt) )
            whichSection = getSectionNumberFromName(URIrecordingNoExt) 
            
            currAlignmentErrors, detectedWordList, grTruthDurationWordList = alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, params, usePersistentFiles)
            totalErrors.extend(currAlignmentErrors)
            
            visualiseInPraat(URIrecordingNoExt, detectedWordList, False, grTruthDurationWordList)

          
        
    mean, stDev, median = getMeanAndStDevError(totalErrors)
    infoA = "( mean: "  "," +  str(mean), ", st dev: " + str(stDev) +   " ALPHA: " +  str(ALPHA)

    logging.info(infoA)
    return mean, stDev, totalErrors



if __name__ == '__main__':
    doitOneRecording(sys.argv)
    
