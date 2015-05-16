
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
    
    
    if len(sys.argv) != 4:
            print ("usage: {}  <whichSectionNumber> <URI_recordingQuery_to_get_tempo_from> <whichLevel>".format(sys.argv[0]) )
            sys.exit();
            
    
    whichSection = int(sys.argv[1]) 
        
    ################################
    # get name of wav file for query 
    URI_recordingQuery_notFull =  sys.argv[2];
    URI_recordingQuery_notFull += '_' + str(whichSection); 
    
    recordingPath = os.path.dirname(URI_recordingQuery_notFull) 
    
    a = glob.glob(URI_recordingQuery_notFull + '*.wav')
    URI_recordingQuery_no_ext =  a[0]
    URI_recordingQuery_no_ext = os.path.splitext(URI_recordingQuery_no_ext)[0]
    #  get query wav done
    #######################################    
    
    whichLevel = int(sys.argv[3]) ; # phrases
        
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

    annotationTokenListA, annotationTokenListNoPauses =  readNonEmptyTokensTextGrid(URI_Anno, whichLevel, initialTimeOffset )
    print URI_Anno + '.anno'