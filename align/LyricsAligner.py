
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
#
#

import os
import sys
import json
import subprocess
from align.MakamRecording import parseSectionLinks, MakamRecording
from align.Decoder import logger
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 
# pathPycompmusic = os.path.join(parentDir, 'pycompmusic')
# if pathPycompmusic not in sys.path:
#     sys.path.append(pathPycompmusic)


pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)
    
from AccuracyEvaluator import _evalAccuracy
from WordLevelEvaluator import tierAliases


import compmusic.extractors
from compmusic import dunya
from compmusic.dunya import makam

import essentia.standard

currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )
modelDIR = currDir + '/model/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

from MakamScore import  loadMakamScore2
from hmm.examples.main import loadSmallAudioFragment
from Decoder import Decoder


from utilsLyrics.Utilz import writeListOfListToTextFile, writeListToTextFile,\
    getMeanAndStDevError, getSectionNumberFromName, readListOfListTextFile, \
    readListTextFile, getMelodicStructFromName, tokenList2TabFile,  fetchFileFromURL

from htkparser.htk_converter import HtkConverter
ANNOTATION_EXT = '.TextGrid'
 
        
def alignRecording( symbtrtxtURI, sectionMetadata, sectionLinksDict, audioFileURI, extractedPitchList, outputDir, sectionAnnosDict=None):

        # parameters 
        withSynthesis = False
        withOracle = False
        oracleLyrics = ''
        usePersistentFiles = True
        withAnnotations = True
        
        htkParser = HtkConverter()
        htkParser.load(MODEL_URI, HMM_LIST_URI)
        
        recordingNoExtURI = os.path.splitext(audioFileURI)[0]
        
        makamScore = loadMakamScore2(symbtrtxtURI, sectionMetadata )
      

        mr = MakamRecording(makamScore, sectionLinksDict, sectionAnnosDict, withAnnotations )
            
        tokenLevelAlignedSuffix = '.alignedLyrics' 
        totalDetectedTokenList = []
        
        totalCorrectDurations = 0
        totalDurations = 0
    
        
        if not withAnnotations: 
        
            for  currSectionLink in mr.sectionLinks :
                if currSectionLink.melodicStructure.startswith('ARANAGME'):
                    print("skipping sectionLink {} with no lyrics ...".format(currSectionLink.melodicStructure))
                    continue
                
    
                detectedTokenList = alignSectionLinkProbableSections(makamScore, extractedPitchList, withSynthesis, withOracle,  oracleLyrics, usePersistentFiles, tokenLevelAlignedSuffix,  recordingNoExtURI, currSectionLink, htkParser) 
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
                
                URIRecordingChunkResynthesizedNoExt =  recordingNoExtURI + "_" + "{}".format(currSectionAnno.beginTs) + '_' + "{}".format(currSectionAnno.endTs) 
                detectedTokenList, detectedPath, maxPhiScore = alignLyricsSection( lyrics, extractedPitchList,  withSynthesis, withOracle, oracleLyrics, [],  usePersistentFiles, tokenLevelAlignedSuffix, recordingNoExtURI, URIRecordingChunkResynthesizedNoExt, currSectionAnno, htkParser)
                
                evalLevel = tierAliases.phraseLevel
                correctDuration, totalDuration = _evalAccuracy(URIRecordingChunkResynthesizedNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, currSectionAnno.beginTs )
    
                totalCorrectDurations += correctDuration
                totalDurations += totalDuration
                
                
                totalDetectedTokenList.extend(detectedTokenList)
            
            accuracy = totalCorrectDurations / totalDurations
            logger.info("accuracy: {:.2f}".format(accuracy))     
            return totalDetectedTokenList, sectionLinksDict
    
def alignSectionLinkProbableSections(makamScore,extractedPitchList, withSynthesis, withOracle,  oracleLyrics, usePersistentFiles, tokenLevelAlignedSuffix,  recordingNoExtURI, currSectionLink, htkParser):
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
        currDetectedTokenList, detectedPath, phiScore = alignLyricsSection( probabaleSection.lyrics, extractedPitchList, withSynthesis, withOracle, oracleLyrics, [],  usePersistentFiles, currTokenLevelAlignedSuffix, recordingNoExtURI, URIRecordingChunkResynthesizedNoExt, currSectionLink, htkParser)
        if phiScore > maxPhiScore:
            maxPhiScore = phiScore
            selectedSection = probabaleSection
            detectedTokenList = currDetectedTokenList
    
    # get sections with same lyrics as top-aligned section
    selectedSectionsSameLyrics =  makamScore.getSectionsSameLyrics( selectedSection, probabaleSections)
    currSectionLink.setSelectedSections(selectedSectionsSameLyrics)
    
    return detectedTokenList
         
         
               
def  alignLyricsSection( lyrics, extractedPitchList,  withSynthesis, withOracle, lyricsWithModelsORacle, listNonVocalFragments,   usePersistentFiles, tokenLevelAlignedSuffix,  URIrecordingNoExt, URIRecordingChunkResynthesizedNoExt, currSectionLink, htkParser):
        '''
        align @param: lyrics for one section
        '''
        if withOracle:
    
            # synthesis not needed really in this setting. workaround because without synth takes whole recording  
            withSynthesis = 1
            
    #     read from file result
        
        detectedAlignedfileName = URIRecordingChunkResynthesizedNoExt + tokenLevelAlignedSuffix
        if not os.path.isfile(detectedAlignedfileName):
            #     ###### extract audio features
            lyricsWithModels, obsFeatures, URIrecordingChunk = loadSmallAudioFragment(lyrics, extractedPitchList,   URIrecordingNoExt, URIRecordingChunkResynthesizedNoExt, bool(withSynthesis), currSectionLink, htkParser)
            
        # DEBUG: score-derived phoneme  durations
    #     lyricsWithModels.printPhonemeNetwork()
    #     lyricsWithModels.printWordsAndStates()
            alpha = 0.97
            decoder = Decoder(lyricsWithModels, URIRecordingChunkResynthesizedNoExt, alpha)
        #  TODO: DEBUG: do not load models
        # decoder = Decoder(lyrics, withModels=False, numStates=86)
        #################### decode
            
            if withOracle:
                detectedTokenList = decoder.decodeWithOracle(lyricsWithModelsORacle, URIRecordingChunkResynthesizedNoExt )
            else:
                detectedTokenList = decoder.decodeAudio(obsFeatures, listNonVocalFragments, usePersistentFiles)
            
            phiOptPath = {'phi': decoder.path.phiPathLikelihood}
            detectedPath = decoder.path.pathRaw
            tokenList2TabFile(detectedTokenList, URIRecordingChunkResynthesizedNoExt, tokenLevelAlignedSuffix, currSectionLink.beginTs)
            
            with open(URIRecordingChunkResynthesizedNoExt + tokenLevelAlignedSuffix + '_phi', 'w'  ) as f:
                json.dump( phiOptPath, f)
           
            
        ### VISUALIZE result 
    #         decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)
        
        else:   
                print "{} already exists. No decoding".format(detectedAlignedfileName)
                detectedTokenList = readListOfListTextFile(detectedAlignedfileName)
                if withOracle:
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