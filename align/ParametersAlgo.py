'''
Created on May 28, 2015

@author: joro
'''
import logging
from numpy.ma.core import  floor
import os

######### PARAMS:
class ParametersAlgo(object):
    
    FOR_JINGJU = 0
    FOR_MAKAM = 0
    
    # use duraiton-based decoding (HMMDuraiton package) or just plain viterbi (HMM package) 
    # if false, use transition probabilities from htkModels
    WITH_DURATIONS= 1
    
    # level into which to segments decoded result stateNetwork
    DETECTION_TOKEN_LEVEL= 'syllables'
    # DETECTION_TOKEN_LEVEL= 'words'
    
    
    DECODE_WITH_HTK = 0
    
    GLOBAL_WAIT_PROB = 0.8
    
    THRESHOLD_PEAKS = -70

    DEVIATION_IN_SEC = 0.1

    # unit: num frames
    NUMFRAMESPERSECOND = 100
    # same as WINDOWSIZE in wavconfig singing. unit:  seconds. TOOD: read from there automatically
    WINDOW_SIZE = 0.025
    
    # in frames
    
    ONLY_MIDDLE_STATE = 1
    
    WITH_SHORT_PAUSES = 0
    
    # padded a short pause state at beginning and end of sequence
    WITH_PADDED_SILENCE = 1
    
    # no feature vectors at all. all observ, probs. set to 1
#     WITH_ORACLE_PHONEMES = -1
    WITH_ORACLE_PHONEMES = 0

    PATH_TO_HCOPY= '/usr/local/bin/HCopy'
    PATH_TO_HVITE = '/usr/local/bin/HVite'

    # On kora.s.upf.edu
#     PATH_TO_HCOPY = '/homedtic/georgid/htkBuilt/bin/HCopy'
    
    projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.path.pardir ))
    PATH_TO_CONFIG_FILES= projDir + '/models_makam/input_files/'    
    
    POLYPHONIC = 1
    
    WITH_ORACLE_ONSETS = -1
    ### no onsets at all. 
#     WITH_ORACLE_ONSETS = -1
    
    # Sigma of onset smoothing function g: normal distribution
    ONSET_SIGMA = 0.075
    ONSET_SIGMA_IN_FRAMES = int(floor(ONSET_SIGMA * NUMFRAMESPERSECOND))
    if ONSET_SIGMA_IN_FRAMES % 2 == 0:
        ONSET_SIGMA_IN_FRAMES += 1
    
#     ONSET_TOLERANCE_WINDOW = 0.02 # seconds. to work implement decoding with one onset only
    ONSET_TOLERANCE_WINDOW = 0 # seconds

    # in _ContinousHMM.b_map cut probabilities
    CUTOFF_BIN_OBS_PROBS = 30
    
    # for for_jingju
    CONSONANT_DURATION_IN_SEC = 0.3
    # for for_makam
#     CONSONANT_DURATION_IN_SEC = 0.1 
    
    CONSONANT_DURATION = NUMFRAMESPERSECOND * CONSONANT_DURATION_IN_SEC;
    
    CONSONANT_DURATION_DEVIATION = 0.7
    
    #####
    LOGGING_LEVEL = logging.INFO
    VISUALIZE = 0
    
    ANNOTATION_ONSETS_EXT = 'annotationOnsets.txt'
