'''
Created on Nov 12, 2012

@author: GuyZ
'''

import numpy


from src.hmm.continuous._HMM import _HMM
from theano.tensor.shared_randomstreams import RandomStreams
import cPickle
import sys
import os
import math
from src.hmm.continuous._ContinuousHMM import _ContinuousHMM

from src.align.evalPhonemes import load_METU_to_ARPA_mapping
from src.align.ParametersAlgo import ParametersAlgo

# sys.path.append('/home/georgid/Documents/pdnn')
currDir = os.path.abspath( os.path.join( os.path.dirname(os.path.realpath(__file__)) , os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir ) )
pdnn_dir = os.path.join(currDir, 'pdnn/')
if pdnn_dir not in sys.path:
    sys.path.append(pdnn_dir)

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
        
        
        METU_to_stateidx_URI = os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.pardir, os.pardir,  'for_makam' , 'state_str2int_METU')
        self.METU_to_stateidx = load_METU_to_ARPA_mapping(METU_to_stateidx_URI)
    

            
    def _set_MLPs(self ):
        '''
        load the MLP learned model as MLP network  
        '''
        nnet_param = os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.pardir, os.pardir,  'models_makam' , 'dampB.mdl')
        nnet_cfg = os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.pardir, os.pardir,  'models_makam' , 'dampB.cfg')

        
        
        numpy_rng = numpy.random.RandomState(89677)
        theano_rng = RandomStreams(numpy_rng.randint(2 ** 30))
        cfg = cPickle.load(smart_open(nnet_cfg,'r'))
        cfg.init_activation()
        self.cfg = cfg
        
        model = DNN(numpy_rng=numpy_rng, theano_rng = theano_rng, cfg = cfg)
    
        # load model parameters
        _file2nnet(model.layers, filename = nnet_param) # this is very slow
        self.model = model
    
    def _mapB(self, features):
        '''
        extend base method. first load all output with given MLP
        takes time, so better do it in advance to _pdfAllFeatures(), becasue _ContinuousHMM._mapB calls _pdfAllFeatures()
        '''
        if not ParametersAlgo.USE_PERSISTENT_PPGs or not os.path.exists(self.PATH_BMAP):
            self.mlp_posteriograms = self.recogn_with_MLP( features) ## posteriograms, no log applied
              
        _ContinuousHMM._mapB(self, features)
        
        
    def _pdfAllFeatures(self,features,j):
        '''
        get the log likelohood of a series of features for model j.
        
        called from _Continuous._mapB()
        
        -----------------------
        Returns log likelihoods
        '''
#         old_settings = numpy.seterr(under='warn')
        
        
        curr_phoneme_ID = self.statesNetwork[j].phoneme.ID
        if curr_phoneme_ID not in self.METU_to_stateidx:
                print 'phoneme {} not in dict'.format(curr_phoneme_ID)
                phoneme_idx = 0
        else:
            phoneme_idx = self.METU_to_stateidx[curr_phoneme_ID] # direct mapping
            

        
        probs_phoneme = self.mlp_posteriograms[:,phoneme_idx]
        logprob = numpy.log(probs_phoneme)
        return logprob  
    
    
    def recogn_with_MLP(self, features):
        '''
        recognize with MLP softmax model
        
        
        Parameters: 
        features 
        
        Return:
        -------------------------- 
        39-dimensional (for each phoneme from CMU's ARPA ) prob. vector, normalized to sum to one for each vector (row) 
        
        '''
        
        self._set_MLPs() # load network
        
        # double check that features are in same dimension as models
        if features.shape[1] != self.model.n_ins:
                sys.exit("dimension of feature vector should be {} but is {} ".format(self.model.n_ins, features.shape[1]) )
        
        ################ recognize
        layer_index  = -1 # last tier
        batch_size = 100

        tmp_dir  = tempfile.mkdtemp()
        tmp_obs_file = os.path.join(tmp_dir, 'features.pkl')
        labels = numpy.zeros( len(features), dtype = 'float32')
        
        with open(tmp_obs_file,'w') as f:
            pickle.dump((features,labels),f)     
            
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