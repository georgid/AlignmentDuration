'''
Created on Oct 13, 2014

@author: joro
'''
import os
from MakamScore import MakamScore
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
    getMeanAndStDevError

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
from WordLevelEvaluator import _evalAlignmentError, evalAlignmentError, tierAliases
from TextGrid_Parsing import TextGrid2WordList
from PraatVisualiser import addAlignmentResultToTextGrid, openTextGridInPraat, addAlignmentResultToTextGridFIle

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
    
    if len(argv) != 7 and  len(argv) != 8 :
            print ("usage: {}  <pathToComposition> <URI_recording_no_ext> <withDuration=1> <ALPHA> <ONLY_MIDDLE_STATE> <evalLevel> <usePersistentFiles=True>".format(argv[0]) )
            sys.exit();
    
    
    URIrecordingNoExt = argv[2]
    whichSection = getSectionNumberFromName(URIrecordingNoExt) 

    pathToComposition = argv[1]
    withDuration = int(argv[3])
    ALPHA = float(argv[4])
    ONLY_MIDDLE_STATE = argv[5]
    
    evalLevel = tierAliases.wordLevel
    evalLevel = int(argv[6])

    params = Parameters(ALPHA, ONLY_MIDDLE_STATE)
    
    usePersistentFiles = 'True'
    if len(argv) == 8:
        usePersistentFiles =  argv[7]
    
    
    set_printoptions(threshold='nan') 
    
    ################## load lyrics and models 
    htkParser = None
    if withDuration == 1:
        htkParser = HtkConverter()
        htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    alignmentErrors, detectedWordList, grTruthDurationWordList = alignDependingOnWithDuration(URIrecordingNoExt, whichSection, pathToComposition, withDuration, evalLevel, params, usePersistentFiles, htkParser)

        
        
    mean, stDev, median = getMeanAndStDevError(alignmentErrors)
#     writeListOfListToTextFile(detectedWordList, None, '/Users/joro/Downloads/test.txt')
    logger.info("mean : {} st dev: {} ".format( mean,stDev))


    #visualiseInPraat(URIrecordingNoExt, detectedWordList, withDuration, grTruthDurationWordList)

    


def alignDependingOnWithDuration(URIrecordingNoExt, whichSection, pathToComposition, withDuration, evalLevel, params, usePersistentFiles, htkParser):
    '''
    call alignment method depending on whether duration or new model selected 
    '''
    withSynthesis = 1
    Phonetizer.initLookupTable(withSynthesis)
    
    if withDuration == 1:
        alignmentErrors, detectedWordList, grTruthDurationWordList = alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, params, evalLevel, usePersistentFiles)
        return alignmentErrors, detectedWordList, grTruthDurationWordList
    
    elif withDuration == 0:
        URIrecordingAnno = URIrecordingNoExt + ANNOTATION_EXT
        URIrecordingWav = URIrecordingNoExt + AUDIO_EXTENSION
        lyrics = loadLyrics(pathToComposition, whichSection).__str__()
        outputHTKPhoneAlignedURI = Aligner.alignOnechunk(MODEL_URI, URIrecordingWav, lyrics, URIrecordingAnno, '/tmp/', withSynthesis)
        alignmentErrors = evalAlignmentError(URIrecordingAnno, outputHTKPhoneAlignedURI, evalLevel)
    
    return alignmentErrors, outputHTKPhoneAlignedURI, [] 



def alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, params, evalLevel, usePersistentFiles):
    '''
    top most logic method
    '''
    
    
    lyrics = loadLyrics(pathToComposition, whichSection)
    lyricsWithModels = LyricsWithModels(lyrics, htkParser, params.ONLY_MIDDLE_STATE)
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
    alignmentErrors = _evalAlignmentError(URIrecordingNoExt + '.TextGrid', detectedWordList, evalLevel)
    return alignmentErrors, detectedWordList, grTruthWordList




def getSectionNumberFromName(URIrecordingNoExt):

    underScoreTokens  = URIrecordingNoExt.split("_")
    index = -1
    while (-1 * index) <= len(underScoreTokens):
        token = str(underScoreTokens[index])
        if token.startswith('meyan') or token.startswith('zemin') or \
        token.startswith('nakarat'):
            break
        index -=1
    
    try:
        whichSection = underScoreTokens[index-1]
    except Exception:
        sys.exit("please put the number of section before its name: e.g. *_2_meyan_* in the file name ")
    return int(whichSection)


