from align.FeatureExtractor import FeatureExtractor

# Copyright 2015,2016 Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of Dunya
#
# Dunya is free software: you can redistribute it and/or modify it under the
# terms of the GNU Affero General Public License as published by the Free Software
# Foundation (FSF), either version 3 of the License, or (at your option) any later
# version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A
# PARTICULAR PURPOSE.  See the GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along with
# this program.  If not, see http://www.gnu.org/licenses/

# Lyrics-to-audio alignment with syllable duration modeling
""" please cite:
Dzhambazov, G., & Serra X. (2015).  Modeling of Phoneme Durations for Alignment between Polyphonic Audio and Lyrics.
Sound and Music Computing Conference 2015.
"""

import os
import sys
import json
import subprocess
from align.MakamRecording import parseSectionLinks, MakamRecording
from align.Decoder import logger, DETECTION_TOKEN_LEVEL, WITH_DURATIONS, Decoder
from hmm.ParametersAlgo import ParametersAlgo
from parse.TextGrid_Parsing import tierAliases
from align.LyricsParsing import parsePhonemes, getOnsetsFromPhonemeAnnos
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 
# pathPycompmusic = os.path.join(parentDir, 'pycompmusic')
# if pathPycompmusic not in sys.path:
#     sys.path.append(pathPycompmusic)





import compmusic.extractors
from compmusic import dunya
from compmusic.dunya import makam

import essentia.standard

currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )
modelDIR = currDir + '/model/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

from MakamScore import  loadMakamScore2
from hmm.examples.main import loadSmallAudioFragment,\
    loadSmallAudioFragmentOracle


from utilsLyrics.Utilz import writeListOfListToTextFile, writeListToTextFile,\
    getMeanAndStDevError, getSectionNumberFromName, readListOfListTextFile, \
    readListTextFile, getMelodicStructFromName, tokenList2TabFile,  fetchFileFromURL

from htkparser.htk_converter import HtkConverter
ANNOTATION_EXT = '.TextGrid'
 
        




def createNameChunk(recordingNoExtURI, beginTs, endTs):
    URIRecordingChunkResynthesizedNoExt = recordingNoExtURI + "_" + "{}".format(beginTs) + '_' + "{}".format(endTs)
    return URIRecordingChunkResynthesizedNoExt

def alignRecording( symbtrtxtURI, sectionMetadataDict, sectionLinksDict, audioFileURI, extractedPitchList, outputDir, WITH_SECTION_ANNOTATIONS):

        # parameters 
        usePersistentFiles = True
        if WITH_SECTION_ANNOTATIONS and sectionLinksDict == None:
            
            sys.exit("specified to work with section annotation for file {} , but it is not provided.  ".format(audioFileURI))

        mr,  htkParser = loadMakamRecording(symbtrtxtURI, sectionMetadataDict, sectionLinksDict, audioFileURI, WITH_SECTION_ANNOTATIONS)
        tokenLevelAlignedSuffix = determineSuffix(WITH_DURATIONS, ParametersAlgo.WITH_ORACLE_PHONEMES, ParametersAlgo.WITH_ORACLE_ONSETS, DETECTION_TOKEN_LEVEL)
    
    
        totalDetectedTokenList = []
        
        totalCorrectDurations = 0
        totalDurations = 0
    
        recordingNoExtURI = os.path.splitext(audioFileURI)[0]    
        
        if not WITH_SECTION_ANNOTATIONS: 
        
            for  currSectionLink in mr.sectionLinks :
                if currSectionLink.melodicStructure.startswith('ARANAGME'):
                    print("skipping sectionLink {} with no lyrics ...".format(currSectionLink.melodicStructure))
                    continue
                
                detectedTokenList = alignSectionLinkProbableSections(mr.makamScore, extractedPitchList, ParametersAlgo.POLYPHONIC, usePersistentFiles, tokenLevelAlignedSuffix,  recordingNoExtURI, currSectionLink, htkParser) 
    #DEBUG           
    #             print "query melodic structure: {}".format(currSectionLink.melodicStructure)
    #             for sectin in currSectionLink.selectedSections:
    #                 print "result sections: {}".format(sectin)
                
                totalDetectedTokenList.extend(detectedTokenList)
            # sectionLinks- list of objects of class sectionLink with the field selectedSections set after slignment
            sectionLinksDict = extendSectionLinksSelectedSections(sectionLinksDict, mr.sectionLinks)
            
            return totalDetectedTokenList, sectionLinksDict        
        
        else: # with Annotations
            
            for  currSectionAnno in mr.sectionAnnos :
                if currSectionAnno.melodicStructure.startswith('ARANAGME'):
                    print("skipping sectionLink {} with no lyrics ...".format(currSectionAnno.melodicStructure))
                    continue            
                if not hasattr(currSectionAnno, 'scoreSection'):
                    print("skipping sectionAnno {} not matched to any score section ...".format(currSectionAnno))
                    continue   
                
                lyrics = currSectionAnno.scoreSection.lyrics
         
                lyricsStr = lyrics.__str__()
                if not lyricsStr or lyricsStr=='None' or  lyricsStr =='_SAZ_':
                    print("skipping sectionLink {} with no lyrics ...".format(currSectionLink.melodicStructure))
                    continue
                
                URIRecordingChunkResynthesizedNoExt = createNameChunk(recordingNoExtURI, currSectionAnno.beginTs, currSectionAnno.endTs) 
                detectedTokenList, detectedPath, maxPhiScore = alignLyricsSection( lyrics, extractedPitchList,  ParametersAlgo.POLYPHONIC, [],  usePersistentFiles, tokenLevelAlignedSuffix, recordingNoExtURI, URIRecordingChunkResynthesizedNoExt, currSectionAnno, htkParser)
                
