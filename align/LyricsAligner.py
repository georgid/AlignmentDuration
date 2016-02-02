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
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 
# pathPycompmusic = os.path.join(parentDir, 'pycompmusic')
# if pathPycompmusic not in sys.path:
#     sys.path.append(pathPycompmusic)


import compmusic.extractors
# from docserver import util
from compmusic import dunya
from compmusic.dunya import makam
import tempfile

currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )
modelDIR = currDir + '/model/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

from MakamScore import loadMakamScore, loadMakamScore2
from hmm.examples.main import loadSmallAudioFragment
from Decoder import Decoder
from SectionLink import SectionLink
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")


from utilsLyrics.Utilz import writeListOfListToTextFile, writeListToTextFile,\
    getMeanAndStDevError, getSectionNumberFromName, readListOfListTextFile, readListTextFile, getMelodicStructFromName, tokenList2TabFile

from htkparser.htk_converter import HtkConverter

 
        
def alignRecording( symbtrtxtURI, sectionMetadata, sectionLinks, audioFileURI, extractedPitchList, outputDir):

        # parameters 
        withSynthesis = True
        withOracle = False
        oracleLyrics = ''
        usePersistentFiles = True
        
        htkParser = HtkConverter()
        htkParser.load(MODEL_URI, HMM_LIST_URI)
        
        recordingNoExtURI = os.path.splitext(audioFileURI)[0]
        
        sectionLinks = _loadsectionTimeStampsLinksNew( sectionLinks) 
        makamScore = loadMakamScore2(symbtrtxtURI, sectionMetadata )
        
            
        tokenLevelAlignedSuffix = '.alignedLyrics' 
        totalDetectedTokenList = []
        for  currSectionLink in sectionLinks :
            if currSectionLink.melodicStructure.startswith('ARANAGME'):
                print("skipping sectionLink {} with no lyrics ...".format(currSectionLink.melodicStructure))
                continue
            
            
#             lyrics = makamScore.getLyricsForSection(currSectionLink.melodicStructure)
#     
#             lyricsStr = lyrics.__str__()
#             if not lyricsStr or lyricsStr=='None' or  lyricsStr =='_SAZ_':
#                 print("skipping sectionLink {} with no lyrics ...".format(currSectionLink.melodicStructure))
#                 continue
#             
#             detectedTokenList, detectedPath, maxPhiScore = alignSectionLink( lyrics, extractedPitchList,  withSynthesis, withOracle, oracleLyrics, [],  usePersistentFiles, tokenLevelAlignedSuffix, recordingNoExtURI, currSectionLink, htkParser)
            
            detectedTokenList, selectedSection = alignBestSectionLink(makamScore, extractedPitchList, withSynthesis, withOracle,  oracleLyrics, usePersistentFiles, tokenLevelAlignedSuffix,  recordingNoExtURI, currSectionLink, htkParser) 
#             TODO: return selected section lyrics
            print selectedSection
            
            totalDetectedTokenList.extend(detectedTokenList)
        
        return totalDetectedTokenList        
        

    
def alignBestSectionLink(makamScore,extractedPitchList, withSynthesis, withOracle,  oracleLyrics, usePersistentFiles, tokenLevelAlignedSuffix,  recordingNoExtURI, currSectionLink, htkParser):
    '''
    runs alignment on given audio multiple times with a list of probable lyrics
    @return detectedTokenList with best score
    @return selectedSection section with this score
    '''   
    maxPhiScore = float('-inf')
    probabaleSections = makamScore.getProbableLyricsForMelodicStructure(currSectionLink.melodicStructure)
    for probabaleSection in probabaleSections:
        currTokenLevelAlignedSuffix =  tokenLevelAlignedSuffix + '_' + probabaleSection.melodicStructure + '_' + probabaleSection.lyricStructure
        currDetectedTokenList, detectedPath, phiScore = alignSectionLink( probabaleSection.lyrics, extractedPitchList, withSynthesis, withOracle, oracleLyrics, [],  usePersistentFiles, currTokenLevelAlignedSuffix, recordingNoExtURI, currSectionLink, htkParser)
        if phiScore > maxPhiScore:
            maxPhiScore = phiScore
            selectedSection = probabaleSection
            detectedTokenList = currDetectedTokenList

    return detectedTokenList, selectedSection
         
         
               
def  alignSectionLink( lyrics, extractedPitchList,  withSynthesis, withOracle, lyricsWithModelsORacle, listNonVocalFragments,   usePersistentFiles, tokenLevelAlignedSuffix,  URIrecordingNoExt, currSectionLink, htkParser):
        '''
        wrapper top-most logic method
        '''
        if withOracle:
    
            # synthesis not needed really in this setting. workaround because without synth takes whole recording  
            withSynthesis = 1
            
    #     read from file result
        URIRecordingChunkResynthesizedNoExt =  URIrecordingNoExt + "_" + str(currSectionLink.beginTs) + '_' + str(currSectionLink.endTs)
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
                
                detectedPath = readListTextFile(outputURI)
                
                with open(URIRecordingChunkResynthesizedNoExt + tokenLevelAlignedSuffix + '_phi', 'r'  ) as f:
                    phiOptPathJSON = json.load(f)
                    phiOptPath = phiOptPathJSON['phi']
                
    
        return detectedTokenList, detectedPath, phiOptPath




    

def _loadsectionTimeStampsLinksNew(sectionLinks):

    
        sectionLinksList = [] 
        
        if len(sectionLinks.keys()) != 1:
                raise Exception('More than one work for recording {} Not implemented!'.format(sectionLinks))
        
        # first work only
        work = sectionLinks[sectionLinks.keys()[0]]

        sectionLinks = work['links']
        for sectionAnno in sectionLinks:
                        
                        melodicStruct = sectionAnno['name']
                        
                        beginTimeStr = str(sectionAnno['time'][0])
                        beginTimeStr = beginTimeStr.replace("[","")
                        beginTimeStr = beginTimeStr.replace("]","")
                        beginTs =  float(beginTimeStr)
                            
                        endTimeStr = str(sectionAnno['time'][1])
                        endTimeStr = endTimeStr.replace("[","")
                        endTimeStr = endTimeStr.replace("]","")
                        endTs =  float(endTimeStr)
                        currSectionLink = SectionLink (melodicStruct, beginTs, endTs) 
                        sectionLinksList.append(currSectionLink )
                    
        return sectionLinksList
    
    
def constructSymbTrTxtURI(URI_dataset, workMBID):
    '''
    URI on local machine of symbTr queried by workMBID 
    '''
    symbtr = compmusic.dunya.makam.get_symbtr(workMBID)
    symbTrCompositionName = symbtr['name']
    
    compositionPath = URI_dataset + symbTrCompositionName + '/'
    symbtrtxtURI = compositionPath + symbTrCompositionName + '.txt'
    
    return symbtrtxtURI,  symbTrCompositionName 