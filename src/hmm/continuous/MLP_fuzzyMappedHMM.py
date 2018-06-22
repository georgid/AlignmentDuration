# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
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


'''
Created on Dec 1, 2016

@author: joro
'''
from src.hmm.continuous.MLPHMM import MLPHMM
import pickle
from sklearn import mixture
# from numpy import mean, cov
import sys
from scipy.stats._multivariate import multivariate_normal
from src.align.ParametersAlgo import ParametersAlgo
import os

# make sure you download this repo in parent folder
# https://github.com/georgid/makam_acapella
if ParametersAlgo.OBS_MODEL == 'MLP_fuzzy':
    currDir = os.path.abspath( os.path.join( os.path.dirname(os.path.realpath(__file__)) , os.path.pardir, os.path.pardir, os.path.pardir, os.path.pardir ) )
    DIR_PPGs = os.path.join(currDir, 'makam_acapella/phonemeAudio/')

numfolds = 4
which_fold = 1 


 
PHONEMELIST = ['AA' ,'E', 'IY', 'I', 'O', 'U', 'OE', 'UE', 'B', 'D', 'GG', 'H', 'KK', 'LL', 'M', 'NN', 'P', 'RR', 'S', 'SH',\
 'T',  'Y', 'Z', 'C', 'CH', 'F', 'J', 'sil']


class MLP_fuzzyMappedHMM(MLPHMM):
    '''
    A MLP HMM - This is a representation of a continuous HMM,
    containing MLP Neural Network in each hidden state.
    
    For more information, refer to _ContinuousHMM.
    '''


        
    def __init__(self, statesNetwork,  transMatrices):
        '''
        See base class constructor for more information
        '''
        MLPHMM.__init__(self, statesNetwork, transMatrices)

        self._train_fuzzy_GMs()
        
    def _train_fuzzy_GMs(self ):
        '''
        train models.  fit normal ditribution based on pre-extracted posteriograms with MLP 
        NOT OPTIMAL to be done here. could be done offline
        '''
        self.means_ = {}
        self.covars_ = {}
        self.gm = {}
        
        for phoneme in PHONEMELIST: 
            phoneme_URI = DIR_PPGs + str(numfolds) + 'folds/fold'  + str(which_fold) + '/' + phoneme + '.PPG'
            with open(phoneme_URI,'r') as f:
                phoneme_dnn_probs = pickle.load(f)
                
            self.gm[phoneme] = mixture.GaussianMixture(n_components=5)
            self.gm[phoneme].fit(phoneme_dnn_probs)
#             from matplotlib import pyplot
#             pyplot.imshow(phoneme_dnn_probs[:3000,:], aspect='auto', interpolation=None)
#             pyplot.show()
            
#             self.means_[phoneme] = mean(phoneme_dnn_probs,axis=0)
#             self.covars_[phoneme] = cov(phoneme_dnn_probs, rowvar=0,ddof=1) 
    
    def _pdfAllFeatures(self, features,j):
        '''
        pdf by Gaussian distribution
        features are posteriograms: self.mlp_posteriograms before taking log 
        
        -----------------------
        Returns log likelihoods
        
          '''
        ### take posteriogram for phoneme
        curr_phoneme_name = self.statesNetwork[j].phoneme.ID
        
        if curr_phoneme_name not in PHONEMELIST:
                sys.exit('phoneme {} not in dict of models'.format(curr_phoneme_name))
                            

        logprob = self.gm[curr_phoneme_name].score_samples(self.mlp_posteriograms)
#         probs_phoneme = multivariate_normal.logpdf(self.mlp_posteriograms[0,:],self.means_[curr_phoneme_name], self.covars_[curr_phoneme_name])
        
        
        return logprob 