#                 break
                correctDuration = 0
                totalDuration = 1
                
                pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
                if pathEvaluation not in sys.path:
                    sys.path.append(pathEvaluation)
     
                from AccuracyEvaluator import _evalAccuracy
                evalLevel = tierAliases.words
                correctDuration, totalDuration = _evalAccuracy(URIRecordingChunkResynthesizedNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, currSectionAnno.beginTs )
    
                totalCorrectDurations += correctDuration
                totalDurations += totalDuration
                
                
                totalDetectedTokenList.extend(detectedTokenList)
            
            accuracy = totalCorrectDurations / totalDurations
            logger.info("accuracy: {:.2f}".format(accuracy))     
            return totalDetectedTokenList, sectionLinksDict
        

def loadMakamRecording(symbtrtxtURI, sectionMetadataDict, sectionLinksDict, audioFileURI,  withAnnotations):
    '''
    refactored method
    '''
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)

    
    makamScore = loadMakamScore2(symbtrtxtURI, sectionMetadataDict)
    mr = MakamRecording(makamScore, sectionLinksDict, withAnnotations)
    
    return mr, htkParser   
    

    
def alignSectionLinkProbableSections(makamScore,extractedPitchList, withSynthesis, oracleLyrics, usePersistentFiles, tokenLevelAlignedSuffix,  recordingNoExtURI, currSectionLink, htkParser):
    '''
    runs alignment on given audio multiple times with a list of probable sections with their corresponding lyrics
    @return detectedTokenList with best score
    @return selectedSection section with this score
    '''   
    maxPhiScore = float('-inf')
    probabaleSections = makamScore.getProbableSectionsForMelodicStructure(currSectionLink)
    for probabaleSection in probabaleSections:
        currTokenLevelAlignedSuffix =  tokenLevelAlignedSuffix + '_' + probabaleSection.melodicStructure + '_' + probabaleSection.lyricStructure
        
        URIRecordingChunkResynthesizedNoExt =  recordingNoExtURI + "_" + str(currSectionLink.beginTs) + '_' + str(currSectionLink.endTs)
        currDetectedTokenList, detectedPath, phiScore = alignLyricsSection( probabaleSection.lyrics, extractedPitchList, withSynthesis, [],  usePersistentFiles, currTokenLevelAlignedSuffix, recordingNoExtURI, URIRecordingChunkResynthesizedNoExt, currSectionLink, htkParser)
        if phiScore > maxPhiScore:
            maxPhiScore = phiScore
            selectedSection = probabaleSection
            detectedTokenList = currDetectedTokenList
    
    # get sections with same lyrics as top-aligned section
    selectedSectionsSameLyrics =  makamScore.getSectionsSameLyrics( selectedSection, probabaleSections)
    currSectionLink.setSelectedSections(selectedSectionsSameLyrics)
    
    return detectedTokenList
         
         
               



