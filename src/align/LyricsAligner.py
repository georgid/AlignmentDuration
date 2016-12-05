import shutil
import csv
import logging
import os
import sys


### include src folder
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if parentDir not in sys.path:
    sys.path.append(parentDir)

 
from src.onsets.OnsetDetector import OnsetDetector

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

from FeatureExtractor import FeatureExtractor
import os
import sys
import json
from src.for_makam.MakamRecording import parseSectionLinks, MakamRecording
from Decoder import logger,  Decoder
from ParametersAlgo import ParametersAlgo
from src.parse.TextGrid_Parsing import tierAliases,\
    divideIntoSentencesFromAnnoWithSil
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir, os.path.pardir,)) 
from scipy.io import wavfile

# from evalPhonemes import eval_percentage_correct_phonemes, display


import essentia.standard

projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir )) 

modelDIR = projDir + '/models_makam/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

from src.for_makam.MakamScore import  loadMakamScore2


from src.utilsLyrics.Utilz import writeListOfListToTextFile, writeListToTextFile,\
    getMeanAndStDevError, getSectionNumberFromName, readListOfListTextFile, \
    readListTextFile, getMelodicStructFromName, addTimeShift,  fetchFileFromURL

from htkparser.htk_converter import HtkConverter
ANNOTATION_EXT = '.TextGrid'
 
  


class LyricsAligner():
    def __init__(self, recording,  WITH_SECTION_ANNOTATIONS, path_to_hcopy):
        
        self.recording = recording
        self.WITH_SECTION_ANNOTATIONS = WITH_SECTION_ANNOTATIONS
        self.path_to_hcopy = path_to_hcopy
        self.tokenLevelAlignedSuffix = determineSuffix(ParametersAlgo.WITH_DURATIONS, ParametersAlgo.WITH_ORACLE_PHONEMES,\
                                                        ParametersAlgo.WITH_ORACLE_ONSETS, ParametersAlgo.DETECTION_TOKEN_LEVEL, ParametersAlgo.OBS_MODEL, ParametersAlgo.Q_WEIGHT_TRANSITION)
        
        if ParametersAlgo.FOR_MAKAM:
            
        
            self.model = HtkConverter()
            self.model.load(MODEL_URI, HMM_LIST_URI)
            pass
        
        elif ParametersAlgo.FOR_JINGJU:
            #### read models_makam done in LyricsWithModels depending 
            self.model = self.recording.which_fold
        else: 
            sys.exit('neither JINGJU nor MAKAM.')



    def alignRecording(self, extractedPitchList, outputDir ):
            '''
            align each section link
            
            Return 
            detected token 
            '''
            ##### parameters 
            if self.WITH_SECTION_ANNOTATIONS: 
                sectionLinks = self.recording.sectionAnnos
            else:
                sectionLinks = self.recording.sectionLinks
            
            #### get duration        
            sampFreq, snd = wavfile.read( self.recording.recordingNoExtURI + '.wav' )
            duration = snd.shape[0] / sampFreq

                
            complete_recording_detected_token_list = []    
            for  currSectionLink in sectionLinks :
                    if duration < currSectionLink.endTs:
                        break
                    
                    detectedTokenList = []
#                     if sectionLink.melodicStructure.startswith('ARANAGME'):
#                         print("skipping sectionLink {} with no lyrics ...".format(sectionLink.melodicStructure))
#                         continue                
                    if not hasattr(currSectionLink, 'section') or currSectionLink.section == None:
                        print("skipping sectionAnno {} not matched to any score section ...".format(currSectionLink))
                        continue   
                    
                    
                    if self.WITH_SECTION_ANNOTATIONS: 
                        lyrics = currSectionLink.section.lyrics
             
                        lyricsStr = lyrics.__str__()
                        if not lyricsStr or lyricsStr=='None' or  lyricsStr =='_SAZ_':
                            print("skipping sectionLink {} with no lyrics ...".format(currSectionLink.melodicStructure))
                            continue 
                        detectedTokenList, detectedPath, maxPhiScore = self.alignLyricsSection(  extractedPitchList,   [],  self.tokenLevelAlignedSuffix,   currSectionLink)
