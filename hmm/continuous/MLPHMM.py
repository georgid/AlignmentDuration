'''
Created on Nov 12, 2012

@author: GuyZ
'''

import numpy


from hmm.continuous._HMM import _HMM
from theano.tensor.shared_randomstreams import RandomStreams
import cPickle
import sys
import os
import math
import csv
from hmm.continuous._ContinuousHMM import _ContinuousHMM
sys.path.append('/Users/joro/Downloads/pdnn')
from io_func import smart_open
from models.dnn import DNN
from io_func.model_io import _file2nnet
import pickle
import tempfile

# from _ContinuousHMM import _ContinuousHMM
# class DurationGMHMM(_ContinuousHMM):
class MLPHMM(_HMM):
    '''
    A MLP HMM - This is a representation of a continuous HMM,
    containing MLP Neural Network in each hidden state.
    
    For more information, refer to _ContinuousHMM.
    '''


        
    def __init__(self, statesNetwork,  transMatrices):
        '''
        See base class constructor for more information
        '''
        _HMM.__init__(self, statesNetwork, transMatrices)
        self._set_MLPs()
        self._load_METU_to_ARPA_mapping()
    
    def _load_METU_to_ARPA_mapping(self):
        mapping_URI = '/Users/joro/Downloads/state_str2int'
        self.METU_to_stateidx = {}
        with open(mapping_URI, 'rb') as csvfile:
            score_ = csv.reader(csvfile, delimiter=' ')
            for idx, row in enumerate(score_):
                self.METU_to_stateidx[row[0]] = int(row[2])
        self.METU_to_stateidx['Y'] = 1 # add short Y
            
    def _set_MLPs(self ):
        '''
        build n GMMs with scikit-learn's classes  
        '''
        nnet_cfg = '/Users/joro/Downloads/dampB.cfg'
        nnet_param = '/Users/joro/Downloads/dampB.mdl' 
        
        numpy_rng = numpy.random.RandomState(89677)
        theano_rng = RandomStreams(numpy_rng.randint(2 ** 30))
        cfg = cPickle.load(smart_open(nnet_cfg,'r'))
        cfg.init_activation()
        self.cfg = cfg
        
        model = DNN(numpy_rng=numpy_rng, theano_rng = theano_rng, cfg = cfg)
    
        # load model parameters
        _file2nnet(model.layers, filename = nnet_param)
        self.model = model
    
    def _mapB(self, observations):
        '''
        extend base method. first load all output with given MLP
        takes time, so better do it in advance to _pdfAllFeatures(), becasue _ContinuousHMM._mapB calls _pdfAllFeatures()
        '''
        self.output_mat = self.recogn_with_MLP( observations)        
        _ContinuousHMM._mapB(self, observations)
        
        
    def _pdfAllFeatures(self,observations,j):
        '''
        get the pdf of a series of features for model j
        '''
#         old_settings = numpy.seterr(under='warn')
        
        curr_phoneme_ID = self.statesNetwork[j].phoneme.ID
        if curr_phoneme_ID not in self.METU_to_stateidx:
                print 'phoneme {} not in dict'.format(curr_phoneme_ID)
                phoneme_idx = 0
        else:
            phoneme_idx = self.METU_to_stateidx[curr_phoneme_ID]
            

        
        probs_phoneme = self.output_mat[:,phoneme_idx]
        logprob = numpy.log(probs_phoneme)
        return logprob  
    
    
    def recogn_with_MLP(self, observations):
        '''
        recognize with model
        return 39-dimensional (for each phoneme from CMU's ARPA ) prob. vector  
        '''
        layer_index  = -1 # last tier
        batch_size = 100

        tmp_dir  = tempfile.mkdtemp()
        tmp_obs_file = os.path.join(tmp_dir, 'observations.pkl')
        labels = numpy.zeros( len(observations), dtype = 'float32')
        
        with open(tmp_obs_file,'w') as f:
            pickle.dump((observations,labels),f)     
            
        self.cfg.init_data_reading_test(tmp_obs_file)

        # get the function for feature extraction
        extract_func = self.model.build_extract_feat_function(layer_index)
    
        output_mats = []    # store the features for all the data in memory. TODO: output the features in a streaming mode
        while (not self.cfg.test_sets.is_finish()):  # loop over the data
            self.cfg.test_sets.load_next_partition(self.cfg.test_xy)
            batch_num = int(math.ceil(1.0 * self.cfg.test_sets.cur_frame_num / batch_size))
    
            for batch_index in xrange(batch_num):  # loop over mini-batches
                start_index = batch_index * batch_size
                end_index = min((batch_index+1) * batch_size, self.cfg.test_sets.cur_frame_num)  # the residue may be smaller than a mini-batch
                output = extract_func(self.cfg.test_x.get_value()[start_index:end_index])
                output_mats.append(output)

        output_mat = numpy.concatenate(output_mats)    
        return output_mat
    
    
    def _pdf(self,x,mean,covar):
        '''
        Gaussian PDF function
        '''        
        covar_det = numpy.linalg.det(covar);
        
        c = (1 / ( (2.0*numpy.pi)**(float(self.d/2.0)) * (covar_det)**(0.5)))
        pdfval = c * numpy.exp(-0.5 * numpy.dot( numpy.dot((x-mean),covar.I), (x-mean)) )
        return pdfval