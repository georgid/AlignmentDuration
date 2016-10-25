
'''
Created on Oct 19, 2016
@author: joro
'''
import numpy as np
from parse.TextGrid_Parsing import TextGrid2WordList, readNonEmptyTokensTextGrid
import sys
import pickle
import logging
from align._LyricsWithModelsBase import computeDurationInFrames
from onsets.OnsetDetector import tsToFrameNumber
import numpy
from align._PhonemeBase import PhonemeBase

def eval_percentage_correct_phonemes(phoneme_annotations_list, B_map):
    '''
    Evaluate the percentage of correctly detected phoneme frames
    
    -generates a `B_map_oracle` matrix with same dim as `mapB`  with 1-s at correct phoneme and 0-s otherwise 
    -converts mapB to 1-s at  position of max prob 
    -intersects B_map_oracle and mapB column wise
    
    :param phoneme_annotations_list: list of phonemes as tuples  (  start_ts, end_ts, METU_phoneme)  
    :param mapB: ndarray of N posteriiograms with shape( len(phoneme_annotations_list), len(num_observations)) 
    
    :returns:  
    percentage
     
    '''
    if B_map.shape[0] != len(annotationTokenListNoPauses):
        sys.exit( 'oracle annotations have different size from extracted')
    
    ######## generates a `B_map_oracle`  with same shape as B_map
    B_map_oracle = numpy.zeros((B_map.shape))
    fromTs = 0
    
    next_sane_start_frame = 0
    for idx, phoneme_annotation in enumerate(phoneme_annotations_list): # only for ONLY_MIDDLE_PHONEME = True
        phoneme_ = PhonemeBase(phoneme_annotation[2])
        
        phoneme_.setBeginTs(float(phoneme_annotation[0]))
        phoneme_.setEndTs(float(phoneme_annotation[1]))
        phoneme_.durationInNumFrames = computeDurationInFrames( phoneme_)
                    
        startFrameNumber = tsToFrameNumber(phoneme_.beginTs - fromTs)

        logging.debug("phoneme: {} with start dur: {} and duration: {}".format( phoneme_.ID, startFrameNumber, phoneme_.durationInNumFrames ))
       
        finalDurInFrames = startFrameNumber + phoneme_.durationInNumFrames
        startFrameNumber = max(next_sane_start_frame, startFrameNumber)  # make sure it does not start at same frame
        
        B_map_oracle[idx, startFrameNumber: finalDurInFrames+1 ] = 1
        next_sane_start_frame =  finalDurInFrames+1 
        #TODO: silence at beginning and end
    
    ######## intersects B_map_oracle and mapB column wise


    
    B_map_max = np.zeros(B_map.shape) ###     take max of feature 

    max_vals = np.amax(B_map, axis=0)
    for i in range(B_map.shape[1]):
        max_indices = np.argwhere(B_map[:,i] == max_vals[i])
        B_map_max[max_indices,i]  = 1
    
    result = B_map_max * B_map_oracle # intersect
    print sum(sum(result)) / B_map_oracle.shape[1] 
    
if __name__ == '__main__':
    
    annotationURI = '../example/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/02_Kimseye_51.35423_72.248897.TextGrid'
    tier = 0 # 'phonemes'
    
    dummy, annotationTokenListNoPauses =  readNonEmptyTokensTextGrid(annotationURI, tier)#     load mapB

    with open('/home/georgid/Downloads/02_Kimseye_mapB', 'r') as f:
                    B_map = pickle.load(f)
    
#     with open('/home/georgid/Downloads/02_Kimseye_mapBOracle', 'r') as f1:
#                     B_mapOracle = pickle.load(f1)
                    
    
    eval_percentage_correct_phonemes(annotationTokenListNoPauses, B_map )