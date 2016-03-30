'''
Created on May 28, 2015

@author: joro
'''
import logging

######### PARAMS:
class ParametersAlgo(object):
    
    THRESHOLD_PEAKS = -70

    DEVIATION_IN_SEC = 0.1

    # unit: num frames
    NUMFRAMESPERSECOND = 100
    # same as WINDOWSIZE in wavconfig singing. unit:  seconds. TOOD: read from there automatically
    WINDOW_SIZE = 0.025
    
    # in frames
    CONSONANT_DURATION = NUMFRAMESPERSECOND * 0.1;
    
    ONLY_MIDDLE_STATE = 1
    
    WITH_SHORT_PAUSES = 1
    
    WITH_PADDED_SILENCE = 1
    
    # no feature vectors at all. all observ, probs. set to 1
    WITH_ORACLE_PHONEMES = -1
    WITH_ORACLE_PHONEMES = 0

    
    POLYPHONIC = 1
    
    WITH_ORACLE_ONSETS = 1
    ### no onsets at all. 
    WITH_ORACLE_ONSETS = -1
    
    ONSET_TOLERANCE_WINDOW = 0.02 # seconds. to work implement decoding with one onset only
#     ONSET_TOLERANCE_WINDOW = 0 # seconds

    # in _ContinousHMM.b_map cut probabilities
    CUTOFF_BIN_OBS_PROBS = 30
    
    
    
    #####
    LOGGING_LEVEL = logging.DEBUG
    VISUALIZE = 0