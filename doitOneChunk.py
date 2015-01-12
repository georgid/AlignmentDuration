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
from Constants import NUM_FRAMES_PERSECOND

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

EVALLEVEL = 2




def doitOneChunk(argv):
    
    if len(argv) != 6 and  len(argv) != 7 :
            print ("usage: {}  <pathToComposition> <whichSection> <URI_recording_no_ext> <ALPHA> <ONLY_MIDDLE_STATE> <usePersistentFiles=True>".format(argv[0]) )
            sys.exit();
    
    
    URIrecordingNoExt = argv[3]
    pathToComposition = argv[1]
    whichSection = int(argv[2])
    ALPHA = float(argv[4])
    ONLY_MIDDLE_STATE = argv[5]
    
    params = Parameters(ALPHA, ONLY_MIDDLE_STATE)
    
    usePersistentFiles = 'True'
    if len(argv) == 7:
        usePersistentFiles =  argv[6]
    
    
    set_printoptions(threshold='nan') 
    
    ################## load lyrics and models 
    
    htkParser = HtkConverter()
    htkParser.load(MODEL_URI, HMM_LIST_URI)
    
    alignmentErrors, detectedWordList, grTruthDurationWordList = alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, params, usePersistentFiles)
        
    mean, stDev, median = getMeanAndStDevError(alignmentErrors)
#     writeListOfListToTextFile(detectedWordList, None, '/Users/joro/Downloads/test.txt')
        
    logger.info("mean : {} st dev: {} ".format( mean,stDev))


    visualiseInPraat(URIrecordingNoExt, detectedWordList, False, grTruthDurationWordList)
    


def alignOneChunk(URIrecordingNoExt, pathToComposition, whichSection, htkParser, params, usePersistentFiles):
    '''
    top most logic method
    '''
    lyrics = loadLyrics(pathToComposition, whichSection)
    lyricsWithModels = LyricsWithModels(lyrics.listWords, htkParser, params.ONLY_MIDDLE_STATE)
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
        
    detectedWordList, grTruthWordList = decodeAudioChunk(URIrecordingNoExt, decoder, usePersistentFiles)
    
### VISUALIZE
    decoder.lyricsWithModels.printWordsAndStatesAndDurations(decoder.path)

#################### evaluate
    alignmentErrors = _evalAlignmentError(URIrecordingNoExt + '.TextGrid', detectedWordList, EVALLEVEL)
    return alignmentErrors, detectedWordList, grTruthWordList





def decodeAudioChunk( URI_recording_noExt, decoder, usePersistentFiles):
    '''
    decoder : 
    WITH_DURAITON flag triggered here
    '''    
    
    observationFeatures = loadMFCCs(URI_recording_noExt) #     observationFeatures = observationFeatures[0:1000]
    
    if WITH_DURATIONS:
        decoder.lyricsWithModels.duration2numFrameDuration(observationFeatures, URI_recording_noExt)
        


    grTruthWordList  = getGroundTruthDurations(URI_recording_noExt, decoder)
    
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
    

def getGroundTruthDurations(URI_recording_noExt, decoder):
        
                # duration of initial silence 
#         finalSilFram = 0
#         countFirstStateFirstWord = decoder.lyricsWithModels.listWords[0].syllables[0].phonemes[0].numFirstState
#         
#         for i in range(countFirstStateFirstWord):
#             finalSilFram += decoder.lyricsWithModels.statesNetwork[i].getDurationInFrames()

        
        annotationURI = URI_recording_noExt + '.TextGrid'
        annotationTokenListA = TextGrid2WordList(annotationURI, EVALLEVEL)     
    
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




def visualiseInPraat(URIrecordingNoExt, detectedWordList, isDetectionInFile, grTruthDurationWordList=[]):
    ### OPTIONAL############# : PRAAT
    pathToAudioFile = URIrecordingNoExt + '.wav'
    URIGrTruth = URIrecordingNoExt + '.TextGrid'
    tierNameWordAligned = '"wordDurationAligned"'
    tierNamePhonemeAligned = '"dummy1"'
# gr truth
    if grTruthDurationWordList != None and grTruthDurationWordList != []:
        addAlignmentResultToTextGrid(grTruthDurationWordList, URIGrTruth, pathToAudioFile, '"grTruthDuration"', '"dummy2"')

# detected
    if isDetectionInFile and os.path.isfile(detectedWordList):
        alignedResultPath, fileNameWordAnno = addAlignmentResultToTextGridFIle(detectedWordList, URIGrTruth, tierNameWordAligned, tierNamePhonemeAligned)
    else:
        alignedResultPath, fileNameWordAnno = addAlignmentResultToTextGrid(detectedWordList, URIGrTruth, pathToAudioFile, tierNameWordAligned, tierNamePhonemeAligned)


# open both
    openTextGridInPraat(alignedResultPath, fileNameWordAnno, pathToAudioFile)




if __name__ == '__main__':
        doitOneChunk(sys.argv)
    
#     for ALPHA in range(0.1,0.3):
#         b  = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/guelen/01_Olmaz_6_nakarat2'
#         a = '/Users/joro/Documents/Phd/UPF//turkish-makam-lyrics-2-audio-test-data/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/'
#         
#         doitOneChunk(a, 6, b,  ALPHA, False, True)


