'''
Created on Feb 11, 2016

@author: joro
'''
import json
import sys
from align.ScoreSection import ScoreSection
from align.MakamRecordingOld import MakamRecordingOld
from scripts.MakamScoreOld import loadMakamScore
import os
# from align.RecordingSegmenter import getURISectionAnnotation

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir, os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'pycompmusic') 
if pathUtils not in sys.path:
    sys.path.append(pathUtils)

import compmusic    
from compmusic import dunya
from compmusic.extractors.makam.lyricsalignLocal import recMBIDs, recordingDirs
# from align.MakamRecordingOld import MakamRecordingOld

from utilsLyrics.Utilz import  findFileByExtensions

pathSectionAnnosSource = '/Users/joro/Downloads/turkish_makam_section_dataset-2014_jnmr/audio_metadata/'


URI_datasetOld = '/Users/joro/Downloads/turkish-makam-lyrics-2-audio-test-data-synthesis/'



dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")



def extendNewMetadata(musicbrainzid, inpuRecordingDir, pathDestinationDataset):
    '''
    annotations with score sections names zemin meyan > convert to > annotations with sections names C1, B1. etc
    uses old makamScore and makamRecording (and SymbTrParser old ) because we need the matchSections and its neater to use it form the constructor of MakamRecording
    '''
    
    rec_data = dunya.makam.get_recording(musicbrainzid )
    w = rec_data['works'][0]

    
    ###### 1. load sections with meyan etc. names and section annotation in json and match
    symbtrtxtURI, symbTrCompositionName  = constructSymbTrTxtURI(URI_datasetOld, w['mbid'])
    compositionPath = URI_datasetOld + symbTrCompositionName + '/'
    makamScore = loadMakamScore(compositionPath)
    makamScore.printSectionsAndLyrics()
    pathToAudioFile = 'blah'
    
    
    pathToRecording, pathToSectionAnnotations = getURISectionAnnotation(inpuRecordingDir, compositionPath) 
    makamRecording = MakamRecordingOld(makamScore, pathToAudioFile, pathToSectionAnnotations)
    print makamRecording.sectionIndices
    
    
    ###### 2. load score sections metadata new C1,C2 etc.
    sectionMetadata = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1, version="0.1")
#     print sectionMetadata
    
    scoreSectionAnnos = sectionMetadata['sections']
    if len(scoreSectionAnnos) != len(makamScore.sectionToLyricsMap):
        sys.exit("text score sections with len {} and scoreSectionAnnos with len {}".format(len(makamScore.sectionToLyricsMap), len(scoreSectionAnnos) ) ) 
    
    scoreSections = []
    for section in scoreSectionAnnos:
                    print section
                    sectionNew = ScoreSection(section['name'],  int(section['startNote']), int(section['endNote']), section['melodicStructure'], section['lyricStructure']) 
                    scoreSections.append(sectionNew)
    
    ######### 3.  old format section annos in json
#     sectionAnnosSourceURI = pathSectionAnnosSource + musicbrainzid + '.json'
#     with open(sectionAnnosSourceURI) as f:
#         sectionAnnosDict = json.load(f)
#     if 'section_annotations' not in sectionAnnosDict:
#                 sys.exit('annotation should have key section_annotations')
#                 
#     sectionAnnosJson = sectionAnnosDict['section_annotations']
#     if len(sectionAnnosJson) != len(makamRecording.sectionIndices):
#         sys.exit(" annotation local in \n {} \n has length  {} whereas annotation json \n {} \n has length {}. Rewrite code with only json".format(pathToSectionAnnotations, len(makamRecording.sectionIndices), sectionAnnosSourceURI, len(sectionAnnosJson)))
#     
#     for sectionAnnoTxt, sectionIdx in zip(sectionAnnosJson, makamRecording.sectionIndices):
#         if sectionIdx != -1:  
#             if sectionIdx > len(scoreSections): # done for        '06_Semahat_Ozdenses_-_Aksam_Oldu_Huzunlendim',
#                 sys.exit('more sections matched that they are in sectiona metadata' )
#             melStruct = scoreSections[sectionIdx].melodicStructure
#             lyricStruct =   scoreSections[sectionIdx].lyricStructure
#         
#         else:
#             melStruct = ''
#             lyricStruct = ''
#         sectionAnnoTxt['melodicStructure'] = melStruct
#         sectionAnnoTxt['lyricStructure'] = lyricStruct
#         
#     sectionAnnosDict['section_annotations'] = sectionAnnosJson
        
    # if no section annos in pathSectionAnnosSource:
    sections = []
    for i, idx in enumerate(makamRecording.sectionIndices):
        currSection = {}
        currSection['time'] = [makamRecording.beginTs[i], makamRecording.endTs[i]]
        currSection['time_unit'] = 'sec'
        currSection['name'] = makamRecording.sectionNamesSequence[i]
        if idx != -1: 
            melStruct = scoreSections[idx].melodicStructure
            lyrStruct = scoreSections[idx].lyricStructure
        else:
            melStruct = ''
            lyrStruct = ''
        currSection['melodicStructure'] = melStruct
        currSection['lyricStructure'] = lyrStruct
        sections.append(currSection)
    sectionAnnosDict = {}
    sectionAnnosDict['section_annotations'] = sections
    
    sectionAnnosURIEdited = pathDestinationDataset + musicbrainzid + '/' + musicbrainzid  + '.json'
    print "wirting file \n" + sectionAnnosURIEdited
    # write edited sectionAnnos
    with open(sectionAnnosURIEdited, 'w') as f8:
        json.dump( sectionAnnosDict, f8, indent=4)
    
    
def constructSymbTrTxtURI(URI_dataset, workMBID):
    '''
    URI on local machine of symbTr queried by workMBID 
    '''
    symbtr = compmusic.dunya.makam.get_symbtr(workMBID)
    symbTrCompositionName = symbtr['name']
    
    compositionPath = URI_dataset + symbTrCompositionName + '/'
    symbtrtxtURI = compositionPath + symbTrCompositionName + '.txt'
    
    return symbtrtxtURI,  symbTrCompositionName


def getURISectionAnnotation(recordingDir, pathToComposition):
    pathToRecording = os.path.join(pathToComposition, recordingDir)
    os.chdir(pathToRecording)
#         pathToSectionAnnotations = os.path.join(pathToRecording, glob.glob('*.sectionAnno.txt')[0]) #             pathToAudio =  os.path.join(pathToRecording, glob.glob('*.wav')[0])
    listExtensions = ["sectionAnno.json", "sectionAnno.txt", "sectionAnno.tsv"]
    sectionAnnoFiles = findFileByExtensions(pathToRecording, listExtensions)
    pathToSectionAnnotations = os.path.join(pathToRecording, sectionAnnoFiles[0])
    return pathToRecording, pathToSectionAnnotations


if __name__ == '__main__':
    
    pathDestinationDataset = '/Users/joro/Downloads/ISTANBULSymbTr2/'

    for musicbrainzid, recordingDir in zip(recMBIDs, recordingDirs):
         extendNewMetadata(musicbrainzid, recordingDir, pathDestinationDataset )
         raw_input("press for next piece...")