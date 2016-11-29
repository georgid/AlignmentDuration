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

### include src folder
import os
import sys
projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if projDir not in sys.path:
    sys.path.append(projDir)

from ParametersAlgo import ParametersAlgo
import tempfile
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir, os.path.pardir)) 
pathSMS = os.path.join(parentDir, 'sms-tools')
from predominantmelodymakam.predominantmelodymakam import PredominantMelodyMakam

# print '\n sys.path:' + sys.path +  '\n'
# if pathSMS not in sys.path:
#     sys.path.append(pathSMS)

from src.smstools.workspace.harmonicModel_function import extractHarmSpec, resynthesize
# from harmonicModel_function import extractHarmSpec, resynthesize


from src.utilsLyrics.Utilz import readListOfListTextFile_gen, writeCsv
import src.utilsLyrics.UtilzNumpy



projDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__)) , os.path.pardir ))



parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

from ParametersAlgo import ParametersAlgo



class FeatureExtractor(object):
    def __init__(self, path_to_hcopy, sectionLink):
        self.path_to_hcopy = path_to_hcopy
        self.featureVectors = []
         
   
   
    def loadMFCCs(self, URI_recording_noExt, extractedPitchList,    sectionLink): 
        '''
        for now lead extracted with HTK, read in matlab and seriqlized to txt file
        '''
            
        
    
        URI_recording = URI_recording_noExt + '.wav'
        
        URIRecordingChunkResynthesized = sectionLink.URIRecordingChunk + '.wav'
        
        logging.info("working on sectionLink: {}".format(URIRecordingChunkResynthesized))
        
        # resynthesize audio chunk:
        if ParametersAlgo.POLYPHONIC: 
            if not os.path.isfile(URIRecordingChunkResynthesized): # only if resynth file does not exist 
                logging.info("doing harmonic models and resynthesis for segment: {} ...".format(URIRecordingChunkResynthesized))
                
                if extractedPitchList == None:
                    extractedPitchList = extractPredominantPitch(URI_recording_noExt)
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
        
        if ParametersAlgo.FOR_MAKAM and ParametersAlgo.OBS_MODEL == 'GMM': # makam mdoels  are trained with 25-dim features (no energy, no deltadeltas )
            mfccs_no_energy = mfccsFeatrues[:,0:12]
            mfccDeltas = mfccsFeatrues[:,13:26] 
            mfccsFeatrues = np.hstack((mfccs_no_energy, mfccDeltas))
        
        
        return mfccsFeatrues
    
            
    def _extractMFCCs( self, URIRecordingChunk):
            baseNameAudioFile = os.path.splitext(os.path.basename(URIRecordingChunk))[0]
            dir_ = os.path.dirname(URIRecordingChunk)
#             dir_  = tempfile.mkdtemp()
            mfcFileName = os.path.join(dir_, baseNameAudioFile  ) + '.mfc'
            
            if ParametersAlgo.OBS_MODEL == 'MLP': # only one type of features trained
               PATH_TO_CONFIG_FEATURES = projDir + '/models_makam/input_files/wav_config_default'
            elif  ParametersAlgo.OBS_MODEL == 'GMM':  
                if ParametersAlgo.FOR_JINGJU:
                    PATH_TO_CONFIG_FEATURES = projDir + '/models_makam/input_files/wav_config_singing_yile' # no singal amplitude normalization
    
                elif ParametersAlgo.FOR_MAKAM:
                    PATH_TO_CONFIG_FEATURES = projDir + '/models_makam/input_files/wav_config_singing_makam'
                
            
            HCopyCommand = [self.path_to_hcopy, '-A', '-D', '-T', '1', '-C', PATH_TO_CONFIG_FEATURES, URIRecordingChunk, mfcFileName]
    
            if not os.path.isfile(mfcFileName):
                logging.info(" Extract mfcc with htk command: {}".format( subprocess.list2cmdline(HCopyCommand) ) )
                pipe= subprocess.Popen(HCopyCommand)
                pipe.wait()
            
            return mfcFileName
        
    
def extractPredominantPitch( URI_recording_noExt):
        '''
        extract pitch using local version of pycompmusic and save as csv as input 
        used as inpu to  note segmentation algo
        '''
        logging.debug( 'extracting pitch for {}...'.format(URI_recording_noExt))

        extractedPitchList = []
        ####### melodia format
      
      ############## LOAD from already extracted locally
#         melodiaInput = URI_recording_noExt + '.pitch'
#         with open(melodiaInput) as f:
#             extractedPitchList = json.load(f)
    #     extractedPitchList = readListOfListTextFile_gen(melodiaInput)
   
        ########## EXTRACT NOW
        extractor = PredominantMelodyMakam()
        results = extractor.run(URI_recording_noExt)
        extractedPitchList = results['pitch']
    
    ############# load from extractor output on server
#     try:
#         pitch_data = dunya.docserver.get_document_as_json(musicbrainzid, "jointanalysis", "pitch", 1, version="0.1")
#         extractedPitchList = pitch_data['pitch']
#     except:
#         logging.error("no initialmakampitch series could be downloaded. for rec  {}".format(musicbrainzid))
#         return None
    
    
        ######## SERIALIZE
        # ignore last entry (probability)
        for i, row in enumerate(extractedPitchList):
            row = row[:-1]
            extractedPitchList[i]=row
        
        outFileURI = os.path.splitext(URI_recording_noExt)[0] + '.pitch.csv'
        writeCsv(outFileURI, extractedPitchList)

        
        
        return extractedPitchList
