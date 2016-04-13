# -*- coding: utf-8 -*-

'''
Created on Nov 13, 2012

@author: GuyZ
'''

import numpy

from hmm.continuous.GMHMM import GMHMM
from hmm.discrete.DiscreteHMM import DiscreteHMM
import os
import sys
from hmm.Parameters import Parameters
from hmm.continuous.DurationPdf import NUMFRAMESPERSEC

# parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir, os.path.pardir)) 
# pathJingju = os.path.join(parentParentDir, 'Jingju')
# 
# if pathJingju not in sys.path:
#     sys.path.append(pathJingju )
from hmm.Path import Path
from hmm.ParametersAlgo import ParametersAlgo
import logging


# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir,os.path.pardir )) 
print parentDir

pathJingjuAlignment = os.path.join(parentDir, 'AlignmentDuration')
if not pathJingjuAlignment in sys.path:
    sys.path.append(pathJingjuAlignment)
    
from Phonetizer import Phonetizer
from MakamScore import loadLyrics

from LyricsWithGMMs import LyricsWithGMMs

from LyricsWithHTKModels import LyricsWithHTKModels


from Decoder import Decoder
from FeatureExtractor import loadMFCCs

modelDIR = pathJingjuAlignment + '/model/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

# parser of htk-build speech model
# pathHtkModelParser = os.path.join(parentDir, 'pathHtkModelParser')
# sys.path.append(pathHtkModelParser)
from htkparser.htk_converter import HtkConverter





def loadSmallAudioFragment(lyrics, withHTK, URIrecordingNoExt, withSynthesis, fromTs=-1, toTs=-1):
    '''
    test duration-explicit HMM with audio features from real recording and htk-loaded model
    asserts it works. no results provided 
    '''
    observationFeatures, URIRecordingChunk = loadMFCCs(URIrecordingNoExt, withSynthesis, fromTs, toTs) #     observationFeatures = observationFeatures[0:1000]

    if withHTK:
        htkParser = HtkConverter()
        htkParser.load(MODEL_URI, HMM_LIST_URI)
    
        lyricsWithModels = LyricsWithHTKModels(lyrics, htkParser, 'False', ParametersAlgo.DEVIATION_IN_SEC)
     
    else:
        lyricsWithModels = LyricsWithGMMs(lyrics,  'True', ParametersAlgo.DEVIATION_IN_SEC, URIrecordingNoExt)

    if lyricsWithModels.getTotalDuration() == 0:
        logging.warning("total duration of segment {} = 0".format(URIRecordingChunk))
        return None, None, None
    
    lyricsWithModels.duration2numFrameDuration(observationFeatures, URIrecordingNoExt)
#     lyricsWithModels.printPhonemeNetwork()

    return lyricsWithModels, observationFeatures, URIRecordingChunk



def loadSmallAudioFragmentOracle(URIrecordingNoExt, lyrics, phonemeAnnotaions ):

        
        # lyricsWithModelsORacle used only as helper for state durs, but not functionally
        lyricsWithModelsORacle = LyricsWithGMMs(lyrics,  'True', ParametersAlgo.DEVIATION_IN_SEC, URIrecordingNoExt)
        lyricsWithModelsORacle.setPhonemeNumFrameDurs( phonemeAnnotaions)
        
        return lyricsWithModelsORacle


def getDecoder(lyricsWithModels, URIrecordingNoExt):
    '''
    helper routine to init decoder. change here parameters
    '''
    alpha = 0.97
    ONLY_MIDDLE_STATE=False
    withHTK = 1
    params = Parameters(alpha, ONLY_MIDDLE_STATE)
    decoder = Decoder(lyricsWithModels, URIrecordingNoExt, withHTK, params.ALPHA)
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
    withOracle = 0  
    decoder.backtrack(withOracle, chiBackPointer, psiBackPointer)



