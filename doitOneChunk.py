'''
Created on Oct 13, 2014

@author: joro
'''
import os
from MakamScore import MakamScore
import glob
import numpy
import sys
from Decoder import Decoder, ONLY_MIDDLE_STATE
from LyricsWithModels import LyricsWithModels
from numpy.core.arrayprint import set_printoptions
import logging

# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )
from Utilz import writeListOfListToTextFile, writeListToTextFile,\
    getMeanAndStDevError

# parser of htk-build speech model
pathHtkModelParser = os.path.join(parentDir, 'pathHtkModelParser')
sys.path.append(pathHtkModelParser)
from htk_converter import HtkConverter


#  evaluation  
pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
sys.path.append(pathEvaluation)
from WordLevelEvaluator import _evalAlignmentError
from PraatVisualiser import openAlignmentInPraat2

# TODO: read mfccs with matlab htk_read
# sys.path.append('/Users/joro/Downloads/python-matlab-bridge-master')
# from pymatbridge import Matlab

numpy.set_printoptions(threshold='nan')

currDir = os.path.abspath(os.path.dirname(os.path.realpath(sys.argv[0])) )
modelDIR = currDir + '/model/'
HMM_LIST_URI = modelDIR +'/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

ANNOTATION_EXT = '.TextGrid'    


def loadLyrics(pathToComposition, whichSection):


#     expand phoneme list from transcript
    os.chdir(pathToComposition)
    pathTotxt = os.path.join(pathToComposition, glob.glob("*.txt")[0])
    pathToSectionTsv =  os.path.join(pathToComposition, glob.glob("*sections.tsv")[0])
    makamScore = MakamScore(pathTotxt, pathToSectionTsv )
    
    # phoneme IDs
    lyrics = makamScore.getLyricsForSection(whichSection)
    return lyrics
    


     

def loadMFCCsWithMatlab(URI_recording_noExt):
    print 'calling matlab'
#     mlab = Matlab(matlab='/Applications/MATLAB_R2009b.app/bin/matlab')
#     mlab.start()
#     res = mlab.run_func('/Users/joro/Documents/Phd/UPF/voxforge/myScripts/lyrics_magic/matlab_htk/writeMFC.m', {'filename':URI_recording_noExt})
#     print res['result']
#     mlab.stop()

def loadMFCCs(URI_recording_noExt): 
    '''
    for now lead extracted with HTK, read in matlab and seriqlized to txt file
    '''
    # first extract features with data.m in Matlab 
    URI_recording_mfc_txt = URI_recording_noExt + '.mfc_txt'
    
    if not os.path.exists(URI_recording_mfc_txt):
#       loadMFCCsWithMatlab(URI_recording_noExt)
        sys.exit('file {} not found. extract features with data.m in Matlab'.format(URI_recording_mfc_txt))
    
    mfccsFeatrues = numpy.loadtxt(URI_recording_mfc_txt , delimiter=','  ) 
    
    return mfccsFeatrues 

def decodeAudioChunk( URI_recording_noExt, decoder, usePersistentFiles):
    
    
    observationFeatures = loadMFCCs(URI_recording_noExt) #     observationFeatures = observationFeatures[0:1000]
    decoder.decodeAudio(observationFeatures, usePersistentFiles, URI_recording_noExt)
    
    
    detectedWordList = decoder.path2ResultWordList()
   

    return detectedWordList




def alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, usePersistentFiles):
    lyrics = loadLyrics(pathToComposition, whichSection)
    lyricsWithModels = LyricsWithModels(lyrics.listWords, htkParser, ONLY_MIDDLE_STATE)
#     lyricsWithModels.printPhonemeNetwork()
    decoder = Decoder(lyricsWithModels)
#  TODO: DEBUG: do not load models
#  decoder = Decoder(lyrics, withModels=False, numStates=86)
#################### decode
    detectedWordList = decodeAudioChunk(URIrecordingNoExt, decoder, usePersistentFiles)

### VISUALIZE
#     decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)

#################### evaluate
    alignmentErrors = _evalAlignmentError(URIrecordingNoExt + '.TextGrid', detectedWordList, 1)
    return alignmentErrors, detectedWordList





def doitOneChunk(argv):
    
    if len(argv) != 4 and  len(argv) != 5 :
            print ("usage: {}  <pathToComposition> <whichSection> <URI_recording_no_ext> <usePersistentFiles=False>".format(argv[0]) )
            sys.exit();
    
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/goekhan/02_Gel_3_zemin'
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL//goekhan/02_Kimseye_5_nakarat'
    URIrecordingNoExt = argv[3]

            
    pathToComposition = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/'
    pathToComposition = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi'
    pathToComposition = argv[1]
    
    whichSection = 5
    whichSection = int(argv[2])
    
    usePersistentFiles = False
    if len(argv) == 5: usePersistentFiles = argv[4]
    
    set_printoptions(threshold='nan') 
    
    ################## load lyrics and models 
    
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    alignmentErrors, detectedWordList = alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, usePersistentFiles)
        
    mean, stDev, median = getMeanAndStDevError(alignmentErrors)
        
    print "mean : ", mean, "st dev: " , stDev

    ### OPTIONAL : open in praat
    openAlignmentInPraat2(detectedWordList,  URIrecordingNoExt + '.TextGrid', URIrecordingNoExt + '.wav')


if __name__ == '__main__':
    doitOneChunk(sys.argv)