def  alignLyricsSection( lyrics, extractedPitchList,  withSynthesis, listNonVocalFragments,   usePersistentFiles, tokenLevelAlignedSuffix,  URIrecordingNoExt, URIRecordingChunkResynthesizedNoExt, currSectionLink, htkParser):
        '''
        align @param: lyrics for one section
        '''
            
    #     read from file result
      
        detectedAlignedfileName = URIRecordingChunkResynthesizedNoExt + tokenLevelAlignedSuffix
        fe = FeatureExtractor() 
        if not os.path.isfile(detectedAlignedfileName):
            
            if  ParametersAlgo.WITH_ORACLE_PHONEMES:
                lyricsWithModelsOracle = loadSmallAudioFragmentOracle(URIRecordingChunkResynthesizedNoExt, htkParser, lyrics )
                # featureVectors is alias for LyricsWithModelsOracle
                fe.featureVectors = lyricsWithModels = lyricsWithModelsOracle 
            else:
            #     ###### extract audio features
                lyricsWithModels, featureVectors, URIrecordingChunk = loadSmallAudioFragment(lyrics, extractedPitchList,   URIrecordingNoExt, URIRecordingChunkResynthesizedNoExt, bool(withSynthesis), currSectionLink, htkParser)
                fe.featureVectors = featureVectors
            
        # DEBUG: score-derived phoneme  durations
            lyricsWithModels.printPhonemeNetwork()
#             lyricsWithModels.printWordsAndStates()
            alpha = 0.97
            decoder = Decoder(lyricsWithModels, URIRecordingChunkResynthesizedNoExt, alpha)
        #  TODO: DEBUG: do not load models
        # decoder = Decoder(lyrics, withModels=False, numStates=86)
        #################### decode
            
            fromTsTextGrid = -1; toTsTextGrid = -1
            if ParametersAlgo.WITH_ORACLE_PHONEMES:
                fromTsTextGrid = 0; toTsTextGrid = 20.88
            
            ##### note onsets
            if ParametersAlgo.WITH_ORACLE_ONSETS == 1:
                URIrecOnsets = URIrecordingNoExt + '.alignedNotes.txt'

                fe.onsetDetector.parserNoteOnsetsGrTruth(URIrecOnsets, currSectionLink.beginTs, currSectionLink.endTs)
                
#                 #### EXPERIMENT: use phone annotations instead:
#                 onsetTimestamps = getOnsetsFromPhonemeAnnos(URIRecordingChunkResynthesizedNoExt)
                
            elif ParametersAlgo.WITH_ORACLE_ONSETS == 0:
                
                fe.onsetDetector.parserNoteOnsets(URIRecordingChunkResynthesizedNoExt + '.wav')
            
            detectedTokenList = decoder.decodeAudio(fe, listNonVocalFragments, usePersistentFiles,  fromTsTextGrid, toTsTextGrid)
            
            phiOptPath = {'phi': decoder.path.phiPathLikelihood}
            detectedPath = decoder.path.pathRaw
            tokenList2TabFile(detectedTokenList, URIRecordingChunkResynthesizedNoExt, tokenLevelAlignedSuffix, currSectionLink.beginTs)
            
            with open(URIRecordingChunkResynthesizedNoExt + tokenLevelAlignedSuffix + '_phi', 'w'  ) as f:
                json.dump( phiOptPath, f)
           
            
        ### VISUALIZE result 
    #         decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)
        
        else:   
                print "{}\n already exists. No decoding".format(detectedAlignedfileName)
                detectedTokenList = readListOfListTextFile(detectedAlignedfileName)
                if ParametersAlgo.WITH_ORACLE_PHONEMES:
                    outputURI = URIRecordingChunkResynthesizedNoExt + '.path_oracle'
                else:
                    outputURI = URIRecordingChunkResynthesizedNoExt + '.path'
                 
                detectedPath = ''
#                 detectedPath = readListTextFile(outputURI)
                 
                phiOptPath = ''
