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
from LyricsParsing import expandlyrics2Words, _constructTimeStampsForWord, testT
from Constants import NUM_FRAMES_PERSECOND, AUDIO_EXTENSION
from Phonetizer import Phonetizer



# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )
from Utilz import writeListOfListToTextFile, writeListToTextFile,\
    getMeanAndStDevError, getSectionNumberFromName

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
from TextGrid_Parsing import TextGrid2WordList
from PraatVisualiser import tokenList2TabFile

# TODO: read mfccs with matlab htk_read
# sys.path.append('/Users/joro/Downloads/python-matlab-bridge-master')
# from pymatbridge import Matlab

numpy.set_printoptions(threshold='nan')

currDir = os.path.abspath(os.path.dirname(os.path.realpath(sys.argv[0])) )
modelDIR = currDir + '/model/'
HMM_LIST_URI = modelDIR +'/monophones0'
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
    
    alignmentErrors, detectedWordList, grTruthDurationWordList, detectedAlignedfileName = alignDependingOnWithDuration(URIrecordingNoExt, whichSection, pathToComposition, withDuration, withSynthesis, evalLevel, params, usePersistentFiles, htkParser)
        
        
    mean, stDev, median = getMeanAndStDevError(alignmentErrors)
#     writeListOfListToTextFile(detectedWordList, None, '/Users/joro/Downloads/test.txt')
    logger.info("mean : {} st dev: {} ".format( mean,stDev))


#     visualiseInPraat(URIrecordingNoExt, withDuration, detectedAlignedfileName,  detectedWordList, grTruthDurationWordList)

    


def alignDependingOnWithDuration(URIrecordingNoExt, whichSection, pathToComposition, withDuration, withSynthesis, evalLevel, params, usePersistentFiles, htkParser):
    '''
    call alignment method depending on whether duration or htk  selected 
    '''

    Phonetizer.initLookupTable(withSynthesis)
    
    tokenLevelAlignedSuffix, phonemesAlignedSuffix = determineSuffix(withDuration, withSynthesis, evalLevel)
    
    
    if withDuration:
        alignmentErrors, detectedWordList, grTruthDurationWordList = alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, params, evalLevel, usePersistentFiles)
        
            
    else:
        URIrecordingAnno = URIrecordingNoExt + ANNOTATION_EXT
        URIrecordingWav = URIrecordingNoExt + AUDIO_EXTENSION
        # new makamScore used
        lyricsObj = loadLyrics(pathToComposition, whichSection)
        lyrics = lyricsObj.__str__()
#         in case  we are at no-lyrics section
        if not lyrics or lyrics =='_SAZ_':
            logger.warn("skipping section {} with no lyrics ...".format(whichSection))
            return [], [], [], []
    
        outputHTKPhoneAlignedURI = Aligner.alignOnechunk(MODEL_URI, URIrecordingWav, lyrics.__str__(), URIrecordingAnno, '/tmp/', withSynthesis)
        alignmentErrors = evalAlignmentError(URIrecordingAnno, outputHTKPhoneAlignedURI, evalLevel)
        detectedWordList = outputHTKPhoneAlignedURI
        grTruthDurationWordList = []
    
    # store decoding results in a file FIXME: if with duration it is not mlf 
    detectedAlignedfileName = []
    detectedAlignedfileName =  tokenList2TabFile(detectedWordList, URIrecordingNoExt, tokenLevelAlignedSuffix)
        
    return alignmentErrors, detectedWordList, grTruthDurationWordList, detectedAlignedfileName
    




def alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, params, evalLevel, usePersistentFiles):
    '''
    top most logic method
    '''

    lyrics = loadLyrics(pathToComposition, whichSection)
    lyricsStr = lyrics.__str__()
    
    if not lyricsStr or lyricsStr =='_SAZ_':
        logger.warn("skipping section {} with no lyrics ...".format(whichSection))
        return [], [], []

    logger.info("aligning audio {}".format(URIrecordingNoExt))
    lyricsWithModels = LyricsWithModels(lyrics, htkParser, params.ONLY_MIDDLE_STATE)
    
    # DEBUG: score-derived phoneme  durations
#     lyricsWithModels.printPhonemeNetwork()
    
    
    decoder = Decoder(lyricsWithModels, params.ALPHA)
#  TODO: DEBUG: do not load models
#  decoder = Decoder(lyrics, withModels=False, numStates=86)
#################### decode
    if usePersistentFiles=='True':
        usePersistentFiles = True
    elif usePersistentFiles=='False':
        usePersistentFiles = False
    else: 
        sys.exit("usePersistentFiles can be only True or False") 
        
    detectedWordList, grTruthWordList = decodeAudioChunk(URIrecordingNoExt, decoder, evalLevel, usePersistentFiles)
    
### VISUALIZE
#     decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)

#################### evaluate
    alignmentErrors = [2, 3, 4]
    alignmentErrors = _evalAlignmentError(URIrecordingNoExt + ANNOTATION_EXT, detectedWordList, evalLevel)
    return alignmentErrors, detectedWordList, grTruthWordList






def decodeAudioChunk( URI_recording_noExt, decoder, evalLevel, usePersistentFiles):
    '''
    decoder : 
    WITH_DURAITON flag triggered here
    '''    
    
    observationFeatures = loadMFCCs(URI_recording_noExt) #     observationFeatures = observationFeatures[0:1000]
    
    if WITH_DURATIONS:
        decoder.lyricsWithModels.duration2numFrameDuration(observationFeatures, URI_recording_noExt)
        

    refDurationsWordList = []
    refDurationsWordList  = getReferenceDurations(URI_recording_noExt, decoder, evalLevel)
    
    detectedWordList = []
#     decoder.decodeAudio(observationFeatures, usePersistentFiles, URI_recording_noExt, decoder.lyricsWithModels.getDurationInFramesList())
#     detectedWordList = decoder.path2ResultWordList()
    

#       use to calc score deviations
    detectedWordList = refDurationsWordList
    
    return detectedWordList, refDurationsWordList



    

def getReferenceDurations(URI_recording_noExt, decoder, evalLevel):
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
            countFirstStateFirstWord = decoder.lyricsWithModels.listWords[0].syllables[0].phonemes[0].numFirstState
             
            for i in range(countFirstStateFirstWord):
                finalSilFram += decoder.lyricsWithModels.statesNetwork[i].getDurationInFrames()
        
            
        grTruthWordList = expandlyrics2Words (decoder.lyricsWithModels, decoder.lyricsWithModels.statesNetwork, finalSilFram,  _constructTimeStampsForWord)
        grTruthDurationfileExtension = '.grTruthDuration'
        writeListOfListToTextFile(grTruthWordList, None , URI_recording_noExt + grTruthDurationfileExtension )
        
#     TODO: could be done easier with this code, and check last method in Word
#         grTruthWordList =    testT(decoder.lyricsWithModels)
        return grTruthWordList
    


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


