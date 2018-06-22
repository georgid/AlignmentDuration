
# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/


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
     
    
                 
     
     
     URI_dataset = '/Users/joro/Downloads/turkish-for_makam-lyrics-2-audio-test-data-synthesis/'
     
     
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
    sectionLinkKoraURI = '/incoming/Turkey-for_makam/derived/' + firstTwoDigits + '/' + recMBID + '/scorealign/0.2/' + sectionLinkFilename
    serverPath = 'georgid@kora.s.upf.edu:' + sectionLinkKoraURI
    destination = compositionPath + recordingDir + '/'
    command = 'scp'
    pipe = subprocess.Popen([command, serverPath, destination])
    pipe.wait()


def downloadPitch(recMBID, recordingDir, compositionPath, fileName):
    firstTwoDigits = recMBID[:2]
    extractedPitchListFileKora = '/incoming/Turkey-for_makam/derived/' + firstTwoDigits + '/' + recMBID + '/initialmakampitch/0.6/' + fileName
        
    serverPath = 'georgid@kora.s.upf.edu:' + extractedPitchListFileKora
    destination = compositionPath + recordingDir + '/'
    command = 'scp'
    pipe = subprocess.Popen([command, serverPath, destination])
    pipe.wait()




if __name__ == '__main__':
    doitAllRecordings()