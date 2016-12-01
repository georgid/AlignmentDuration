
'''
Created on Oct 19, 2016
@author: joro
'''
import numpy as np


import sys
import pickle
import logging
import numpy
import os
import csv
from sys import argv
import math
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from Constants import NUM_FRAMES_PERSECOND

### include src folder
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if parentDir not in sys.path:
    sys.path.append(parentDir)

from src.onsets.OnsetDetector import tsToFrameNumber
from src.parse.TextGrid_Parsing import TextGrid2WordList, readNonEmptyTokensTextGrid,\
    divideIntoSentencesFromAnnoWithSil, tierAliases
from _PhonemeBase import PhonemeBase




def eval_percentage_correct_phonemes(phoneme_annotations_URI, B_map_URI, phoneme2idx_URI=None, curr_section_counter=1):
    '''
    Evaluate the percentage of correctly detected phoneme frames
    
    -generates a `B_map_oracle` matrix with same dim as `mapB`  with 1-s at correct phoneme and 0-s otherwise 
    -converts mapB to 1-s at  position of max prob 
    -intersects B_map_oracle and mapB column wise
    
    :param phoneme_annotations_list: URI to csv of list of phonemes as tuples  (  start_ts, end_ts, METU_phoneme) 
     or URI to TextGrid and tier name. reads all phonemes from TextGrid at tier names phoenemes
    :param mapB: ndarray of N posteriiograms with shape( num_phonemes_in_dict, len(num_observations)) 
    :param phoneme2idx_URI: phoneme to idx. The order in posteriograms is as in this index list, if None, posteriograms have same order as in annotation (with repeating phonemes)
    
    :returns:  
    percentage
     
    '''
    if phoneme2idx_URI != None:
        phoneme2idx = load_METU_to_ARPA_mapping(phoneme2idx_URI)
#     if B_map.shape[0] != len(annotationTokenListNoPauses):
#         sys.exit( 'oracle annotations have different size from extracted')
    
    
    ######## generates a `B_map_oracle`  with same shape as B_map
    with open(B_map_URI,'r') as f:
                    B_map = pickle.load(f)
    if B_map.shape[0] > B_map.shape[1]:
        # shifting B_map
        B_map =  B_map.T
    B_map_oracle = numpy.zeros((B_map.shape))
    fromTs = 0
    
    ####### parse annotation    
    phoneme_annotations_list = parse_annotation(phoneme_annotations_URI, curr_section_counter)
    
    ###### create B_map oracle from annotation 
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
        
        if phoneme2idx_URI != None: # order comes from state_str2
            idx = phoneme2idx[phoneme_.ID]
        B_map_oracle[idx, startFrameNumber: finalDurInFrames+1 ] = 1
        next_sane_start_frame =  finalDurInFrames+1 
        #TODO: silence at beginning and end
    
    ######## intersects B_map_oracle and mapB column wise
    
    B_map_max = np.zeros(B_map.shape) 

    max_vals = np.amax(B_map, axis=0) ###     take max of feature 
    for i in range(B_map.shape[1]):
        max_indices = np.argwhere(B_map[:,i] == max_vals[i])
        B_map_max[max_indices,i]  = 1
    

    
    result = B_map_max * B_map_oracle # intersect
    return sum(sum(result)) / B_map_oracle.shape[1], B_map


def parse_annotation(phoneme_annotations_URI, curr_section_counter):
    '''
    parse phoneneme timestamps for one structural section 
    
    Parameters
    ------
    phoneme_annotations_URI: str
        URI to file with phoneme annos 
    curr_section_counter: int
        consecutive number of section (structural part) in file
    
    Return
    ------------
    list of tuples (startTs,  endTs, Phoneme ID)
    
    '''
    
    if phoneme_annotations_URI.endswith('.TextGrid'):
        list_start_end_indices, annotation_lines_list = divideIntoSentencesFromAnnoWithSil(phoneme_annotations_URI, tierAliases.line, tierAliases.phonemes)
        start_idx = list_start_end_indices[curr_section_counter][0]
        end_idx = list_start_end_indices[curr_section_counter][1]
        line_start_time =  annotation_lines_list[curr_section_counter][0]
        dummy, phoneme_annotations_list = readNonEmptyTokensTextGrid(phoneme_annotations_URI, tierAliases.phonemes, start_idx, end_idx, -line_start_time) #     load mapB
    else:
        phoneme_annotations_list = read_csv(phoneme_annotations_URI) # there should not be empty words
    return phoneme_annotations_list

def computeDurationInFrames(phonemeAnno):
        '''
        compute Duration from annotation token 
        '''
        durationInSec = float(phonemeAnno.endTs) - float(phonemeAnno.beginTs)
        durationInFrames = math.floor(durationInSec * NUM_FRAMES_PERSECOND)
        return durationInFrames
    

def load_METU_to_ARPA_mapping(METU_to_stateidx_URI):
        '''
        METU phoneme corresponds to which idx in trained model 
        '''

        METU_to_stateidx = {}
        
        with open(METU_to_stateidx_URI, 'rb') as csvfile:
            score_ = csv.reader(csvfile, delimiter=' ')
            for row in score_:
                    METU_to_stateidx[row[0]] = int(row[-1])
        METU_to_stateidx['Y'] = 1 # add short Y
        return METU_to_stateidx

def display(perc_correct, B_map_max):
    print 'perc correct = ' + str(perc_correct)
    
    import matplotlib.pyplot as plt
    plt.imshow(B_map_max, interpolation='none', aspect='auto')
    plt.colorbar()
    plt.show()  
    
def read_csv(annotation_URI):
  
        anno_phonemes = []
        with open(annotation_URI, 'rb') as csvfile:
            score_ = csv.reader(csvfile, delimiter='\t')
            for row in score_:
                anno_phonemes.append((float(row[0]), float(row[1]),  row[2].lower() ) )
        return anno_phonemes
    
if __name__ == '__main__':
    
    if len(sys.argv) != 4:
            print ("Tool to get alignment accuracy of one for_jingju aria with different parameters ")
            print ("usage: {}     <path to annotation> <path_to_posteriograms PPG> <URI_state2str_idx>".format(argv[0]) )
            sys.exit()
            
    annotationURI = sys.argv[1]
    B_map_URI = sys.argv[2]
    METU_to_stateidx_URI = sys.argv[3]
    
  
                    
    perc_correct, B_map_max = eval_percentage_correct_phonemes(annotationURI, B_map_URI, METU_to_stateidx_URI )
    display(perc_correct, B_map_max)
  

