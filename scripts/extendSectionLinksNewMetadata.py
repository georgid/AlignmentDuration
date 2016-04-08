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
from scripts.fetchSymbTrFromGithub10SarkiTestDataset import fetchFileFromURL
# from align.RecordingSegmenter import getURISectionAnnotation

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir, os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'pycompmusic') 
if pathUtils not in sys.path:
    sys.path.append(pathUtils)

import compmusic    
from compmusic import dunya
from compmusic.extractors.makam.lyricsalignNoteOnsets import recMBIDs
# from align.MakamRecordingOld import MakamRecordingOld

from utilsLyrics.Utilz import  findFileByExtensions
'''
1. take section annotaitons with old section names from annotations for ISTANBUL. match with old section_metadata using MakamRecording to create pointers to sections
2. take section metadaata with new names from dunya. 
3. prove that number of new metadata section names is consistent with number of old section names
4. replace pointers to sections with new section names (if section annotaions from sertan's jnmr dataset present take it else take section annotations from ISTANBUL )
 
'''
pathSectionAnnosSourceJNMR = '/Users/joro/Downloads/turkish_makam_section_dataset-2014_jnmr/audio_metadata/'


URI_datasetOld = '/Users/joro/Downloads/turkish-makam-lyrics-2-audio-test-data-synthesis/'



dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")










def extendNewMetadata(musicbrainzid, inpuRecordingDir, pathDestinationDataset):
    '''
    annotations with score sections names zemin meyan > convert to > annotations with sections names C1, B1. etc
    uses old makamScore and makamRecording (and SymbTrParser old ) because we need the matchSections and its neater to use it form the constructor of MakamRecording
    '''
    
    
    rec_data = dunya.makam.get_recording(musicbrainzid )
    w = rec_data['works'][0]

    symbtrtxtURI, symbTrCompositionName  = constructSymbTrTxtURI(URI_datasetOld, w['mbid'])
    sectionsMetadataNewLabels, sectionsMetadata = getSectionsMetadata(w, symbTrCompositionName)



    
    ###### 1. load old score section metadata with meyan etc. names and section annotation in json 
    compositionPath = URI_datasetOld + symbTrCompositionName + '/'
    makamScore = loadMakamScore(compositionPath)
#     makamScore.printSectionsAndLyrics()
    
    if len(sectionsMetadata) != len(makamScore.sectionToLyricsMap):
        sys.exit("for composition {} text score sections are {} and sectionsMetadata with new labels are {}".format(compositionPath, len(makamScore.sectionToLyricsMap), len(sectionsMetadata)))

    ###### match score sections to audio annotations (in constructor of makam recording)
    pathToAudioFile = 'blah'
    pathToRecording, pathToSectionAnnotations = getURISectionAnnotation(inpuRecordingDir, compositionPath) 
    makamRecording = MakamRecordingOld(makamScore, pathToAudioFile, pathToSectionAnnotations)
    print makamRecording.sectionIndices
    
    
        ########   load  section annos from source
    sectionAnnosSourceURI = pathSectionAnnosSourceJNMR + musicbrainzid + '.json'
    if not os.path.isfile(sectionAnnosSourceURI):
        print 'no section annotaion in JNMR dataset. all fields in final json except for field section_annotaitons will be empty'
        sectionAnnosDict = {}
        sections = replaceSecionsWithNewLabels_GeorgisAnnotations(sectionsMetadataNewLabels, makamRecording)
    else:
        with open(sectionAnnosSourceURI) as f:
             sectionAnnosDict = json.load(f)
        sections = replaceSectionsWIthNewLabesJNMR(sectionsMetadataNewLabels, sectionAnnosSourceURI, sectionAnnosDict, pathToSectionAnnotations, makamRecording)

                 
        
    
    
    
    sectionAnnosDict['section_annotations'] = sections
    
    
    
    
    ##### write edited sectionAnnos
    sectionAnnosURIEdited = pathDestinationDataset + '/' + musicbrainzid  + '.json'
    print "wirting file \n" + sectionAnnosURIEdited
    with open(sectionAnnosURIEdited, 'w') as f8:
        json.dump( sectionAnnosDict, f8, indent=4)

    
    
