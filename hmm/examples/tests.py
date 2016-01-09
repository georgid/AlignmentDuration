'''
Created on Jun 10, 2015

@author: joro
'''
import numpy
from hmm.continuous.GMHMM import GMHMM
from hmm.discrete import DiscreteHMM
from main import decode, loadSmallAudioFragment
import os
import sys
from hmm.Parameters import Parameters
from hmm.examples.main import  getDecoder

# file parsing tools as external lib 
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir,os.path.pardir )) 
print parentDir

pathJingjuAlignment = os.path.join(parentDir, 'AlignmentDuration')
if not pathJingjuAlignment in sys.path:
    sys.path.append(pathJingjuAlignment)

from Phonetizer import Phonetizer
from MakamScore import loadLyrics
from Decoder import Decoder


from PraatVisualiser import tokenList2TabFile
from Utilz import readListOfListTextFile

pathToComposition = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/'
URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ISTANBUL/safiye/01_Bakmiyor_1_zemin'
whichSection = 1

# # test with synthesis
# pathToComposition = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/'
# URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade/04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade'
# whichSection = 1


pathToComposition ='/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/'
URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/ISTANBUL/guelen/01_Olmaz_2_zemin'
whichSection = 2

pathToComposition ='/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi/'
URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/HMMDuration/hmm/examples/KiseyeZeminPhoneLevel_2_zemin'
whichSection = 2

import logging
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
sys.path.append(pathEvaluation)
from AccuracyEvaluator import _evalAccuracy


pathJingjuAlignment = os.path.join(parentDir, 'JingjuAlignment')
if not pathJingjuAlignment in sys.path:
    sys.path.append(pathJingjuAlignment)


def test_simple():
    n = 2
    m = 2
    d = 2
    pi = numpy.array([0.5, 0.5])
    A = numpy.ones((n,n),dtype=numpy.double)/float(n)
    
    w = numpy.ones((n,m),dtype=numpy.double)
    means = numpy.ones((n,m,d),dtype=numpy.double)
    covars = [[ numpy.matrix(numpy.eye(d,d)) for j in xrange(m)] for i in xrange(n)]
    
    w[0][0] = 0.5
    w[0][1] = 0.5
    w[1][0] = 0.5
    w[1][1] = 0.5    
    means[0][0][0] = 0.5
    means[0][0][1] = 0.5
    means[0][1][0] = 0.5    
    means[0][1][1] = 0.5
    means[1][0][0] = 0.5
    means[1][0][1] = 0.5
    means[1][1][0] = 0.5    
    means[1][1][1] = 0.5    

    gmmhmm = GMHMM(n,m,d,A,means,covars,w,pi,init_type='user',verbose=True)
    
    obs = numpy.array([ [0.3,0.3], [0.1,0.1], [0.2,0.2]])
    
    print "Doing Baum-welch"
    gmmhmm.train(obs,10)
    print
    print "Pi",gmmhmm.pi
    print "A",gmmhmm.A
    print "weights", gmmhmm.w
    print "means", gmmhmm.means
    print "covars", gmmhmm.covars
    
def test_rand():
    gmmhmm,d = makeTestDurationHMM()
    obs = numpy.array((0.6 * numpy.random.random_sample((40,d)) - 0.3), dtype=numpy.double)
    
    print "Doing Baum-welch"
    gmmhmm.train(obs,1000)
    print
    print "Pi",gmmhmm.pi
    print "A",gmmhmm.A
    print "weights", gmmhmm.w
    print "means", gmmhmm.means
    print "covars", gmmhmm.covars
    
def test_discrete():

    ob5 = (3,1,2,1,0,1,2,3,1,2,0,0,0,1,1,2,1,3,0)
    print "Doing Baum-welch"
    
    atmp = numpy.random.random_sample((4, 4))
    row_sums = atmp.sum(axis=1)
    a = atmp / row_sums[:, numpy.newaxis]    

    btmp = numpy.random.random_sample((4, 4))
    row_sums = btmp.sum(axis=1)
    b = btmp / row_sums[:, numpy.newaxis]
    
    pitmp = numpy.random.random_sample((4))
    pi = pitmp / sum(pitmp)
    
    hmm2 = DiscreteHMM(4,4,a,b,pi,init_type='user',precision=numpy.longdouble,verbose=True)
    hmm2.train(numpy.array(ob5*10),100)
    print "Pi",hmm2.pi
    print "A",hmm2.A
    print "B", hmm2.B


def makeTestDurationHMM():
    '''
    generate some random model. 
    '''
    n = 5
    d = 2
    m = 3
    atmp = numpy.random.random_sample((n, n))
    row_sums = atmp.sum(axis=1)
    a = numpy.array(atmp / row_sums[:, numpy.newaxis], dtype=numpy.double)    

    wtmp = numpy.random.random_sample((n, m))
    row_sums = wtmp.sum(axis=1)
    w = numpy.array(wtmp / row_sums[:, numpy.newaxis], dtype=numpy.double)
    
    means = numpy.array((0.6 * numpy.random.random_sample((n, m, d)) - 0.3), dtype=numpy.double)
    covars = numpy.zeros( (n,m,d,d) )
    
    for i in xrange(n):
        for j in xrange(m):
            for k in xrange(d):
                covars[i][j][k][k] = 1    
    
    pitmp = numpy.random.random_sample((n))
    pi = numpy.array(pitmp / sum(pitmp), dtype=numpy.double)

    gmmhmm = GMHMM(n,m,d,a,means,covars,w,pi,init_type='user',verbose=True)
    return    gmmhmm, d  


