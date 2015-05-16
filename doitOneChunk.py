'''
Created on Oct 13, 2014

@author: joro
'''
import os
from MakamScore import  loadLyrics
import glob
import numpy
import sys
from LyricsWithModels import LyricsWithModels
from numpy.core.arrayprint import set_printoptions
from Parameters import Parameters
from Decoder import Decoder, WITH_DURATIONS, logger
from LyricsParsing import expandlyrics2WordList, _constructTimeStampsForWord, testT
from Constants import NUM_FRAMES_PERSECOND, AUDIO_EXTENSION
from Phonetizer import Phonetizer



# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )
from Utilz import writeListOfListToTextFile, writeListToTextFile,\
    getMeanAndStDevError, getSectionNumberFromName, readListOfListTextFile

# parser of htk-build speech model
pathHtkModelParser = os.path.join(parentDir, 'pathHtkModelParser')
sys.path.append(pathHtkModelParser)
from htk_converter import HtkConverter

# Alignment with HTK
pathAlignmentStep = os.path.join(parentDir, 'AlignmentStep')
if not pathAlignmentStep in sys.path:
    sys.path.append(pathAlignmentStep)
from Aligner import Aligner 

#  evaluation  
pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
sys.path.append(pathEvaluation)
from WordLevelEvaluator import _evalAlignmentError, evalAlignmentError, tierAliases, determineSuffix
from AccuracyEvaluator import _evalAccuracy, evalAccuracy
from TextGrid_Parsing import TextGrid2WordList
from PraatVisualiser import tokenList2TabFile

# TODO: read mfccs with matlab htk_read
# sys.path.append('/Users/joro/Downloads/python-matlab-bridge-master')
# from pymatbridge import Matlab

numpy.set_printoptions(threshold='nan')

currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )
modelDIR = currDir + '/model/'
HMM_LIST_URI = modelDIR + '/monophones0'
MODEL_URI = modelDIR + '/hmmdefs9gmm9iter'

ANNOTATION_EXT = '.TextGrid'    
AUDIO_EXT = '.wav'







def doitOneChunk(argv):
    
    if len(argv) != 8 and  len(argv) != 9 :
            print ("usage: {}  <pathToComposition> <URI_recording_no_ext> <withDuration=True> <withSynthesis> <ALPHA> <ONLY_MIDDLE_STATE> <evalLevel> <usePersistentFiles=True>".format(argv[0]) )
            sys.exit();
    
    
    URIrecordingNoExt = argv[2]
    whichSection = getSectionNumberFromName(URIrecordingNoExt) 

    pathToComposition = argv[1]
    withDuration = argv[3]
    if withDuration=='True':
        withDuration = True
    elif withDuration=='False':
        withDuration = False
    else: 
        sys.exit("withDuration can be only True or False")  
    
    withSynthesis = argv[4]
    if withSynthesis=='True':
        withSynthesis = True
    elif withSynthesis=='False':
        withSynthesis = False
    else: 
        sys.exit("withSynthesis can be only True or False")  
    
    
    ALPHA = float(argv[5])
    ONLY_MIDDLE_STATE = argv[6]
    
    evalLevel = tierAliases.wordLevel
    evalLevel = int(argv[7])

    params = Parameters(ALPHA, ONLY_MIDDLE_STATE)
    
    usePersistentFiles = 'True'
    if len(argv) == 9:
        usePersistentFiles =  argv[8]
    
    
    set_printoptions(threshold='nan') 
    
    ################## load lyrics and models 
    htkParser = None
    if withDuration:
        htkParser = HtkConverter()
        htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    alignmentErrors,  detectedAlignedfileName, correctDuration, totalDuration, correctDurationScoreDev = alignDependingOnWithDuration(URIrecordingNoExt, whichSection, pathToComposition, withDuration, withSynthesis, evalLevel, params, usePersistentFiles, htkParser)
        
        
    mean, stDev, median = getMeanAndStDevError(alignmentErrors)
    logger.info("mean : {} st dev: {} ".format( mean,stDev))
    logger.info("result: {}".format(detectedAlignedfileName))

#     visualiseInPraat(URIrecordingNoExt, withDuration, detectedAlignedfileName,  detectedWordList, grTruthDurationWordList)

    


