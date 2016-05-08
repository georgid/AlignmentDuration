# -*- coding: utf-8 -*-

'''
Created on Nov 13, 2012

@author: GuyZ
'''

import numpy

import os
import sys
from hmm.Parameters import Parameters
from hmm.continuous.DurationPdf import NUMFRAMESPERSEC

# parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir, os.path.pardir)) 
# pathJingju = os.path.join(parentParentDir, 'Jingju')
# 
# if pathJingju not in sys.path:
#     sys.path.append(pathJingju )
from align.ParametersAlgo import ParametersAlgo
import logging
from align.LyricsParsing import loadOraclePhonemes
from jingju.ParsePhonemeAnnotation import loadPhonemesAnnoOneSyll
from align.LyricsWithModelsHTK import LyricsWithModelsHTK
from align.LyricsWithModelsGMM import LyricsWithModelsGMM


# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir,os.path.pardir )) 
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir )) 

    
from align.Decoder import Decoder

modelDIR = projDir + '/model/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

from htkparser.htk_converter import HtkConverter





def loadSmallAudioFragment( featureExtractor, extractedPitchList,  URIrecordingNoExt, URIRecordingChunkResynthesizedNoExt, withSynthesis, sectionLink, htkParser):
    '''
    test duration-explicit HMM with audio features from real recording and htk-loaded model
    asserts it works. no results provided 
    '''
    
    featureVectors, URIRecordingChunk = featureExtractor.loadMFCCs(URIrecordingNoExt, extractedPitchList,  URIRecordingChunkResynthesizedNoExt, withSynthesis, sectionLink) #     featureVectors = featureVectors[0:1000]

    
    if ParametersAlgo.FOR_JINGJU:
        lyricsWithModels = LyricsWithModelsGMM( sectionLink.section.lyrics, htkParser,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
    elif ParametersAlgo.FOR_MAKAM:
        lyricsWithModels = LyricsWithModelsHTK( sectionLink.section.lyrics, htkParser,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
    else:
        sys.exit('neither JINGJU nor MAKAM.')

    if lyricsWithModels.getTotalDuration() == 0:
        logging.warning("total duration of segment {} = 0".format(URIRecordingChunk))
        return None, None, None
    
    
    # needed only with duration model
    lyricsWithModels.duration2numFrameDuration(featureVectors, URIrecordingNoExt)
#     lyricsWithModels.printPhonemeNetwork()

    
    return lyricsWithModels, featureVectors, URIRecordingChunk






def loadSmallAudioFragmentOracle(URIRecordingChunkResynthesizedNoExt, htkParser, lyrics):

        
        # lyricsWithModelsORacle used only as helper to get its stateNetwork with durs, but not functionally - e.g. their models are not used
        withPaddedSilence = False # dont model silence at end and beginnning. this away we dont need to do annotatation of sp at end and beginning 
        lyricsWithModelsORacle = LyricsWithModelsHTK(lyrics,  htkParser,  ParametersAlgo.DEVIATION_IN_SEC, withPaddedSilence)
        
        
        URIrecordingTextGrid  = URIRecordingChunkResynthesizedNoExt  + '.TextGrid'
        fromSyllableIdx = 1; toSyllableIdx = 8
        phonemeAnnotaions = loadOraclePhonemes(URIrecordingTextGrid, fromSyllableIdx, toSyllableIdx)   
    
        
        lyricsWithModelsORacle.setPhonemeNumFrameDurs( phonemeAnnotaions)
        
        return lyricsWithModelsORacle
    

def loadSmallAudioFragmentOracleJingju(currSectionLink):
    
    lyricsTextGrid = currSectionLink.section.lyricsTextGrid
    # get start and end phoneme indices from TextGrid
    lyricsWithModelsORacle = []
    for idx, syllableIdx in enumerate(range(currSectionLink.section.fromSyllableIdx, currSectionLink.section.toSyllableIdx+1)): # for each  syllable including silent syllables
        # go through the phonemes. load all 
        currSyllable = currSectionLink.listWordsFromTextGrid[idx].syllables[0]
        phonemesAnno, syllableTxt = loadPhonemesAnnoOneSyll(lyricsTextGrid, syllableIdx, currSyllable)
        lyricsWithModelsORacle.extend(phonemesAnno)
    return lyricsWithModelsORacle     
            

# def parsePhoenemeAnnoDursOracle(lyrics, phonemeListExtracted ):
#     
#         htkParser = HtkConverter()
#         htkParser.load(MODEL_URI, HMM_LIST_URI)
#         
#         dummyDeviation = 1
#         # lyricsWithModelsORacle used only as helper for state durs, but not functionally
#         lyricsWithModelsORacle = _LyricsWithModelsBase(lyrics, htkParser,  dummyDeviation, ParametersAlgo.WITH_PADDED_SILENCE)
#         lyricsWithModelsORacle.setPhonemeDurs( phonemeListExtracted)
#         
#         return lyricsWithModelsORacle


def getDecoder(lyricsWithModels, URIrecordingNoExt):
    '''
    helper routine to init decoder. change here parameters
    '''
    alpha = 0.97
    ONLY_MIDDLE_STATE=False
    params = Parameters(alpha, ONLY_MIDDLE_STATE)
    decoder = Decoder(lyricsWithModels, URIrecordingNoExt, params.ALPHA)
    return decoder


def decode(lyricsWithModels, observationFeatures, URIrecordingNoExt):   
    '''
    convenience method. same as decoder.decodeAudio() without the parts with WITH_Duration flag.
    '''
    decoder = getDecoder(lyricsWithModels, URIrecordingNoExt)
    
    #  decodes
    decoder.hmmNetwork.initDecodingParameters(observationFeatures)
    chiBackPointer, psiBackPointer = decoder.hmmNetwork._viterbiForcedDur()
#   
    decoder.backtrack( chiBackPointer, psiBackPointer)
