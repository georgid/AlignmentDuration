'''
Created on May 28, 2015

@author: joro
'''
import os

######### PARAMS:
class ParametersAlgo(object):
    THRESHOLD_PEAKS = -70

    DEVIATION_IN_SEC = 2.0

    # unit: num frames
    NUMFRAMESPERSECOND = 100
    
    CONSONANT_DURATION_IN_SEC = 0.3
    CONSONANT_DURATION = NUMFRAMESPERSECOND * CONSONANT_DURATION_IN_SEC;
    
    CONSONANT_DURATION_DEVIATION = 0.7
    
    currDir = os.path.abspath( os.path.dirname(os.path.realpath(__file__)))
    parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

    
    MODELS_DIR = parentDir + '/models_jingju/15folds/'

    