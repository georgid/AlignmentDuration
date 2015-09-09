
'''
Created on Apr 8, 2015

@author: joro
'''


import sys
# trick to make terminal/console NOT assume ascii
reload(sys).setdefaultencoding("utf-8")
import os


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir,  os.path.pardir)) 

pathUtils = os.path.join(parentParentDir, 'utilsLyrics')

sys.path.append(parentDir )

import glob

sys.path.append(pathUtils )


from Utilz import writeListToTextFile, getBeginTsFromName



if __name__ == '__main__':
    
    
    if len(sys.argv) != 3:
            print ("usage: {}   <URI_recordingQuery> <whichLevel>".format(sys.argv[0]) )
            sys.exit();
            
    
        
    ################################
    # get name of wav file for query 
    URI_recordingQuery_no_ext =  sys.argv[1];
    
     
    whichLevel = int(sys.argv[2]) ; # phrases
        
        #########
    # 1. TextGrid to tsv  to be opened in matlab
    URI_Anno = URI_recordingQuery_no_ext + '.TextGrid'
 
    try:
        initialTimeOffset = getBeginTsFromName(URI_recordingQuery_no_ext);
    except Exception:
        initialTimeOffset = 0;
    # serialize to grid
    pathEvaluation = os.path.join(parentParentDir, 'AlignmentEvaluation')
    if pathEvaluation not in sys.path:
            sys.path.append(pathEvaluation)
            
    from WordLevelEvaluator import readNonEmptyTokensTextGrid
    startIdx = 1
    endIdx = -1
#     annotationTokenListA, annotationTokenListNoPauses =  readNonEmptyTokensTextGrid(URI_Anno, whichLevel, initialTimeOffset )
    # the parameters start and endIdx might not make sense
    annotationTokenListA, annotationTokenListNoPauses =  readNonEmptyTokensTextGrid(URI_Anno, whichLevel, startIdx, endIdx )

    
    print URI_Anno + '.anno'