#                         self.extractNoteOnsetsAndEval(currSectionLink)
      
                     
                    else:  # section links. align all related and take maximum
                        detectedTokenList = self.alignSectionLinkProbableSections( extractedPitchList, currSectionLink)
                    
                    ############ add initial time of each section
                    currSectionLink.detectedTokenList = detectedTokenList
                    complete_recording_detected_token_list.append(currSectionLink.detectedTokenList)
        
            return complete_recording_detected_token_list, self.recording.sectionLinksOrAnnoDict          
    
                
             

    def eval_percentage_phonemes(self, URI_TextGrid, currSectionLink):
        '''
        convenience method that calls 
        eval_percentage_correct_phonemes
        '''
        URI_PPG = currSectionLink.URIRecordingChunk + '.' + ParametersAlgo.OBS_MODEL + '.PPG.pkl'
        METU_to_stateidx_URI = None
        if ParametersAlgo.OBS_MODEL == 'MLP'  or ParametersAlgo.OBS_MODEL == 'MLP_fuzzy':
            METU_to_stateidx_URI = os.path.join(os.path.dirname(os.path.realpath(__file__)), os.pardir, 'for_makam', 'state_str2int_METU')
        perc_correct, B_map_max = eval_percentage_correct_phonemes(URI_TextGrid, URI_PPG, METU_to_stateidx_URI, currSectionLink.counter)
        display(perc_correct, B_map_max)


    def evalAccuracy(self, eval_level):
        
        pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation/align_eval')
        if pathEvaluation not in sys.path:
                    sys.path.append(pathEvaluation)
        from AccuracyEvaluator import _evalAccuracy

        totalCorrectDurations = 0
        totalDurations = 0    
        
        if self.WITH_SECTION_ANNOTATIONS: 
                sectionLinks = self.recording.sectionAnnos
        else:
                sectionLinks = self.recording.sectionLinks
        
##     might be needed for jingju        
        URI_TextGrid = os.path.join(self.recording.recordingNoExtURI + ANNOTATION_EXT)
        
            
        ##### add index of begin token and end token        
        
        high_level_tier_name = tierAliases.line
                               
        list_start_end_indices, annotationLinesList = divideIntoSentencesFromAnnoWithSil(URI_TextGrid, \
        high_level_tier_name, eval_level)
        if len(list_start_end_indices) != len(sectionLinks):
            sys.exit('TextGrid has {} lines, whereas section Links are {}'.format(len(list_start_end_indices), len(sectionLinks) ) )
        for idx, currSectionLink in enumerate(sectionLinks):  # assign syllable/word/phrase start- and end-indices in TextGrid
            currSectionLink.set_begin_end_indices(list_start_end_indices[idx][0], list_start_end_indices[idx][1])
        
       

        for currSectionLink in sectionLinks:
                    
            
                        if not hasattr(currSectionLink, 'detectedTokenList'): # use the exostence of  detected token list as indicator of lyrics-sections
                            continue
                        
                        ###################### eval phoeneme level
#                         self.eval_percentage_phonemes(URI_TextGrid, currSectionLink)
                        
                        
                        ############################# eval accuracy Annotaion level
                        correctDuration = 0
                        totalDuration = 1
                        
                        correctDuration, totalDuration = _evalAccuracy(URI_TextGrid, currSectionLink.detectedTokenList, ParametersAlgo.EVAL_LEVEL, currSectionLink.token_begin_idx, currSectionLink.token_end_idx  )
                        logger.debug('current section {} accuracy: {}'.format( currSectionLink,  correctDuration / totalDuration) )
                        
                        totalCorrectDurations += correctDuration
                        totalDurations += totalDuration
            
        accuracy = totalCorrectDurations / totalDurations
        logger.warning("recording {} accuracy: {:.2f}".format(self.recording.recordingNoExtURI, accuracy))                
        return totalCorrectDurations, totalDurations

    def store_as_textGrid(self, detectedTokenList):
        
        if self.WITH_SECTION_ANNOTATIONS: 
                sectionLinks = self.recording.sectionAnnos
        else:
                sectionLinks = self.recording.sectionLinks
        
        serializedFile = self.recording.recordingNoExtURI + '.' +  ParametersAlgo.DETECTION_TOKEN_LEVEL
        URI_TextGrid = os.path.join(self.recording.recordingNoExtURI + ANNOTATION_EXT)
        
        f = open(serializedFile,'w')
        csvWriter = csv.writer(f, delimiter='\t')
        csvWriter.writerow(['start','end','phone'])
        for currSectionLink in sectionLinks:
            if not hasattr(currSectionLink, 'detectedTokenList'): # use the exostence of  detected token list as indicator of lyrics-sections
                                      continue
            # export as csv with tabs
            for row in currSectionLink.detectedTokenList:
                csvWriter.writerow(row[:-1])
        f.close()
