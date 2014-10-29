'''
Created on Oct 13, 2014

@author: joro
'''
import os
from MakamScore import MakamScore
import glob
import numpy
import sys
from Decoder import Decoder
from LyricsWithModels import LyricsWithModels

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics')
pathHtk2Sp = os.path.join(parentDir, 'htk2s3')
pathHMM = os.path.join(parentDir, 'HMM')

sys.path.append(pathHtk2Sp)
sys.path.append(pathUtils )
sys.path.append(pathHMM)


from hmm.continuous.GMHMM  import GMHMM
from htk_converter import HtkConverter
from Utilz import writeListOfListToTextFile, writeListToTextFile

pathEvaluation = os.path.join(parentDir, 'Evaluation')
sys.path.append(pathEvaluation)
from WordLevelEvaluator import _evalAlignmentError

numpy.set_printoptions(threshold='nan')

PATH_TO_HMMLIST='/Users/joro/Documents/Phd/UPF/voxforge/auto/scripts/interim_files/'

HMMLIST_NAME = 'monophones0'

MODEL_URI = '/Users/joro/Documents/Phd/UPF/METUdata/model_output/multipleGaussians/hmmdefs9/iter9/hmmdefs'

HMM_LIST_URI =  os.path.join(PATH_TO_HMMLIST + HMMLIST_NAME)

     


def loadTranscript(pathToComposition, whichSection):


#     expand phoneme list from transcript
    os.chdir(pathToComposition)
    pathTotxt = os.path.join(pathToComposition, glob.glob("*.txt")[0])
    pathToSectionTsv =  os.path.join(pathToComposition, glob.glob("*.tsv")[0])
    makamScore = MakamScore(pathTotxt, pathToSectionTsv )
        
    # phoneme IDs
    lyrics = makamScore.getLyricsForSection(whichSection)
    return lyrics
    


     
def loadMFCCs(URI_recording_noExt): 
    '''
    for now lead extracted with HTK, read in matlab and seriqlized to txt file
    '''
    URI_recording = URI_recording_noExt + '.mfc_txt' 
    
    mfccsFeatrues = numpy.loadtxt(URI_recording , delimiter=','  ) 
    
    return mfccsFeatrues 




def decodeAudio(argv, decoder):
    URIrecording = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/goekhan/02_Gel_3_zemin'
    
    
    observationFeatures = loadMFCCs(URIrecording) #     observationFeatures = observationFeatures[0:1000]
    path, psi, delta = decoder.decodeAudio(observationFeatures)
    writeListToTextFile(path, None, '/Users/joro/Downloads/path.test')
    detectedWordList = decoder.path2ResultWordList()
   
    alignmentError = _evalAlignmentError(URIrecording + '.TextGrid', detectedWordList, 1)
    return alignmentError

def main(argv):
    
    if len(argv) != 4:
            print ("usage: {}  <pathToComposition> <whichSection> <URI_recording_no_ext>".format(argv[0]) )
            sys.exit();
            
    pathToComposition = '/Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/'
    pathToComposition = argv[1]
    
    whichSection = 3
    whichSection = int(argv[2])
    
     

    lyrics = loadTranscript(pathToComposition, whichSection)
    
    lyricsWithModels = LyricsWithModels(lyrics.listWords, MODEL_URI, HMM_LIST_URI )
#     lyricsWithModels.printPhonemeNetwork()
    
    decoder = Decoder(lyricsWithModels)
    
    #################### decode
    URIrecording = argv[3]
    alignmentError = decodeAudio(URIrecording, decoder)
    
    print alignmentError
   

if __name__ == '__main__':
    main(sys.argv)

