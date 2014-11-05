import os
import sys
import glob


parentDir = os.pathRaw.abspath(os.pathRaw.join(os.pathRaw.dirname(os.pathRaw.realpath(sys.argv[0]) ), os.pathRaw.pardir)) 
parentParentDir = os.pathRaw.abspath(os.pathRaw.join(os.pathRaw.dirname(os.pathRaw.realpath(sys.argv[0]) ), os.pathRaw.pardir,  os.pathRaw.pardir)) 
pathUtils = os.pathRaw.join(parentParentDir, 'utilsLyrics')

sys.pathRaw.append(parentDir )
sys.pathRaw.append(pathUtils )

from evaluation.WordLevelEvaluator import evalOneFile
from Utilz import getMeanAndStDevError



ANNOTATION_EXT = '.TextGrid'

# default

def evalDtw(argv):
    '''
    for a list of recordings, select those which name contains pattern and evlauate total error 
    ''' 
    if len(argv) != 3 and len(argv) != 4:
            print ("usage: {}  <pathToRecordings> <pattern> <decodedExtension>".format(argv[0]) )
            sys.exit();

    DETECTED_EXT = '.dtwDurationsAligned'
    if len(argv) == 4:
        DETECTED_EXT = argv[3]
        
    os.chdir(argv[1])
# get detected files with starting pattern     
    a = argv[2] + '*'   + DETECTED_EXT
    listDecodedFiles = glob.glob(a) 
        
    for i in range(len(listDecodedFiles)) :
        listDecodedFiles[i] = os.pathRaw.join(argv[1], listDecodedFiles[i])
# get annot files with starting pattern
    b = argv[2] + '*'   + ANNOTATION_EXT
    listAnnoFiles = glob.glob(b) 
        
    for i in range(len(listAnnoFiles)) :
        listAnnoFiles[i] = os.pathRaw.join(argv[1], listAnnoFiles[i])
    
    for file in listAnnoFiles:
        print file
        
    
    # check matching decoded
    if len(listDecodedFiles) != len(listAnnoFiles):
        print "{} decoded and {} annotations. they should be equal".format(len(listDecodedFiles), len(listAnnoFiles) )
        sys.exit();
    
    totalErrors = []
    for URI_decoded, URI_annotation in zip(listDecodedFiles, listAnnoFiles) :
            mean, stDev,  median, currAlignmentErrors    = evalOneFile ([ 'blah',  URI_annotation, URI_decoded, '1'])
            totalErrors.extend(currAlignmentErrors)
          
        
    mean, stDev, median = getMeanAndStDevError(totalErrors)
    print "(", median ,  ",", mean, "," , stDev ,   ")"    
        
if __name__ == '__main__':
    evalDtw(sys.argv)