#         with open( self.recording.recordingNoExtURI + ParametersAlgo.DETECTION_TOKEN_LEVEL,'w') as f:
#                 csvWriter = csv.writer(f)
#                 csvWriter.writerows(detectedTokenList)
                
        
         
                
    
    def alignSectionLinkProbableSections(self,  extractedPitchList,    currSectionLink):
        '''
        runs alignment on given audio multiple times with a list of probable sections with their corresponding lyrics
        @return detectedTokenList with best score
        @return selectedSection section with this score
        '''   
        maxPhiScore = float('-inf')
        probabaleSections = self.recording.score.getProbableSectionsForMelodicStructure(currSectionLink)
        
        for probabaleSection in probabaleSections:
            currSectionLink.section = probabaleSection
            currTokenLevelAlignedSuffix =  self.tokenLevelAlignedSuffix + '_' + probabaleSection.melodicStructure + '_' + probabaleSection.lyricStructure
            
            currDetectedTokenList, detectedPath, phiScore = self.alignLyricsSection( extractedPitchList,  [],   currTokenLevelAlignedSuffix,  currSectionLink)
            if phiScore > maxPhiScore:
                maxPhiScore = phiScore
                selectedSection = probabaleSection
                detectedTokenList = currDetectedTokenList
        
        # get sections with same lyrics as top-aligned section
        selectedSectionsSameLyrics =  self.recording.score.getSectionsSameLyrics( selectedSection, probabaleSections)
        currSectionLink.setSelectedSections(selectedSectionsSameLyrics)
        
        return detectedTokenList
         
         
               
    def extractNoteOnsetsAndEval(self, currSectionLink):
                    '''
                    only extract note onsets as a separate step
                    and eval note onset extraction
                    
                    '''
                    URIrecOnsets = os.path.join( os.path.dirname(self.recording.recordingNoExtURI), ParametersAlgo.ANNOTATION_SCORE_ONSETS_EXT)
                    onsetDetector = OnsetDetector (currSectionLink) 
                    gr_truth_URI = onsetDetector.parseNoteOnsetsGrTruth(URIrecOnsets)
                    extractedOnsetsURI =  onsetDetector.extractNoteOnsets(currSectionLink.URIRecordingChunk + '.wav')
                    
                    print "evaluateTranscriptions( '"  + gr_truth_URI  + "','"  + extractedOnsetsURI + "')"





    

    def  alignLyricsSection( self, extractedPitchList,  listNonVocalFragments,    tokenLevelAlignedSuffix,    currSectionLink):
            '''
            align @param: lyrics for one section
            '''
                
        #     read from file result
            URIRecordingChunkResynthesizedNoExt = currSectionLink.URIRecordingChunk
            detectedAlignedfileName = currSectionLink.URIRecordingChunk + tokenLevelAlignedSuffix
            fe = FeatureExtractor(self.path_to_hcopy, currSectionLink) 
            onsetDetector  = OnsetDetector(currSectionLink)
            
            detectedPath = ''
            phiOptPath = ''
            detectedTokenList = []
            
            if not os.path.isfile(detectedAlignedfileName):
                
                fromTsTextGrid = -1; toTsTextGrid = -1
                
                
                if  ParametersAlgo.WITH_ORACLE_PHONEMES: # oracle phonemes
                    raw_input('implemented only for Kimseye...! Continue only if working with Kimseye' )
                    if ParametersAlgo.FOR_MAKAM:    fromTsTextGrid = 0; toTsTextGrid = 20.88  # for kimseye etmem
                    fromSyllableIdx = 0; toSyllableIdx = 10
                    currSectionLink.loadSmallAudioFragmentOracle(self.model, fromSyllableIdx, toSyllableIdx )
                    fe.featureVectors = currSectionLink.lyricsWithModels                      # featureVectors is alias for LyricsWithModelsOracle
    
                else:     ###### extract audio features
                    fe.featureVectors = currSectionLink.loadSmallAudioFragment( fe, extractedPitchList,   self.recording.recordingNoExtURI, self.model)
    #                 sectionLink.lyricsWithModels.printWordsAndStates()
            #################### decode
                decoder = Decoder(currSectionLink, currSectionLink.lyricsWithModels, URIRecordingChunkResynthesizedNoExt)
                
    
                ##### prepare note onsets. result stored in files, which are used in decoding  ############################
                if ParametersAlgo.WITH_ORACLE_ONSETS == 1:
                    URIrecOnsets = os.path.join(os.path.dirname(self.recording.recordingNoExtURI), ParametersAlgo.ANNOTATION_RULES_ONSETS_EXT)
                    onsetDetector.parseNoteOnsetsGrTruth(URIrecOnsets)
                    
                elif ParametersAlgo.WITH_ORACLE_ONSETS == 0:
                    onsetDetector.extractNoteOnsets(URIRecordingChunkResynthesizedNoExt + '.wav')
                ###############################################
                
    
                detectedTokenList = decoder.decodeAudio(fe, onsetDetector, listNonVocalFragments,  fromTsTextGrid, toTsTextGrid)
                detectedTokenList = addTimeShift(detectedTokenList,  currSectionLink.beginTs)
                
    
                detectedPath = decoder.path.pathRaw
    
    #                 ##### write all decoded output persistently to files
                if ParametersAlgo.WRITE_TO_FILE:
                    self.write_decoded_to_file(tokenLevelAlignedSuffix, URIRecordingChunkResynthesizedNoExt, decoder.path.phiPathLikelihood,  detectedTokenList)
               
                
            ### VISUALIZE result 
        #         decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)
            
            else:    # do not decode, read form file
                detectedTokenList, phiOptPath, detectedPath = self.read_decoded(URIRecordingChunkResynthesizedNoExt, detectedAlignedfileName)
                    
          
            return detectedTokenList, detectedPath, phiOptPath



    def write_decoded_to_file(self, tokenLevelAlignedSuffix, URIRecordingChunkResynthesizedNoExt, phiOptPath, detectedTokenList):
        '''
        writes path and list of aligned tokens to file 
        '''
        
        tokenAlignedfileName = URIRecordingChunkResynthesizedNoExt + tokenLevelAlignedSuffix
        with open(tokenAlignedfileName, 'w') as f1:
            json.dump(detectedTokenList, f1) 
        #             writeListOfListToTextFile(detectedTokenList, 'startTs \t endTs \t phonemeOrSyllorWord \t beginNoteNumber \n', tokenAlignedfileName)
        phiOptPath = {'phi':phiOptPath}
        with open(URIRecordingChunkResynthesizedNoExt + tokenLevelAlignedSuffix + '_phi', 'w') as f:
            json.dump(phiOptPath, f)



    def read_decoded(self, URIRecordingChunkResynthesizedNoExt, detectedAlignedfileName):
        '''
        read detected token list from persistent file
        '''
        print "{}\n already exists. No decoding".format(detectedAlignedfileName) 
        #                 detectedTokenList = readListOfListTextFile(detectedAlignedfileName)
        with open(detectedAlignedfileName, 'r') as f2:
            detectedTokenList = json.load(f2)
        if ParametersAlgo.WITH_ORACLE_PHONEMES:
            outputURI = URIRecordingChunkResynthesizedNoExt + '.path_oracle'
        else:
            outputURI = URIRecordingChunkResynthesizedNoExt + '.path'
        
        detectedPath = readListTextFile(outputURI)
        
        phiOptPath = '' # TODO: read with json
        return detectedTokenList, phiOptPath, detectedPath



