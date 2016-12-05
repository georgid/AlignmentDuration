'''
Created on May 28, 2015

@author: joro
'''

### include src folder
import os
import sys
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if parentDir not in sys.path:
    sys.path.append(parentDir)
    
import logging
from numpy.ma.core import  floor
import os
from src.parse.TextGrid_Parsing import tierAliases

######### PARAMS:
class ParametersAlgo(object):
    
    ALPHA = 0.97
    FOR_JINGJU = 0
    FOR_MAKAM = 0
    
    OBS_MODEL = 'GMM'
    OBS_MODEL = 'MLP'
    OBS_MODEL = 'MLP_fuzzy'
    
    EVAL_LEVEL = tierAliases.words 
# eval level  phonemes does not work
#     EVAL_LEVEL = tierAliases.pinyin # in Jingju only level is syllable
                
    # use duraiton-based decoding (HMMDuraiton package) or just plain viterbi (HMM package) 
    # if false, use transition probabilities from htkModels
    WITH_DURATIONS= 1
    
    USE_PERSISTENT_PPGs = 0
    
    # level into which to segments decoded result stateNetwork
#     DETECTION_TOKEN_LEVEL= 'syllables'
    DETECTION_TOKEN_LEVEL= 'words'
#     DETECTION_TOKEN_LEVEL= 'phonemes'
    
    Q_WEIGHT_TRANSITION = 3.5
    
    DECODE_WITH_HTK = 0
    
    GLOBAL_WAIT_PROB = 0.9
    
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
    WITH_PADDED_SILENCE = 0
    
    # no feature vectors at all. all observ, probs. set to 1
#     WITH_ORACLE_PHONEMES = -1
    WITH_ORACLE_PHONEMES = 0

    PATH_TO_HCOPY= '/usr/local/bin/HCopy'
    PATH_TO_HVITE = '/usr/local/bin/HVite'

    # On kora.s.upf.edu
#     PATH_TO_HCOPY = '/homedtic/georgid/htkBuilt/bin/HCopy'
    
    projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.path.pardir ))
    PATH_TO_CONFIG_FILES= projDir + '/models_makam/input_files/'    
    
    parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 
    MODELS_DIR = os.path.join(parentDir, 'models_jingju/' + '3' + 'folds/')
    
    POLYPHONIC = 1
    
    WITH_ORACLE_ONSETS = -1
    ### no onsets at all. 
#     WITH_ORACLE_ONSETS = -1
    
    # Sigma of onset smoothing function g: normal distribution
    ONSET_SIGMA = 0.075
#     ONSET_SIGMA = 0.15
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
    
    ANNOTATION_RULES_ONSETS_EXT = 'annotationOnsets.txt'
    ANNOTATION_SCORE_ONSETS_EXT = 'alignedNotes.txt' # use this ont to get better impression on recall, compared to annotationOnsets.txt, which are only on note onsets with rules of interest 
    
    
    WRITE_TO_FILE = True
    