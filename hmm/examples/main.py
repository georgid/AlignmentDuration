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
from hmm.ParametersAlgo import ParametersAlgo
import logging


# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir,os.path.pardir )) 
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir )) 

    
from align.LyricsWithModels import LyricsWithModels
from align.Decoder import Decoder
from align.FeatureExtractor import loadMFCCs, loadNoteOnsets

modelDIR = projDir + '/model/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

from htkparser.htk_converter import HtkConverter





def loadSmallAudioFragment(lyrics, extractedPitchList,  URIrecordingNoExt, URIRecordingChunkResynthesizedNoExt, withSynthesis, sectionLink, htkParser):
    '''
    test duration-explicit HMM with audio features from real recording and htk-loaded model
    asserts it works. no results provided 
    '''
    

    lyricsWithModels = LyricsWithModels(lyrics, htkParser,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
     
    observationFeatures, URIRecordingChunk = loadMFCCs(URIrecordingNoExt, extractedPitchList,  URIRecordingChunkResynthesizedNoExt, withSynthesis, sectionLink) #     observationFeatures = observationFeatures[0:1000]

    lyricsWithModels.duration2numFrameDuration(observationFeatures, URIrecordingNoExt)
#     lyricsWithModels.printPhonemeNetwork()

    
    return lyricsWithModels, observationFeatures, URIRecordingChunk

def loadSmallAudioFragmentOracle(URIrecordingNoExt, htkParser, lyrics, phonemeAnnotaions ):

        
        # lyricsWithModelsORacle used only as helper to get its stateNetwork with durs, but not functionally - e.g. their models are not used
        withPaddedSilence = False # dont model silence at end and beginnning. this away we dont need annotatation of sp at end and beginning 
        lyricsWithModelsORacle = LyricsWithModels(lyrics,  htkParser,  ParametersAlgo.DEVIATION_IN_SEC, withPaddedSilence)
        lyricsWithModelsORacle.setPhonemeNumFrameDurs( phonemeAnnotaions)
        
        return lyricsWithModelsORacle


def parsePhoenemeAnnoDursOracle(lyrics, phonemeListExtracted ):
    
        htkParser = HtkConverter()
        htkParser.load(MODEL_URI, HMM_LIST_URI)
        
        dummyDeviation = 1
        # lyricsWithModelsORacle used only as helper for state durs, but not functionally
        lyricsWithModelsORacle = LyricsWithModels(lyrics, htkParser,  dummyDeviation, ParametersAlgo.WITH_PADDED_SILENCE)
        lyricsWithModelsORacle.setPhonemeDurs( phonemeListExtracted)
        
        return lyricsWithModelsORacle

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
    lenObs = len(observationFeatures)
    chiBackPointer, psiBackPointer = decoder.hmmNetwork._viterbiForcedDur(lenObs)
#   
    decoder.backtrack( chiBackPointer, psiBackPointer)
