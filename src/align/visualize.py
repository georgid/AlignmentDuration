# coding: utf-8

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
open results in praat

visualizes errors for different as graph. matplotlib
'''
import sys
import os
from matplotlib.axes import Axes
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

#  evaluation  
pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if not pathEvaluation in sys.path:
    sys.path.append(pathEvaluation)

# 
# from PraatVisualiser import addAlignmentResultToTextGrid, openTextGridInPraat, addAlignmentResultToTextGridFIle, \
#   _alignmentResult2TextGrid

# from tab2PraatAndOpenWithPRaat import tab2PraatAndOpenWithPRaat 

# from TextGrid_Parsing import tier_names


import matplotlib.pylab as plt
import matplotlib
import numpy as np
ANNOTATION_EXT = '.TextGrid'  


def visualizeBMap(b_Map): 

            matplotlib.interactive(False)

#             plt.figure(figsize=(16,8))
            fig, ax = plt.subplots()
#             ax.imshow(self.B_map, extent=[0, 200, 0, 100], interpolation='none')
            plt.imshow(b_Map, aspect='auto', interpolation='none')

#             plt.colorbar()
#             fig.colorbar()
            ax.autoscale(False)
            plt.title('B_map')
            plt.show(block=True)
            return ax


def visualizeMatrix(psi,  titleName):
#         psi = np.rot90(psi)
#         psi = np.flipud(psi)
#         plt.figure(1)

        fig, ax1 = plt.subplots()
        ax  = plt.imshow(psi, interpolation='none', aspect='auto')
        plt.colorbar(ax)
        plt.grid(True)
        plt.title(titleName)
        figManager = plt.get_current_fig_manager()
        figManager.full_screen_toggle()
        
        matplotlib.rcParams.update({'font.size': 22})
#         plt.tight_layout()
        
#         plt.show() 
        return ax1 

def visualizeTransMatrix(matrix, titleName, phonemesNetwork):
    visualizeMatrix(matrix,  titleName)
    
    listPhonemeNames = []
    for phoneme in phonemesNetwork:
        listPhonemeNames.append(phoneme.ID)
    from numpy.core.numeric import arange
    plt.xticks(arange(len(listPhonemeNames)) , listPhonemeNames )
    plt.yticks(arange(len(listPhonemeNames)) , listPhonemeNames )
    plt.show()

def visualizePath( ax, path, B_map):
    ''' print path on top of existing plot
    '''
            
    if B_map.shape[1] != len(path):
        sys.exit("obs features are {}, but path has duration {}".format(B_map.shape[1], len(path)))
    
    plt.plot(path, marker='x', color='k', markersize=5)
    
    plt.show()





    

def plotStuff():
    # In[14]:
    
    #x - alpha
    alphas = np.arange(0.81,1,0.01)
    
    
    
    #errors for olmaz ilaç
    errorMeans = [ 2.13, 2.13, 2.03, 1.65, 1.44,1.34, 1.3, 1.07, 1.07, 1.06, 1.07, 0.9, 0.9, 0.89, 0.63, 0.13, 0.13, 0.13, 0.12 ]
    errorStDev = [2.18,  2.18, 2.22, 2.13, 2.09, 2.12, 2.14, 1.86, 1.86, 1.86, 1.87, 1.86, 1.85,1.85,  1.75, 0.17, 0.16, 0.17, 0.15]
    
    
    
    # In[15]:
    
    len(alphas)
    
    
    # In[ ]:
    
    
    plt.plot(alphas,errorMeans, 'r^', alphas, errorStDev, 'bs' )
    plt.show()