def decodeAudioChunk( URI_recording_noExt, decoder, evalLevel, usePersistentFiles):
    '''
    decoder : 
    WITH_DURAITON flag triggered here
    '''    
    
    observationFeatures = loadMFCCs(URI_recording_noExt) #     observationFeatures = observationFeatures[0:1000]
    
    if WITH_DURATIONS:
        decoder.lyricsWithModels.duration2numFrameDuration(observationFeatures, URI_recording_noExt)
        


    grTruthWordList  = getGroundTruthDurations(URI_recording_noExt, decoder, evalLevel)
    
    detectedWordList = []
    decoder.decodeAudio(observationFeatures, usePersistentFiles, URI_recording_noExt, decoder.lyricsWithModels.getDurationInFramesList())
    detectedWordList = decoder.path2ResultWordList()
     
    
    
    return detectedWordList, grTruthWordList




def loadLyrics(pathToComposition, whichSection):


#     expand phoneme list from transcript
    os.chdir(pathToComposition)
    pathTotxt = os.path.join(pathToComposition, glob.glob("*.txt")[0])
    pathToSectionTsv =  os.path.join(pathToComposition, glob.glob("*sections.tsv")[0])
    makamScore = MakamScore(pathTotxt, pathToSectionTsv )
    
    # phoneme IDs
    lyrics = makamScore.getLyricsForSection(whichSection)
    return lyrics
    

def getGroundTruthDurations(URI_recording_noExt, decoder, evalLevel):
        
                # duration of initial silence 
#         finalSilFram = 0
#         countFirstStateFirstWord = decoder.lyricsWithModels.listWords[0].syllables[0].phonemes[0].numFirstState
#         
#         for i in range(countFirstStateFirstWord):
#             finalSilFram += decoder.lyricsWithModels.statesNetwork[i].getDurationInFrames()

        
        annotationURI = URI_recording_noExt + ANNOTATION_EXT
        annotationTokenListA = TextGrid2WordList(annotationURI, evalLevel)     
    
        annoTsAndToken =  annotationTokenListA[0]
        if annoTsAndToken[2] != "" and not(annoTsAndToken[2].isspace()): # skip empty phrases
                logger.warn("annotaiton {} starts with non-sil token ".format(annotationURI))
                finalSilFram =  float(annoTsAndToken[0]) * NUM_FRAMES_PERSECOND
        else:
            finalSilFram = float(annoTsAndToken[1]) * NUM_FRAMES_PERSECOND
        
            
        grTruthWordList = expandlyrics2Words (decoder.lyricsWithModels, decoder.lyricsWithModels.statesNetwork, finalSilFram,  _constructTimeStampsForWord)
        writeListOfListToTextFile(grTruthWordList, None , URI_recording_noExt + "gtDur.txt" )
        
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




def visualiseInPraat(URIrecordingNoExt, detectedWordList, withDuration, grTruthDurationWordList=[]):
    ### OPTIONAL############# : PRAAT
    pathToAudioFile = URIrecordingNoExt + '.wav'
    URIGrTruth = URIrecordingNoExt + ANNOTATION_EXT
    tierNameWordAligned = '"wordDurationAligned"'
    tierNamePhonemeAligned = '"dummy1"'
# gr truth
    if grTruthDurationWordList != None and grTruthDurationWordList != []:
        addAlignmentResultToTextGrid(grTruthDurationWordList, URIGrTruth, pathToAudioFile, '"grTruthDuration"', '"dummy2"')

# detected
    if withDuration == '1':
        isDetectedInFile = False
    elif withDuration == '0':
        isDetectedInFile = True
        
    if isDetectedInFile and os.path.isfile(detectedWordList):
        alignedResultPath, fileNameWordAnno = addAlignmentResultToTextGridFIle(detectedWordList, URIGrTruth, tierNameWordAligned, tierNamePhonemeAligned)
    else:
        alignedResultPath, fileNameWordAnno = addAlignmentResultToTextGrid(detectedWordList, URIGrTruth, pathToAudioFile, tierNameWordAligned, tierNamePhonemeAligned)


# open final TextGrid in Praat 
    openTextGridInPraat(alignedResultPath, fileNameWordAnno, pathToAudioFile)




if __name__ == '__main__':
        doitOneChunk(sys.argv)
    
#     for ALPHA in range(0.1,0.3):
#         b  = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/guelen/01_Olmaz_6_nakarat2'
#         a = '/Users/joro/Documents/Phd/UPF//turkish-makam-lyrics-2-audio-test-data/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/'
#         
#         doitOneChunk(a, 6, b,  ALPHA, False, True)