#                 with open(URIRecordingChunkResynthesizedNoExt + tokenLevelAlignedSuffix + '_phi', 'r'  ) as f:
#                     phiOptPathJSON = json.load(f)
#                     phiOptPath = phiOptPathJSON['phi']
                
    
        return detectedTokenList, detectedPath, phiOptPath







   

def extendSectionLinksSelectedSections(sectionLinksDict, sectionLinksAligned):
    '''
    add selected sections as field in input sectionLinks Dict 
    @param: sectionLinksAligned - list of objects of class sectionLink with the field selectedSections set
    @return:  changed @param sectionLinksDict 
    '''
    sectionLinks = parseSectionLinks(sectionLinksDict)
    for currSectionLink in sectionLinks:
                        
                        
                        beginTimeStr = str(currSectionLink['time'][0])
                        beginTimeStr = beginTimeStr.replace("[","")
                        beginTimeStr = beginTimeStr.replace("]","")
                        
                        relevantSectionLinkAligned =  getSectionLinkBybeginTs(sectionLinksAligned, beginTimeStr)
                        
                        if not hasattr(relevantSectionLinkAligned, 'selectedSections'):
                            continue 
                        selectedSections = []
                        for currSelectedSection in relevantSectionLinkAligned.selectedSections:
                            sec = {'melodicStructure':currSelectedSection.melodicStructure, 'lyricStructure':currSelectedSection.lyricStructure}
                            selectedSections.append(sec)
                            currSectionLink['selectedSections'] = selectedSections
    return sectionLinksDict                       

def getSectionLinkBybeginTs(sectionLinks, queryBeginTs):
    for sectionLink in sectionLinks:
        if str(sectionLink.beginTs) ==  queryBeginTs:
            return sectionLink
                                 
   



def downloadSymbTr(workMBID, outputDirURI):
    
    symbtr = compmusic.dunya.makam.get_symbtr(workMBID)
    symbTrCompositionName = symbtr['name']
    
    URL = 'https://raw.githubusercontent.com/MTG/SymbTr/master/txt/' + symbTrCompositionName + '.txt'
    outputFileURI = os.path.join(outputDirURI, symbTrCompositionName + '.txt')
    fetchFileFromURL(URL, outputFileURI)
   
    return outputFileURI
    
    
    
def download_wav(musicbrainzid, outputDir):
        '''
        download wav for MB recording id from makam collection
        '''
        mp3FileURI = dunya.makam.download_mp3(musicbrainzid, outputDir)
    ###### mp3 to Wav: way 1
    #         newName = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.mp3')
    #         os.rename(mp3FileURI, newName )
    #         mp3ToWav = Mp3ToWav()
    #         wavFileURI = mp3ToWav.run('dummyMBID', newName)
        
        ###### mp3 to Wav: way 2
        wavFileURI = os.path.splitext(mp3FileURI)[0] + '.wav'
        if os.path.isfile(wavFileURI):
            return wavFileURI
            
        pipe = subprocess.Popen(['/usr/local/bin/ffmpeg', '-i', mp3FileURI, wavFileURI])
        pipe.wait()
    
        return wavFileURI

def stereoToMono(wavFileURI):
        sampleRate = 44100
        loader = essentia.standard.MonoLoader(filename=wavFileURI, sampleRate=sampleRate)
        audio = loader()
        monoWriter = essentia.standard.MonoWriter(filename=wavFileURI)
        monoWriter(audio)
        return wavFileURI
    

def determineSuffix(withDuration, withOracle, withOracleOnsets, decodedTokenLevel):
    tokenAlignedSuffix = '.'
    tokenAlignedSuffix += decodedTokenLevel
    if withDuration: tokenAlignedSuffix += 'Duration'
    if withOracle == 1: tokenAlignedSuffix += 'OraclePhonemes'
    elif withOracle == -1: tokenAlignedSuffix += 'NoPhonemes'
    if withOracleOnsets == 1: tokenAlignedSuffix += 'OracleOnsets'
    elif withOracleOnsets == 0: tokenAlignedSuffix += 'Onsets'
    
    tokenAlignedSuffix += 'Aligned' 
    return tokenAlignedSuffix