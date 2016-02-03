'''
Created on Jan 27, 2016

@author: joro
'''
import sys
import os
import json
import subprocess
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import compmusic
from compmusic import dunya
from align.LyricsAligner import alignRecording, constructSymbTrTxtURI,\
    downloadSymbTr
from align.MakamScore import printMakamScore
dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')

recMBIDs = [ 
                                 'b49c633c-5059-4658-a6e0-9f84a1ffb08b',
#                  'feda89e3-a50d-4ff8-87d4-c1e531cc1233',
                'dd536d18-aa84-451c-b7e5-d97271300b8c',
#                  '9c26ff74-8541-4282-8a6e-5ba9aa5cc8a1',
#                  'bd1758b6-297b-47fe-97b7-bf5d94f23049',
                 '43745ff1-0848-4592-b1ad-9e7b172b0ebd',
                 '727cff89-392f-4d15-926d-63b2697d7f3f',
                 'f5a89c06-d9bc-4425-a8e6-0f44f7c108ef',
#                  '567b6a3c-0f08-42f8-b844-e9affdc9d215',
                 '338e24ba-1f19-49a1-ad6a-2b89e0e09c38',
#                  '8c7eccf5-0d9e-4f33-89f0-87e95b7da970',
#                  '1701ceba-bd5a-477e-b883-5dacac67da43'
                 ]





def doitAllRecordings():
     
    
                 
                 

     recordingDirs =  [ 
                                          '2-15_Nihavend_Aksak_Sarki',
#                       'Melihat_Gulses',
                    '05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var',
#                                             'Sakin--Gec--Kalma', 
#                       '21_Recep_Birgit_-_Olmaz_Ilac_Sine-i_Sad_Pareme',
                      '06_Semahat_Ozdenses_-_Aksam_Oldu_Huzunlendim',
                      '18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya',
                      '04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade',
#                       '03_Bekir_Unluataer_-_Kimseye_Etmem_Sikayet_Aglarim_Ben_Halime',
                      'Semahat_Ozdenses'
#                       'Eda_Simsek',
#                       'Nurten_Demirkol'
                    
                      ]  
     
     
     URI_dataset = '/Users/joro/Downloads/turkish-makam-lyrics-2-audio-test-data-synthesis/'
     
     
     for recMBID,  recordingDir in zip(recMBIDs,  recordingDirs ):
        
        rec_data = dunya.makam.get_recording(recMBID )
        if len(rec_data['works']) > 1:
            sys.exit("rec ID {} has more than one work, not implemented.".format(recMBID))
        work = rec_data['works'][0]
        workMBID = work['mbid']
        
        printMakamScore(URI_dataset, workMBID)
        
        
        symbtrtxtURI, symbTrCompositionName  = constructSymbTrTxtURI(URI_dataset, workMBID)
        symbtrtxtURI = downloadSymbTr(workMBID, URI_dataset)
        
        compositionPath = URI_dataset + symbTrCompositionName + '/'
        sectionMetadataURI = compositionPath + symbTrCompositionName + '.sectionsMetadata.json'
        
        audioFileURI =  compositionPath + recordingDir + '/' + recordingDir + '.wav'
        
        # get sectionLink
        sectionLinkFilename = recMBID + '-scorealign-0.2-sectionlinks-1.json'
        sectionLinksURI = compositionPath + recordingDir + '/' +  sectionLinkFilename
        if not os.path.isfile(sectionLinksURI):
           downloadSectionLink(recMBID, recordingDir, compositionPath, sectionLinkFilename)
        
        # get pitch
        fileName = recMBID + '-makampitch-0.6-pitch-1.json'
        extractedPitchListFile = compositionPath + recordingDir + '/' +  fileName
        if not os.path.isfile(extractedPitchListFile):
            downloadPitch(recMBID, recordingDir, compositionPath, fileName)

        with open(extractedPitchListFile) as f:
            extractedPitchList = json.load(f)
        
        outputDir = 'output'
        totalDetectedTokenList = alignRecording(symbtrtxtURI, sectionMetadataURI, sectionLinksURI, audioFileURI, extractedPitchList, outputDir)
        
        raw_input('press key...')



def downloadSectionLink(recMBID, recordingDir, compositionPath, sectionLinkFilename):
    firstTwoDigits = recMBID[:2]
    sectionLinkKoraURI = '/incoming/Turkey-makam/derived/' + firstTwoDigits + '/' + recMBID + '/scorealign/0.2/' + sectionLinkFilename
    serverPath = 'georgid@kora.s.upf.edu:' + sectionLinkKoraURI
    destination = compositionPath + recordingDir + '/'
    command = 'scp'
    pipe = subprocess.Popen([command, serverPath, destination])
    pipe.wait()


def downloadPitch(recMBID, recordingDir, compositionPath, fileName):
    firstTwoDigits = recMBID[:2]
    extractedPitchListFileKora = '/incoming/Turkey-makam/derived/' + firstTwoDigits + '/' + recMBID + '/initialmakampitch/0.6/' + fileName
        
    serverPath = 'georgid@kora.s.upf.edu:' + extractedPitchListFileKora
    destination = compositionPath + recordingDir + '/'
    command = 'scp'
    pipe = subprocess.Popen([command, serverPath, destination])
    pipe.wait()




if __name__ == '__main__':
    doitAllRecordings()