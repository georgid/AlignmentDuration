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
from for_jingju.ParsePhonemeAnnotation import loadPhonemesAnnoOneSyll
from align.LyricsWithModelsHTK import LyricsWithModelsHTK
from align.LyricsWithModelsGMM import LyricsWithModelsGMM


# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir,os.path.pardir )) 
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir )) 

    
from align.Decoder import Decoder

modelDIR = projDir + '/models_makam/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

from htkparser.htk_converter import HtkConverter














   
            

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
