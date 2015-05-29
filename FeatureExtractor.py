'''
Created on May 27, 2015

@author: joro
'''
import os
import sys
import numpy as np
import logging

import htkmfc
from Constants import NUM_FRAMES_PERSECOND
import subprocess
from matplotlib.colors import NP_CLIP_OUT
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathSMS = os.path.join(parentDir, 'sms-tools/workspace')


if pathSMS not in sys.path:
    sys.path.append(pathSMS)
from harmonicModel_function import extractHarmSpec, resynthesize

pathUtils = os.path.join(parentDir, 'utilsLyrics')
if pathUtils not in sys.path:
    sys.path.append(pathUtils)

import UtilzNumpy

PATH_TO_HCOPY= '/usr/local/bin/HCopy'
PATH_TO_CONFIG_FILES= '/Users/joro/Documents/Phd/UPF/voxforge/auto/scripts/input_files/'

parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 
pathJingju = os.path.join(parentParentDir, 'Jingju')

if pathJingju not in sys.path:
    sys.path.append(pathJingju )
from ParametersAlgo import THRESHOLD_PEAKS

def loadMFCCsWithMatlab(URI_recording_noExt):
    print 'calling matlab'
#     mlab = Matlab(matlab='/Applications/MATLAB_R2009b.app/bin/matlab')
#     mlab.start()
#     res = mlab.run_func('/Users/joro/Documents/Phd/UPF/voxforge/myScripts/lyrics_magic/matlab_htk/writeMFC.m', {'filename':URI_recording_noExt})
#     print res['result']
#     mlab.stop()

def loadMFCCs(URI_recording_noExt, fromTs, toTs): 
    '''
    for now lead extracted with HTK, read in matlab and seriqlized to txt file
    '''
    # resynthesize audio chunk:
    melodiaInput = URI_recording_noExt + '.melodia.txt'
    URI_recording = URI_recording_noExt + '.wav'
    
    URIRecordingChunk = URI_recording_noExt + "_" + str(fromTs) + '_' + str(toTs) + '.wav'
    
    if fromTs==-1 and toTs==-1:
        # TODO
        fromTs=0; toTs=2
        sys.exit("fromTs and toTs not defined")
        
    hfreq, hmag, hphase, fs, hopSizeMelodia, inputAudioFromTsToTs = extractHarmSpec(URI_recording, melodiaInput, fromTs, toTs, THRESHOLD_PEAKS)
    resynthesize(hfreq, hmag, hphase, fs, hopSizeMelodia, URIRecordingChunk)


        
    # call htk to extract features
    URImfcFile = _extractFeatures( URIRecordingChunk)
    
    # read features form binary htk file
    logging.debug("reading MFCCs from {} ...".format(URImfcFile))
    HTKFeat_reader =  htkmfc.open(URImfcFile, 'rb')
    mfccsFeatrues = HTKFeat_reader.getall()
    mfccs = mfccsFeatrues[:,0:12]

    mfccDeltas = mfccsFeatrues[:,13:] 
    mfccsFeatrues = np.hstack((mfccs, mfccDeltas))
        
    # first extract features with data.m in Matlab 
#     URI_recording_mfc_txt = URIRecordingChunk + '.mfc_txt'
#     
#     if not os.path.exists(URI_recording_mfc_txt):
# #       loadMFCCsWithMatlab(URI_recording_noExt)
#         sys.exit('file {} not found. extract features with data.m in Matlab'.format(URI_recording_mfc_txt))
#     mfccsFeatrues2 = np.loadtxt(URI_recording_mfc_txt , delimiter=','  ) 
#     
#     UtilzNumpy.areArraysEqual(mfccsFeatrues, mfccsFeatrues2)
    
    
    return mfccsFeatrues

def _extractFeatures( URIRecordingChunk):
        baseNameAudioFile = os.path.splitext(os.path.basename(URIRecordingChunk))[0]
        dir_ = os.path.dirname(URIRecordingChunk)
        mfcFileName = os.path.join(dir_, baseNameAudioFile  ) + '.mfc'
        
        HCopyCommand = [PATH_TO_HCOPY, '-A', '-D', '-T', '1', '-C', PATH_TO_CONFIG_FILES + 'wav_config_singing', URIRecordingChunk, mfcFileName]
#         if not os.path.isfile(mfcFileName):
        pipe= subprocess.Popen(HCopyCommand)
        pipe.wait()
        return mfcFileName


if __name__ == '__main__':
    
    URI_noExt =   '/Users/joro/Documents/Phd/UPF/arias/laosheng-erhuang_04'

    loadMFCCs(URI_noExt, 55, 58)
        