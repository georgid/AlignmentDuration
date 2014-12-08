'''
Created on Dec 8, 2014

@author: joro
'''


import sys
from doitOneRecording import doitOneRecording
import logging
from datetime import datetime
import os

def doit(argv):
    if len(argv) != 5 and len(argv) != 6:
        print ("usage: {}  <pathToCompositions>  <pathToRecordings> <ALPHA>  <ONLY_MIDDLE_STATE> <usePersistentFiles=False>".format(argv[0]) )
        sys.exit();

    pathToScores = argv[1]

    path_testFile  = argv[2]
    
    ALPHA = argv[3]
    
    
    ONLY_MIDDLE_STATE = argv[4]
    
    usePersistentFiles = False
        
    if len(argv) == 6:
        usePersistentFiles = argv[5]
    
    scores = ['nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi', \
    'nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/', \
    'nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/', \
    'nihavent--sarki--aksak--koklasam_saclarini--artaki_candan/', \
    'ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses',\
    'nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey',\
    'ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses', \
    'segah--sarki--curcuna--olmaz_ilac--haci_arif_bey'
    ]
    subpaths = ['/goekhan/', '/goekhan/', '/barbaros/', '/barbaros/', '/safiye/', '/safiye/', '/guelen/', '/guelen/' ]
    patterns = ['02_Kimseye', '02_Gel', '02_Gel', '02_Koklasam',   '01_Aksam' ,    '01_Bakmiyor', '01_Aksam', '01_Olmaz' ]
    
    currTime = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')    
    filename = os.path.join(os.getcwdu(),   'alignError_' + currTime + '.out') 
    outputFileHandle = open(filename, 'a')
    
    logging.info("\n Output file is: " + filename )
    print "\n Output file is: ",  filename
    
    
    outputFileHandle.write('\n'  + str(ALPHA) )
    totalMean  = 0.0
    for i in range(len(scores)):

        URI_score = pathToScores + scores[i]
        URI_testFile = path_testFile + subpaths[i]
        pattern  = patterns[i]
        
        logging.info("doing command ...\n doitOneRecording  " + URI_score + " " +  URI_testFile  + " " + pattern)
        mean, stDev  = doitOneRecording([ 'dummy', URI_score, URI_testFile, pattern, ALPHA, ONLY_MIDDLE_STATE, usePersistentFiles])
        
        infoA = "( mean: "  "," +  str(mean), ", st dev: " + str(stDev) +   " ALPHA: " +  str(ALPHA)
        
        logging.info(infoA)
        print infoA
        
        listLine = '\n' + subpaths[i] + " " + pattern + " " + str(mean) +   " " + str(stDev) 
        
        if outputFileHandle.closed:
            outputFileHandle = open(filename, 'a')
        outputFileHandle.write(listLine)
        outputFileHandle.close()
        
        totalMean  += mean 
    
    result = '\n' + 'total mean: ' + str(totalMean/len(scores)) + '\n'
    print result
    logging.info( result  )
    
    if outputFileHandle.closed:
        outputFileHandle = open(filename, 'a')
    outputFileHandle.write(result)
    
    outputFileHandle.close()
    print 'written to file ' + filename 
    
    

    
if __name__ == '__main__':
    doit(sys.argv)