def alignDependingOnWithDuration(URIrecordingNoExt, whichSection, pathToComposition, withDuration, withSynthesis, evalLevel, params, usePersistentFiles, htkParser):
    '''
    call alignment method depending on whether duration or htk  selected 
    '''
    if withSynthesis:
        Phonetizer.initLookupTable(withSynthesis,  'grapheme2METUphonemeLookupTableSYNTH')
    else:
        Phonetizer.initLookupTable(withSynthesis,  'grapheme2METUphonemeLookupTable')
    
    tokenLevelAlignedSuffix, phonemesAlignedSuffix = determineSuffix(withDuration, withSynthesis, evalLevel)
    
    ##############################
    ## load lyrics for section
    lyrics = loadLyrics(pathToComposition, whichSection)
    lyricsStr = lyrics.__str__()
        
    if not lyricsStr or lyricsStr=='None' or  lyricsStr =='_SAZ_':
            logger.warn("skipping section {} with no lyrics ...".format(whichSection))
            return [], 'dummy', 0, 0, 0
    
    logger.info("aligning audio {}".format(URIrecordingNoExt))
    lyricsWithModels = LyricsWithModels(lyrics, htkParser, params.ONLY_MIDDLE_STATE)
    
    observationFeatures = loadMFCCs(URIrecordingNoExt) #     observationFeatures = observationFeatures[0:1000]
    
    if WITH_DURATIONS:
            lyricsWithModels.duration2numFrameDuration(observationFeatures, URIrecordingNoExt)
        
    ##############
    ## reference duration
    correctDurationScoreDev, totalDuration  = getReferenceDurations(URIrecordingNoExt, lyricsWithModels, evalLevel)
    
    if withDuration:

        alignmentErrors, detectedTokenList, correctDuration, totalDuration = alignOneChunk(URIrecordingNoExt, lyricsWithModels, params.ALPHA, evalLevel, usePersistentFiles, tokenLevelAlignedSuffix)

            
    else:
        URIrecordingAnno = URIrecordingNoExt + ANNOTATION_EXT
        URIrecordingWav = URIrecordingNoExt + AUDIO_EXTENSION
        # new makamScore used
#         lyricsObj = loadLyrics(pathToComposition, whichSection)
#         lyrics = lyricsObj.__str__()
# #         in case  we are at no-lyrics section
#         if not lyrics or lyrics=='None' or  lyrics =='_SAZ_':
#             logger.warn("skipping section {} with no lyrics ...".format(whichSection))
#             return [], [], [], []
    
        outputHTKPhoneAlignedURI = Aligner.alignOnechunk(MODEL_URI, URIrecordingWav, lyricsStr, URIrecordingAnno, '/tmp/', withSynthesis)
        alignmentErrors = []
        alignmentErrors = evalAlignmentError(URIrecordingAnno, outputHTKPhoneAlignedURI, evalLevel)
        detectedTokenList = outputHTKPhoneAlignedURI
        
        correctDuration, totalDuration = evalAccuracy(URIrecordingAnno, outputHTKPhoneAlignedURI, evalLevel)
        
    
    # store decoding results in a file FIXME: if with duration it is not mlf 
    detectedAlignedfileName = URIrecordingNoExt + tokenLevelAlignedSuffix
    if not os.path.isfile(detectedAlignedfileName):
        detectedAlignedfileName =  tokenList2TabFile(detectedTokenList, URIrecordingNoExt, tokenLevelAlignedSuffix)
        
        
    return alignmentErrors,  detectedAlignedfileName, correctDuration, totalDuration, correctDurationScoreDev
    




