'''
Created on Dec 8, 2014

@author: joro
'''


import sys
from doitOneRecording import doitOneRecording
from datetime import datetime
import os
from Decoder import logger
from Utilz import getMeanAndStDevError

def doit(argv):
    if len(argv) != 6 and len(argv) != 7:
        print ("usage: {}  <pathToCompositions>  <pathToRecordings> <withDurations> <ALPHA> <ONLY_MIDDLE_STATE> <usePersistentFiles=True>".format(argv[0]) )
        sys.exit();

    pathToScores = argv[1]

    path_testFile  = argv[2]
    
    withDuration = argv[3]
    ALPHA = argv[4]
    
    
    ONLY_MIDDLE_STATE = argv[5]
    evalLevel = 2
    
    usePersistentFiles = 'True'
        
    if len(argv) == 7:
        usePersistentFiles = argv[6]
    
    compositionNames = ['nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi', \
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
#      take only unique 
    
    ############################# doit for a list of recordings: MALE  ###############################        
    
    

    
    compositionNames = [ 
                            'nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi', 
                        'nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin',
                        'ussak--sarki--aksak--bu_aksam_gun--tatyos_efendi', 
                        'segah--sarki--curcuna--olmaz_ilac--haci_arif_bey',
                                'ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses',
                            'nihavent--sarki--aksak--gel_guzelim--faiz_kapanci',
                                'nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey',
                                'nihavent--sarki--aksak--koklasam_saclarini--artaki_candan',
                        'nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi'
                    
                    ]
    
    recordingDirs =  [  'Melihat_Gulses',
                      '05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var',
                                            'Sakin--Gec--Kalma', 
                      '21_Recep_Birgit_-_Olmaz_Ilac_Sine-i_Sad_Pareme',
                      '06_Semahat_Ozdenses_-_Aksam_Oldu_Huzunlendim',
                      '18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya',
                      '04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade',
                      '2-15_Nihavend_Aksak_Sarki',
                      '03_Bekir_Unluataer_-_Kimseye_Etmem_Sikayet_Aglarim_Ben_Halime'
                    
                      ]                          
                     
                            
        
                  


    
    currTime = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')    
    filename = os.path.join(os.getcwdu(),   'alignError_' + currTime + '.out') 
    outputFileHandle = open(filename, 'a')
    
    logger.info("\n Output file is: " + filename )
    
    
    outputFileHandle.write('\n'  + str(ALPHA) )
    totalErrors  = [] 
    
       #############################
#     for a-capella ISTANBUL data 
    subpaths = ['/idil/', '/idil/', '/idil/', '/guelen/', '/guelen/', '/barbaros/',  '/safiye/','/barbaros/','/goekhan/'    ]
    patterns = [  'Melihat_Gulses', '05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var',  'Sakin--Gec--Kalma', '01_Olmaz', '01_Aksam',  '02_Gel', '01_Bakmiyor', '02_Koklasam','02_Kimseye']

#     for compositionName, recordingDir in zip(compositionNames, recordingDirs):
    
    for i in range(len(compositionNames)):
         
         
        URI_Composition = pathToScores + compositionNames[i]
        URI_Recording = path_testFile + subpaths[i]
        pattern  = patterns[i]
        pattern = pattern + '_'

#     for synthesis data 

#         URI_Composition = os.path.join(pathToScores, compositionName)
#         URI_Recording =  os.path.join(URI_Composition, recordingDir)
#         pattern = recordingDir + '_'
# end of synthesis data

        command = [ 'python', '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/doitOneRecording.py', URI_Composition, URI_Recording, pattern, withDuration, str(ALPHA), ONLY_MIDDLE_STATE, str(evalLevel), usePersistentFiles]
        commandStr = " ".join(command)
        logger.info("{} ".format(commandStr ))
        
        continue
        mean, stDev, errorsForRecording  = doitOneRecording([ 'dummy', URI_Composition, URI_Recording, pattern, withDuration, ALPHA, ONLY_MIDDLE_STATE, evalLevel, usePersistentFiles])
        totalErrors.extend(errorsForRecording)
        

        
        listLine = '\n' + URI_Recording + " " + pattern + " " + str(mean) +   " " + str(stDev) 
        
        if outputFileHandle.closed:
            outputFileHandle = open(filename, 'a')
        outputFileHandle.write(listLine)
        outputFileHandle.close()
        
        
    mean, stDev, median  = getMeanAndStDevError(totalErrors)
    result = '\n' + 'total mean: ' + str(mean) + '\n'
    
    logger.info( result  )
    
    if outputFileHandle.closed:
        outputFileHandle = open(filename, 'a')
    outputFileHandle.write(result)
    
    outputFileHandle.close()
    print 'written to file ' + filename 
    
    

    
if __name__ == '__main__':
    doit(sys.argv)
