'''
Created on Nov 28, 2014

@author: joro
'''


import sys
print 'SYS PATH is: ', sys.path
import os
import glob
import logging
from doitOneChunk import alignOneChunk, HMM_LIST_URI, MODEL_URI, ANNOTATION_EXT
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



def doitOneRecording(argv):
    '''
    for a list of recordings, select those which name contains pattern and evlauate total error 
    ''' 
    if len(argv) != 4 and  len(argv) != 5 :
            print ("usage: {}  <pathToComposition>  <pathToRecordings> <pattern> <usePersistentFiles=False>".format(argv[0]) )
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
    
    usePersistentFiles = False
    if len(argv) == 5: usePersistentFiles = argv[4]
        
     
    totalErrors = []
    
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    for  URI_annotation in listAnnoFiles :
            URIrecordingNoExt  = os.path.splitext(URI_annotation)[0]
            logging.info("PROCESSING {}".format(URIrecordingNoExt) )
            whichSection  = int(URIrecordingNoExt.split("_")[-2])
            currAlignmentErrors, detectedWordList = alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, usePersistentFiles)
            totalErrors.extend(currAlignmentErrors)
          
        
    mean, stDev, median = getMeanAndStDevError(totalErrors)
    print "( mean: "  ",", mean, ", st dev: " , stDev ,   ")"  
    return mean, stDev



if __name__ == '__main__':
    doitOneRecording(sys.argv)
    