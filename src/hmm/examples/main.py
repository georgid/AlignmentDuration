# -*- coding: utf-8 -*-

# Copyright (C) 2014-2018  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/




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
from src.align.ParametersAlgo import ParametersAlgo
import logging
from src.align.LyricsParsing import loadOraclePhonemes
from src.for_jingju.ParsePhonemeAnnotation import loadPhonemesAnnoOneSyll
from src.align.LyricsWithModelsHTK import LyricsWithModelsHTK
from src.align.LyricsWithModelsGMM import LyricsWithModelsGMM


# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir,os.path.pardir )) 
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir )) 

    
from src.align.Decoder import Decoder

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
    decoder = Decoder(lyricsWithModels, URIrecordingNoExt)
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