def replaceSectionsWIthNewLabesJNMR(scoreSectionsNewLables, sectionAnnosSourceURI, sectionAnnosDict, pathToSectionAnnotations, makamRecording):
    '''
    extend sectionsAnnos with JNMR
    '''
    if 'section_annotations' not in sectionAnnosDict:
                     sys.exit('annotation should have key section_annotations')
    sectionsAnnos = sectionAnnosDict['section_annotations']
    
    # sanity check
    if len(sectionsAnnos) != len(makamRecording.sectionIndices):
        sys.exit(" annotation local in \n {} \n has length  {} whereas annotation json \n {} \n . Rewrite code with only json".format(pathToSectionAnnotations, len(makamRecording.sectionIndices), sectionAnnosSourceURI ))
    
    for sectionAnnoTxt, sectionIdx in zip(sectionsAnnos, makamRecording.sectionIndices):
        if sectionIdx != -1:
            if sectionIdx > len(scoreSectionsNewLables): # done for        '06_Semahat_Ozdenses_-_Aksam_Oldu_Huzunlendim',
                sys.exit('more sectionsAnnos matched that they are in sectiona metadata')
            melStruct = scoreSectionsNewLables[sectionIdx].melodicStructure
            lyricStruct = scoreSectionsNewLables[sectionIdx].lyricStructure
        else:
            melStruct = ''
            lyricStruct = ''
        sectionAnnoTxt['melodicStructure'] = melStruct
        sectionAnnoTxt['lyricStructure'] = lyricStruct
    
    return sectionsAnnos
 
 

def getSectionsMetadata(w, symbTrCompositionName):
    ###### 2. load score sections metadata new C1,C2 etc.
    sectionMetadataAll = dunya.docserver.get_document_as_json(w['mbid'], "metadata", "metadata", 1, version="0.1") #     print sectionMetadataAll
    if w['mbid'] == 'c6e43ac6-4a18-42ab-bcc4-46e29360051e':
        
        symbTrMetadataURL = 'https://raw.githubusercontent.com/sertansenturk/turkish_makam_corpus_stats/master/data/SymbTrData/' + symbTrCompositionName + '.json'
        print symbTrMetadataURL
        import tempfile
        tmpDir = tempfile.mkdtemp()
        fetchFileFromURL(symbTrMetadataURL, tmpDir + '/tmp.json') 
        with open(tmpDir + '/tmp.json') as f:
             sectionMetadataAll = json.load(f)
             
    sectionsMetadata = sectionMetadataAll['sections']
    scoreSections = []
    for section in sectionsMetadata:
#                     print section
        sectionNew = ScoreSection(section['name'], int(section['startNote']), int(section['endNote']), section['melodicStructure'], section['lyricStructure'])
        scoreSections.append(sectionNew)
    
    return scoreSections, sectionsMetadata
   
    
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


def replaceSecionsWithNewLabels_GeorgisAnnotations(sectionsMetadataNewLabels, makamRecording):
    # if no section annos in pathSectionAnnosSourceJNMR. because for some recordings there are no annotations in JNMR dataset
    sections = []
    for i, idx in enumerate(makamRecording.sectionIndices):
        currSection = {}
        currSection['time'] = [makamRecording.beginTs[i], makamRecording.endTs[i]]
        currSection['time_unit'] = 'sec'
        currSection['name'] = makamRecording.sectionNamesSequence[i]
        if idx != -1:
            melStruct = sectionsMetadataNewLabels[idx].melodicStructure
            lyrStruct = sectionsMetadataNewLabels[idx].lyricStructure
        else:
            melStruct = ''
            lyrStruct = ''
        currSection['melodicStructure'] = melStruct
        currSection['lyricStructure'] = lyrStruct
        sections.append(currSection)
    
    return sections


if __name__ == '__main__':
    
    pathSectionAnnosDestination = '/Users/joro/Documents/Phd/UPF/turkish_makam_section_dataset/audio_metadata/'
    

    for musicbrainzid in recMBIDs:
        recordingDir = recMBIDs[musicbrainzid]
        extendNewMetadata(musicbrainzid, recordingDir, pathSectionAnnosDestination )
        raw_input("press for next piece...")