'''
Created on Jan 13, 2016

@author: joro
'''
import os
import sys
import json
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))




from makam.MakamRecording import MakamRecording, parseSectionLinks
from align.ScoreSection import ScoreSection
from makam.MakamScore import loadMakamScore2

from align.LyricsAligner import LyricsAligner, extendSectionLinksSelectedSections,\
    stereoToMono

currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )


WITH_SECTION_ANNOTATIONS = 1

from align.ParametersAlgo import ParametersAlgo

        
def testLyricsAlign():
    
    # test with section links
    symbtrtxtURI = os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci.txt')
    sectionMetadataURI =  os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci.sectionsMetadata.json' )
    sectionLinksSourceURI = os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya.sectionLinks.json' )
    sectionAnnosSourceURI = os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/727cff89-392f-4d15-926d-63b2697d7f3f.json')
    audioFileURI =  os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya.wav')
    
    # test with section anno and acapella
#     symbtrtxtURI = os.path.join( currDir,'../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi.txt')
#     sectionMetadataURI =  os.path.join( currDir, '../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi.sectionsMetadata.json' )
#     sectionAnnosSourceURI = os.path.join( currDir, '../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/567b6a3c-0f08-42f8-b844-e9affdc9d215.json' )
#     audioFileURI =  os.path.join( currDir, '../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/02_Kimseye.wav')
#     
    
    with open(sectionLinksSourceURI) as f:
            sectionLinksDict = json.load(f)
    with open(sectionMetadataURI) as f2:
            sectionMetadataDict = json.load(f2)


    outputDir =  os.path.join( currDir, '../example/output/' )
    
    
    
    ###  for Juanjos pitch
#     extractedPitch = os.path.splitext(audioFileURI)[0] + '.pitch'
#     with open(extractedPitch) as f:
#         extractedPitchList = json.load(f)
    extractedPitchList = None
    
    if WITH_SECTION_ANNOTATIONS:
        
        with open(sectionAnnosSourceURI) as f:
            sectionLinksDict = json.load(f)
    
    
    audioFileURI = stereoToMono(audioFileURI)               


    la = LyricsAligner(ParametersAlgo.PATH_TO_HCOPY)
    
    totalDetectedTokenList, sectionLinksDict = la.alignRecording(symbtrtxtURI, sectionMetadataDict, sectionLinksDict, audioFileURI, extractedPitchList, outputDir, WITH_SECTION_ANNOTATIONS)
      
    ret = {'alignedLyricsSyllables':{}, 'sectionlinks':{} }
    ret['alignedLyricsSyllables'] = totalDetectedTokenList
    ret['sectionlinks'] = sectionLinksDict
    print ret



    

def testExtendSectionLinksSelectedSections():
    '''
    test if extending a sections Links file works well
    extendSectionLinksSelectedSections(sectionLinksDict, sectionLinks)
    '''
    sectionLinks = parseSectionLinks(sectionLinksDict)
  
    makamScore = loadMakamScore2(symbtrtxtURI, sectionMetadataDict )
    
    # changes one test section link as if it were aligned 
    testSectionLink = sectionLinks[1]
    probabaleSections = makamScore.getProbableSectionsForMelodicStructure(testSectionLink)
    selectedSection = ScoreSection('blah', 1, 20, 'B2', 'B1')
    selectedSectionsSameLyrics =  makamScore.getSectionsSameLyrics( selectedSection, probabaleSections)
    testSectionLink.setSelectedSections(selectedSectionsSameLyrics)
    
    extendSectionLinksSelectedSections(sectionLinksDict, sectionLinks)
    print sectionLinksDict
    

def testMakamRecording():
    makamScore = loadMakamScore2(symbtrtxtURI, sectionMetadataDict)
    
    with open(sectionAnnosSourceURI) as f:
        sectionLinksDict = json.load(f)
    
    mr = MakamRecording(makamScore, sectionLinksDict, sectionAnnosDict )
    

# def testDecoding():
#     
#     lyricsWithModels = LyricsWithModels(lyrics, htkParser,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
#     decoder = Decoder(lyricsWithModels, URIRecordingChunkResynthesizedNoExt, alpha)



if __name__ == '__main__':
    testLyricsAlign()
#     testLyricsAlignOracle()
#     testExtendSectionLinksSelectedSections()
#     testMakamRecording()