'''
Created on Nov 28, 2014

@author: joro
'''


import sys
import os
from doitOneChunk import HMM_LIST_URI, MODEL_URI, ANNOTATION_EXT, getSectionNumberFromName, alignDependingOnWithDuration,\
    AUDIO_EXT
from Utilz import getMeanAndStDevError
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

pathPycompmusic = os.path.join(parentDir, 'pycompmusic')
if pathPycompmusic not in sys.path:
    sys.path.append(pathPycompmusic)
   
from compmusic import dunya
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

pathDunya = os.path.join(parentDir, 'dunya')
if pathDunya not in sys.path:
    sys.path.append(pathDunya)

# from docserver import util

from hmm.Parameters import Parameters

def doitOneRecording(argv):
    '''
    for a list of recordings, select those which name contains pattern and evlauate total error 
    ''' 
    if len(argv) != 6 and  len(argv) != 7 :
            print ("usage: {}  <pathToComposition>  <URIRecording> <mbID> <ALPHA>  <ONLY_MIDDLE_STATE> <evalLevel> <usePersistentFiles=True> ".format(argv[0]) )
            sys.exit();
    
    recMusicbrainzid = argv[3]
    
#     rec_data = dunya.makam.get_recording(recMusicbrainzid )
#     if len(rec_data['works']) == 0:
#             raise Exception('No work on recording %s' % recMusicbrainzid)
#     if len(rec_data['works']) > 1:
#             raise Exception('More than one work for recording %s Not implemented!' % recMusicbrainzid)
#     w = rec_data['works'][0]
    
#     sectionsurl = util.docserver_get_url(recMusicbrainzid, "scorealign", "sectionlinks", 1, version="0.2")
#     
#     metadata = util.docserver_get_filename(w['mbid'], "metadata", "metadata", version="0.1")
#     TODO: put metadata in section 
    
    pathToComposition  = argv[1]
    URIrecordingNoExt = argv[2]
    withDuration = True
    withSynthesis = True

    
        
    ALPHA = float(argv[4])
    
     
    ONLY_MIDDLE_STATE = argv[5]
    
    params = Parameters(ALPHA, ONLY_MIDDLE_STATE)
    
    evalLevel = int(argv[6])
    
    usePersistentFiles = 'True'
    if len(argv) == 8:
        usePersistentFiles =  argv[7]
        
         
    totalErrors = []
    
    totalCorrectDurationsReference = 0
    totalCorrectDurations = 0
    
    totalDurations = 0
    
    
#     htkParser = None
#     if withDuration:
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    # TODO: fetch sectionLinks
    URIsectionLinks = URIrecordingNoExt + '.sectionLinks.json' 
    # parse section links
    sectionLinks = _loadsectionTimeStampsLinksNew( URIsectionLinks) 
    
    for  currSectionLink in sectionLinks :
            if currSectionLink.melodicStructure.startswith('ARANAGME'):
                continue
            currAlignmentErrors,  currCorrectDuration, currTotalDuration, currCorrectDurationRef, maxPhiScore = alignDependingOnWithDuration(URIrecordingNoExt, currSectionLink, pathToComposition, withDuration, withSynthesis, evalLevel, params, usePersistentFiles, htkParser)

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
    