def loadMakamRecording(mbRecordingID, audioFileURI, symbtrtxtURI, sectionMetadataDict, sectionLinksDict,   withAnnotations):
    '''
    refactored method
    '''
    
    makamScore = loadMakamScore2(symbtrtxtURI, sectionMetadataDict)
    if ParametersAlgo.LOGGING_LEVEL == logging.DEBUG or ParametersAlgo.LOGGING_LEVEL == logging.INFO:
        makamScore.printSectionsAndLyrics()
#     raw_input("make sure lyrics are correct in sections. if not correct change URL to get file from in  get_section_metadata_dict... then press key")

    mr = MakamRecording(mbRecordingID, audioFileURI, makamScore, sectionLinksDict, withAnnotations)
    
    return mr  
    

    


   

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
                                 
   


    
    
    



def stereoToMono(wavFileURI):
        sampleRate = 44100
        loader = essentia.standard.MonoLoader(filename=wavFileURI, sampleRate=sampleRate)
        audio = loader()
        monoWriter = essentia.standard.MonoWriter(filename=wavFileURI)
        monoWriter(audio)
        return wavFileURI
    

def determineSuffix(withDuration, withOracle, withOracleOnsets, decodedTokenLevel, obs_model, q_weight_transition):
    tokenAlignedSuffix = '.'
    tokenAlignedSuffix += decodedTokenLevel
    if ParametersAlgo.DECODE_WITH_HTK:
        tokenAlignedSuffix += '_htk_'
    else:
        if withDuration: tokenAlignedSuffix += 'Duration'
        if withOracle == 1: tokenAlignedSuffix += 'OraclePhonemes'
        elif withOracle == -1: tokenAlignedSuffix += 'NoPhonemes'
        if withOracleOnsets == 1: 
            tokenAlignedSuffix += 'OracleOnsets'
            tokenAlignedSuffix += str(q_weight_transition) 
        elif withOracleOnsets == 0:
            tokenAlignedSuffix += 'Onsets'
            tokenAlignedSuffix += str(q_weight_transition)
        
        
        if obs_model == 'MLP': tokenAlignedSuffix += 'MLP'
        if obs_model == 'MLP_fuzzy': tokenAlignedSuffix += 'MLP_fuzzy'
    
            
    
    tokenAlignedSuffix += 'Aligned' 
    return tokenAlignedSuffix