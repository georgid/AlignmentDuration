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
import essentia.standard
import math
import json
from onsets.OnsetDetector import OnsetDetector
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



currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )
PATH_TO_CONFIG_FILES= currDir + '/input_files/'

parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

from ParametersAlgo import ParametersAlgo



    





  

class FeatureExtractor(object):
    def __init__(self, path_to_hcopy):
        self.path_to_hcopy = path_to_hcopy
        self.featureVectors = []
        self.onsetDetector = OnsetDetector()
         
   
   
    def loadMFCCs(self, URI_recording_noExt, extractedPitchList, URIRecordingChunkResynthesizedNoExt,  withSynthesis, sectionLink): 
        '''
        for now lead extracted with HTK, read in matlab and seriqlized to txt file
        '''
            
        
    
        URI_recording = URI_recording_noExt + '.wav'
        
        URIRecordingChunkResynthesized = URIRecordingChunkResynthesizedNoExt + '.wav'
        
        logging.info("working on sectionLink: {}".format(URIRecordingChunkResynthesized))
        
        # resynthesize audio chunk:
        if withSynthesis: 
            if not os.path.isfile(URIRecordingChunkResynthesized): # only if resynth file does not exist 
                logging.info("doing harmonic model and resynthesis for segment: {} ...".format(URIRecordingChunkResynthesized))
                
                if extractedPitchList == None:
                    extractedPitchList = self._extractPredominantPitch(URI_recording_noExt)
                hfreq, hmag, hphase, fs, hopSizeMelodia, inputAudioFromTsToTs = extractHarmSpec(URI_recording, extractedPitchList, sectionLink.beginTs, sectionLink.endTs, ParametersAlgo.THRESHOLD_PEAKS)
                resynthesize(hfreq, hmag, hphase, fs, hopSizeMelodia, URIRecordingChunkResynthesized)
        else:
            sampleRate = 44100
            loader = essentia.standard.MonoLoader(filename = URI_recording, sampleRate = sampleRate)
            audio = loader()
            audioChunk = audio[sectionLink.beginTs*sampleRate : sectionLink.endTs*sampleRate]
            monoWriter = essentia.standard.MonoWriter(filename=URIRecordingChunkResynthesized)
            monoWriter(audioChunk)
        
        # call htk to extract features
        URImfcFile = self._extractMFCCs( URIRecordingChunkResynthesized)
        
        # read features form binary htk file
        logging.debug("reading MFCCs from {} ...".format(URImfcFile))
        HTKFeat_reader =  htkmfc.open(URImfcFile, 'rb')
        mfccsFeatrues = HTKFeat_reader.getall()
        mfccs = mfccsFeatrues[:,0:12]
    
        mfccDeltas = mfccsFeatrues[:,13:] 
        mfccsFeatrues = np.hstack((mfccs, mfccDeltas))
        
        
        return mfccsFeatrues, URIRecordingChunkResynthesized
    
            
    def _extractMFCCs( self, URIRecordingChunk):
            baseNameAudioFile = os.path.splitext(os.path.basename(URIRecordingChunk))[0]
            dir_ = os.path.dirname(URIRecordingChunk)
    #         dir_  = tempfile.mkdtemp()
            mfcFileName = os.path.join(dir_, baseNameAudioFile  ) + '.mfc'
            
            HCopyCommand = [self.path_to_hcopy, '-A', '-D', '-T', '1', '-C', PATH_TO_CONFIG_FILES + 'wav_config_singing', URIRecordingChunk, mfcFileName]
    
    #         if not os.path.isfile(mfcFileName):
            logging.info(" Extract mfcc with htk command: {}".format( subprocess.list2cmdline(HCopyCommand) ) )
            pipe= subprocess.Popen(HCopyCommand)
            pipe.wait()
            return mfcFileName
        
    
    def _extractPredominantPitch(self, URI_recording_noExt):
    
        extractedPitchList = []
        ####### melodia format
    #     melodiaInput = URI_recording_noExt + '.melodia'
    #     extractedPitchList = readListOfListTextFile_gen(melodiaInput)
        
        ####### juanjos melody
    #     dirName = os.path.dirname(os.path.realpath(URI_recording_noExt + '.wav'))
    #     os.chdir(dirName)
    # 
    #     pathToPitch = os.path.join(dirName, glob.glob("*.pitch")[0])
    #     f = open(pathToPitch) 
    #     extractedPitchList = []
    #     for line in reader(f):
    #         currLine = []
    #         for e in line:
    #             currLine.append(float(e))
    #         extractedPitchList.append(currLine)
            
    
        
        ####### json serialized array format
    
    #     from compmusic.extractors.makam import pitch
    #     extractor = pitch.PitchExtractMakam()
    #     results = extractor.run(URI_recording_noExt + '.wav')
    #     extractedPitchList = results['pitch']
        
        melodiaInput = URI_recording_noExt + '.pitch'
        with open(melodiaInput) as f:
            extractedPitchList = json.load(f)
        
        
        return extractedPitchList
