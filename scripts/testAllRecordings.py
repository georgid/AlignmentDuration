'''
Created on Jan 27, 2016
@deprecated: 
@author: joro
'''
import sys
import os
import json
import subprocess
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

import compmusic
from compmusic import dunya
from align.LyricsAligner import alignRecording, constructSymbTrTxtURI
from align.MakamScore import printMakamScore
dunya.set_token('69ed3d824c4c41f59f0bc853f696a7dd80707779')

from compmusic.extractors.makam.lyricsalignLocal import recMBIDs, recordingDirs



def doitAllRecordings():
     
    
                 
     
     
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
        
        # get sectionLink from derived on kora
        sectionLinkFilename = recMBID + '-scorealign-0.2-sectionlinks-1.json'
        sectionAnnosSourceURI = compositionPath + recordingDir + '/' +  sectionLinkFilename
        if not os.path.isfile(sectionAnnosSourceURI):
           downloadSectionLink(recMBID, recordingDir, compositionPath, sectionLinkFilename)
        
        # get pitch from derived on  kora
        fileName = recMBID + '-makampitch-0.6-pitch-1.json'
        extractedPitchListFile = compositionPath + recordingDir + '/' +  fileName
        if not os.path.isfile(extractedPitchListFile):
            downloadPitch(recMBID, recordingDir, compositionPath, fileName)

        with open(extractedPitchListFile) as f:
            extractedPitchList = json.load(f)
        
        outputDir = 'output'
        totalDetectedTokenList = alignRecording(symbtrtxtURI, sectionMetadataURI, sectionAnnosSourceURI, audioFileURI, extractedPitchList, outputDir)
        
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