def testRand_DurationHMM():
    '''
    test with audio features from real recording, but some random model, not trained model 
    TODO: this might not work. rewrite
    '''
    durGMMhmm,d = makeTestDurationHMM()
    
    durGMMhmm.setALPHA(0.97)
    
    listDurations = [70,30,20,10,20];
    durGMMhmm.setDurForStates(listDurations)
    
    
    observationFeatures = numpy.array((0.6 * numpy.random.random_sample((2,d)) - 0.3), dtype=numpy.double)
#     observationFeatures = loadMFCCs(URIrecordingNoExt)

    decode(lyricsWithModels, observationFeatures, 'testRecording')
    
        
#     # test computePhiStar
#     currState = 1
#     currTime = 25
#     phiStar, fromState, maxDurIndex = durGMMhmm.computePhiStar(currTime, currState)
#     print "phiStar={}, maxDurIndex={}".format(phiStar, maxDurIndex)

def test_backtrack(lyricsWithModels, URIrecordingNoExt):

    decoder = getDecoder(lyricsWithModels, URIrecordingNoExt)
    absPathPsi = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'psi' )
    psi = numpy.loadtxt(absPathPsi)
    
    absPathChi = os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'chi' )
    chi = numpy.loadtxt(absPathChi)
    withOracle= 0
    decoder. backtrack(withOracle, chi, psi)


def test_decoding(pathToComposition, whichSection):
    '''
    read initialized matrix from file. useful to test getMaxPhi with vector
    '''
    
    withSynthesis = True
    lyrics = loadLyrics(pathToComposition, whichSection, withSynthesis)
    lyricsWithModels, observationFeatures, URIRecordingChunk = loadSmallAudioFragment(lyrics,  URIrecordingNoExt, withSynthesis, fromTs=-1, toTs=-1)
    
    decoder = getDecoder(lyricsWithModels, URIRecordingChunk)
    
    decoder.hmmNetwork.phi = numpy.loadtxt('phi_init')
    lenObs = len(observationFeatures)
    chiBackPointer, psiBackPointer = decoder.hmmNetwork._viterbiForcedDur(lenObs)


def test_initialization(lyricsWithModels, URIrecordingNoExt, observationFeatures):
    '''
    just initialilzation step.
    '''
    decoder = getDecoder(lyricsWithModels, URIrecordingNoExt)
    #  init
    decoder.hmmNetwork.initDecodingParameters(observationFeatures)


def test_oracle(URIrecordingNoExt, pathToComposition, whichSection):
    '''
    read phoneme-level ground truth and test
    '''
    withSynthesis = False
    lyrics = loadLyrics(pathToComposition, whichSection, withSynthesis)
    
    if logger.level == logging.DEBUG:
        lyrics.printPhonemeNetwork()
    
    # consider only part of audio
    fromTs = 0; toTs = 20.88
    # since not all TextGrid might be on phoneme level
    fromPhonemeIdx  = 1; toPhonemeIdx = 42
    tokenLevelAlignedSuffix = '.syllables_oracle'
    
    detectedAlignedfileName = URIrecordingNoExt + tokenLevelAlignedSuffix
    if os.path.isfile(detectedAlignedfileName):
        print "{} already exists. No decoding".format(detectedAlignedfileName)
        detectedTokenList  = readListOfListTextFile(detectedAlignedfileName)
        
    else:
        detectedTokenList = decodeWithOracle(lyrics, URIrecordingNoExt, fromTs, toTs, fromPhonemeIdx, toPhonemeIdx)
          
        detectedAlignedfileName = URIrecordingNoExt + tokenLevelAlignedSuffix
        if not os.path.isfile(detectedAlignedfileName):
            detectedAlignedfileName =  tokenList2TabFile(detectedTokenList, URIrecordingNoExt, tokenLevelAlignedSuffix)
            
        
    ANNOTATION_EXT = '.TextGrid'
    # eval on phrase level
    evalLevel = 2
    correctDuration, totalDuration = _evalAccuracy(URIrecordingNoExt + ANNOTATION_EXT, detectedTokenList, evalLevel, -1, -1 )
    print "accuracy= {}".format(correctDuration / totalDuration)
    
    return detectedTokenList






    

if __name__ == '__main__':    
    #test_simple()
    # test_rand()
    #test_discrete()
    # testRand_DurationHMM()
    
#     test_oracle(URIrecordingNoExt, pathToComposition, whichSection)

#####################     for all tetst below inclide these 3 lines for lyrics:
    withSynthesis = True
    lyrics = loadLyrics(pathToComposition, whichSection, withSynthesis)
    lyricsWithModels, observationFeatures, URIrecordingChunk = loadSmallAudioFragment(lyrics,  URIrecordingNoExt, withSynthesis, fromTs=-1, toTs=-1)
#     
    decode(lyricsWithModels, observationFeatures, URIrecordingNoExt)
#   
    
#     test_backtrack(lyricsWithModels, URIrecordingNoExt)
#     test_initialization(lyricsWithModels, URIrecordingNoExt, observationFeatures)

   
#     test_decoding(pathToComposition, whichSection)