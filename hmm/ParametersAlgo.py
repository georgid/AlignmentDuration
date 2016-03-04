'''
Created on May 28, 2015

@author: joro
'''

######### PARAMS:
class ParametersAlgo(object):
    THRESHOLD_PEAKS = -70

    DEVIATION_IN_SEC = 0.1

    # unit: num frames
    NUMFRAMESPERSECOND = 100
    # same as WINDOWSIZE in wavconfig singing. unit:  seconds. TOOD: read from there automatically
    WINDOW_SIZE = 0.25
    
    # in frames
    CONSONANT_DURATION = NUMFRAMESPERSECOND * 0.1;
    
    ONLY_MIDDLE_STATE = 0
    
    WITH_SHORT_PAUSES = 1
    
    WITH_PADDED_SILENCE = 1
    
    WITH_ORACLE = 1
    
    