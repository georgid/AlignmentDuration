'''
Created on Nov 28, 2014

@author: joro
@deprecated: 
'''


import sys
from Parameters import Parameters
import os
import glob
import logging
from thrash.doitOneChunk import alignOneChunk, HMM_LIST_URI, MODEL_URI, ANNOTATION_EXT, getSectionNumberFromName, alignDependingOnWithDuration,\
    AUDIO_EXT
from Utilz import getMeanAndStDevError, getMelodicStructFromName, findFileByExtensions
from genericpath import isfile
from Decoder import logger
import SectionLink




parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
# parser of htk-build speech models_makam
pathHtkModelParser = os.path.join(parentDir, 'pathHtkModelParser')
sys.path.append(pathHtkModelParser)
from htk_converter import HtkConverter

pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )

#  evaluation  
pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
sys.path.append(pathEvaluation)


def doitOneRecording(argv):
    '''
    for a list of recordings, select those which name contains pattern and evluate total error 
    ''' 
    if len(argv) != 9 and  len(argv) != 10 :
            print ("usage: {}  <pathToComposition>  <pathToRecording> <pattern> <withDuration=True/False> <withSynthesis> <ALPHA>  <ONLY_MIDDLE_STATE> <evalLevel> <usePersistentFiles=True> ".format(argv[0]) )
            sys.exit();
    
    os.chdir(argv[2])
    
    
        
# get annot files with starting pattern
    pattern = argv[3] + '*'   + AUDIO_EXT
    listAudioFilesAll = glob.glob(pattern) 
        

    for i in range(len(listAudioFilesAll)) :
        listAudioFilesAll[i] = os.path.join(argv[2], listAudioFilesAll[i])
        
#     listAudioFiles = []
#         if not isfile( os.path.splitext(listAudioFilesAll[i])[0] +  ".notUsed"):
#             listAudioFiles.append(listAudioFilesAll[i])
    listAudioFiles = listAudioFilesAll
    
    for file in listAudioFiles:
        logger.debug(file)
        
    pathToComposition  = argv[1]
    withDuration = argv[4]
    if withDuration=='True':
        withDuration = True
    elif withDuration=='False':
        withDuration = False
    else: 
        sys.exit("withDuration can be only True or False")  
    
    withSynthesis = argv[5]
    if withSynthesis=='True':
        withSynthesis = True
    elif withSynthesis=='False':
        withSynthesis = False
    else: 
        sys.exit("withSynthesis can be only True or False")  

    
        
    ALPHA = float(argv[6])
    
     
    ONLY_MIDDLE_STATE = argv[7]
    
    params = Parameters(ALPHA, ONLY_MIDDLE_STATE)
    
    evalLevel = int(argv[8])
    
    usePersistentFiles = 'True'
    if len(argv) == 10:
        usePersistentFiles =  argv[9]
        
         
    totalErrors = []
    
    totalCorrectDurationsReference = 0
    totalCorrectDurations = 0
    
    totalDurations = 0
    
    
#     htkParser = None
#     if withDuration:
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    # create dict of (melodicStruct,lyricStruct)
    
    
    secMetadataName =  findFileByExtensions(pathToComposition, ['sectionsMetadata.json']) 
    URIsecMetadata = os.path.join(pathToComposition, secMetadataName[0])
    groups = loadSectionMetadata(URIsecMetadata)
    
    
    for  URI_annotation in listAudioFiles :
            URIrecordingNoExt  = os.path.splitext(URI_annotation)[0]
            logger.info("PROCESSING {}".format(URIrecordingNoExt) )
            
#             whichSection = getSectionNumberFromName(URIrecordingNoExt) 
            melodicStruct, dummy = getMelodicStructFromName(URIrecordingNoExt)
            probabaleSections = getProbableLyrics(groups, melodicStruct)
            if probabaleSections == 0:
                return
            maxPhiScore = float('-inf')
            
            
            for probabaleSection in probabaleSections:
                whichSection = probabaleSection[2]
                currAlignmentErrors,  currCorrectDuration, currTotalDuration, currCorrectDurationRef, currMaxPhiScore = alignDependingOnWithDuration(URIrecordingNoExt, whichSection, pathToComposition, withDuration, withSynthesis, evalLevel, params, usePersistentFiles, htkParser)
                logger.warning("score {} for probable section {} ".format(currMaxPhiScore, probabaleSection))
                
                if currMaxPhiScore > maxPhiScore:
                    maxPhiScore = currMaxPhiScore
                    maxSection = probabaleSection
            logger.info('maxSection for {} is {} '.format(URIrecordingNoExt, maxSection) )

def loadSectionMetadata(URIsecMetadata):
    import json
    with open(URIsecMetadata) as jsonFile:
        sectionMetadata =json.load(jsonFile)

    sections = sectionMetadata['sections']
    groups = {}
    for idx, section in enumerate(sections):
        if section['name'] != 'VOCAL_SECTION':
            continue

        sectionName = section['melodicStructure'] 
        lyricsStruct = section['lyricStructure']
        if sectionName[0] not in groups: # start a new group
            groups[sectionName[0]] = [(sectionName, lyricsStruct, idx)]
        else:
            if not existsInGroup(groups, section): # same melody and lyrics
                sectionsWithThisName = groups[sectionName[0]]
                sectionsWithThisName.append((sectionName, lyricsStruct, idx))
    return groups
    

def existsInGroup(groups, section):
    sectionName = section['melodicStructure']
    lyricsStruct = section['lyricStructure']
    sectionsInGroup = groups[sectionName[0]]
    for sectionInGr in sectionsInGroup:
        if sectionInGr[0] == sectionName and \
            sectionInGr[1] == lyricsStruct:
                return 1
    return 0


def getProbableLyrics(groups, sectionNameQuery):
    if sectionNameQuery[0] not in groups:
        print "section not in metadata"
        return
    
    sections = groups[sectionNameQuery[0]]
    if len(sections) == 1:
        return 0
    return groups[sectionNameQuery[0]]



if __name__ == '__main__':
    doitOneRecording(sys.argv)
    