def alignOneChunk(URIrecordingNoExt, lyricsWithModels, alpha, evalLevel, usePersistentFiles, tokenLevelAlignedSuffix):
    '''
    wrapper top-most logic method
    '''
     
        
    # read from file result
    detectedAlignedfileName = URIrecordingNoExt + tokenLevelAlignedSuffix
    if os.path.isfile(detectedAlignedfileName):
        detectedTokenList = readListOfListTextFile(detectedAlignedfileName)
    else:
             
        # DEBUG: score-derived phoneme  durations
        lyricsWithModels.printPhonemeNetwork()
    #     lyricsWithModels.printWordsAndStates()
    
        
        
        decoder = Decoder(lyricsWithModels, alpha)
    #  TODO: DEBUG: do not load models
    # decoder = Decoder(lyrics, withModels=False, numStates=86)
    #################### decode
        if usePersistentFiles=='True':
            usePersistentFiles = True
        elif usePersistentFiles=='False':
            usePersistentFiles = False
        else: 
            sys.exit("usePersistentFiles can be only True or False") 
            
        detectedTokenList = decodeAudioChunk(URIrecordingNoExt, decoder, evalLevel, usePersistentFiles)
        
    ### VISUALIZE
    #     decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)
        

#################### evaluate
    alignmentErrors = [2, 3, 4]
    alignmentErrors = _evalAlignmentError(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel)
    
    correctDuration, totalDuration = _evalAccuracy(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel )

    return alignmentErrors, detectedTokenList, correctDuration, totalDuration






def decodeAudioChunk( URI_recording_noExt, decoder, evalLevel, usePersistentFiles):
    '''
    decoder : 
    WITH_DURAITON flag triggered here
    '''    
    
    observationFeatures = loadMFCCs(URI_recording_noExt) #     observationFeatures = observationFeatures[0:1000]
    
       
    
    detectedWordList = []
    decoder.decodeAudio(observationFeatures, usePersistentFiles, URI_recording_noExt, decoder.lyricsWithModels.stateDurationInFrames2List())
    detectedWordList = decoder.path2ResultWordList()
       
    
    return detectedWordList



    

def getReferenceDurations(URI_recording_noExt, lyricsWithModels, evalLevel):
        '''
        timestamps of words according to reference durations read from score. Used to obtain so called 'score-deviation' metric
        not used in decoding 
        '''
        
        
        annotationURI = URI_recording_noExt + ANNOTATION_EXT

        ##### get duration of initial silence 

        try:
            annotationTokenListA = TextGrid2WordList(annotationURI, evalLevel)     
            
            # just copy duration of silence in groundTruth 
            annoTsAndToken =  annotationTokenListA[0]
            if annoTsAndToken[2] != "" and not(annoTsAndToken[2].isspace()): # skip empty phrases
                    logger.warn("annotaiton {} starts with non-sil token ".format(annotationURI))
                    finalSilFram =  float(annoTsAndToken[0]) * NUM_FRAMES_PERSECOND
            else:
                finalSilFram = float(annoTsAndToken[1]) * NUM_FRAMES_PERSECOND
            
        
        except :
        # if no Gr Truth annotation file (or needed layer) present - take from model    
            finalSilFram = 0
            countFirstStateFirstWord = lyricsWithModels.listWords[0].syllables[0].phonemes[0].numFirstState
             
            for i in range(countFirstStateFirstWord):
                finalSilFram += lyricsWithModels.statesNetwork[i].getDurationInFrames()
        
            
        refTokenList = expandlyrics2WordList (lyricsWithModels, lyricsWithModels.statesNetwork, finalSilFram,  _constructTimeStampsForWord)
        grTruthDurationfileExtension = '.scoreDeviation'
        writeListOfListToTextFile(refTokenList, None , URI_recording_noExt + grTruthDurationfileExtension )
        
#     TODO: could be done easier with this code, and check last method in Word
#         refTokenList =    testT(lyricsWithModels)

        correctDuration, totalDuration = _evalAccuracy(annotationURI, refTokenList, evalLevel )

        return correctDuration, totalDuration
    


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
    logger.debug("reading MFCCs from {} ...".format(URI_recording_mfc_txt))
    mfccsFeatrues = numpy.loadtxt(URI_recording_mfc_txt , delimiter=','  ) 
    
    return mfccsFeatrues








if __name__ == '__main__':
        doitOneChunk(sys.argv)
    
#     for ALPHA in range(0.1,0.3):
#         b  = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/guelen/01_Olmaz_6_nakarat2'
#         a = '/Users/joro/Documents/Phd/UPF//turkish-makam-lyrics-2-audio-test-data/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/'
#         
#         doitOneChunk(a, 6, b,  ALPHA, False, True)


