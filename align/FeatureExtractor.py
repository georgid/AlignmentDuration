'''
Created on May 27, 2015

@author: joro
'''
import os
import sys
import numpy as np
import logging

import htkmfc
import subprocess
from Decoder import logger
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir, os.path.pardir)) 
pathSMS = os.path.join(parentDir, 'sms-tools')
import tempfile

# print '\n sys.path:' + sys.path +  '\n'
# if pathSMS not in sys.path:
#     sys.path.append(pathSMS)

from smstools.workspace.harmonicModel_function import extractHarmSpec, resynthesize
# from harmonicModel_function import extractHarmSpec, resynthesize


from utilsLyrics.Utilz import readListOfListTextFile_gen
import utilsLyrics.UtilzNumpy

PATH_TO_HCOPY= '/usr/local/bin/HCopy'
# ANDRES. On kora.s.upf.edu
# PATH_TO_HCOPY= '/srv/htkBuilt/bin/HCopy'

currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )
PATH_TO_CONFIG_FILES= currDir + '/input_files/'

parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

from hmm.ParametersAlgo import ParametersAlgo





def loadMFCCs(URI_recording_noExt, extractedPitchList, URIRecordingChunkResynthesizedNoExt,  withSynthesis, sectionLink): 
    '''
    for now lead extracted with HTK, read in matlab and seriqlized to txt file
    '''
        
#     extractedPitchList = _extractPredominantPitch(URI_recording_noExt)
    

    URI_recording = URI_recording_noExt + '.wav'
    
    URIRecordingChunkResynthesized = URIRecordingChunkResynthesizedNoExt + '.wav'
    
    logger.setLevel(logging.INFO)
    logger.info("working on sectionLink: {}".format(URIRecordingChunkResynthesized))
    
    # resynthesize audio chunk:
    if withSynthesis: 
        if not os.path.isfile(URIRecordingChunkResynthesized): # only if resynth file does not exist 
            logger.info("doing harmonic model and resynthesis for segment: {} ...".format(URIRecordingChunkResynthesized))

            hfreq, hmag, hphase, fs, hopSizeMelodia, inputAudioFromTsToTs = extractHarmSpec(URI_recording, extractedPitchList, sectionLink.beginTs, sectionLink.endTs, ParametersAlgo.THRESHOLD_PEAKS)
            resynthesize(hfreq, hmag, hphase, fs, hopSizeMelodia, URIRecordingChunkResynthesized)
    
        # NOT IMPLEMENTED
#     else:
#         # TODO take only part from audio with essentia
#          print "!!! extracting features from whole audio{}".format(URI_recordingChunk_noExt)
#          URIRecordingChunkResynthesized = URI_recordingChunk_noExt + '.wav'
        
    # call htk to extract features
    URImfcFile = _extractMFCCs( URIRecordingChunkResynthesized)
    
    # read features form binary htk file
    logging.debug("reading MFCCs from {} ...".format(URImfcFile))
    HTKFeat_reader =  htkmfc.open(URImfcFile, 'rb')
    mfccsFeatrues = HTKFeat_reader.getall()
    mfccs = mfccsFeatrues[:,0:12]

    mfccDeltas = mfccsFeatrues[:,13:] 
    mfccsFeatrues = np.hstack((mfccs, mfccDeltas))
    
    
    return mfccsFeatrues, URIRecordingChunkResynthesized


def _extractPredominantPitch(URI_recording_noExt):
    
    extractedPitchList = []
    ####### melodia format
#     melodiaInput = URI_recording_noExt + '.melodia'
#     extractedPitchList = readListOfListTextFile_gen(melodiaInput)
    
    ####### json serialized array format

#     from compmusic.extractors.makam import pitch
#     extractor = pitch.PitchExtractMakam()
#     results = extractor.run(URI_recording_noExt + '.wav')
#     extractedPitchList = json.loads(results['pitch'])
    
#     melodiaInput = URI_recording_noExt + '.pitch'
#     with open(melodiaInput) as f:
#         extractedPitchList = json.load(f)
    
    
    return extractedPitchList

def _extractMFCCs( URIRecordingChunk):
        baseNameAudioFile = os.path.splitext(os.path.basename(URIRecordingChunk))[0]
        dir_ = os.path.dirname(URIRecordingChunk)
#         dir_  = tempfile.mkdtemp()
        mfcFileName = os.path.join(dir_, baseNameAudioFile  ) + '.mfc'
        
        HCopyCommand = [PATH_TO_HCOPY, '-A', '-D', '-T', '1', '-C', PATH_TO_CONFIG_FILES + 'wav_config_singing', URIRecordingChunk, mfcFileName]

        if not os.path.isfile(mfcFileName):
            logger.info(" Extract mfcc with htk command: {}".format( subprocess.list2cmdline(HCopyCommand) ) )
            pipe= subprocess.Popen(HCopyCommand)
            pipe.wait()
        return mfcFileName



        