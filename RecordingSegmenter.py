# -*- coding: utf-8 -*-

'''
Created on Mar 3, 2014

@author: joro


'''

from MakamScore import MakamScore, loadLyrics
from MakamRecording import MakamRecording 
import subprocess
import os
import glob
from Utilz import  writeListOfListToTextFile, loadTextFile, findFileByExtensions
# from Aligner import Aligner
from Aligner import  HTK_MLF_ALIGNED_SUFFIX, PHRASE_ANNOTATION_EXT,\
    openAlignmentInPraat
import sys

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
sys.path.append(pathEvaluation)
from WordLevelEvaluator import evalAlignmentError


# this one has excluded sections with wrong pitch from melodia
# PATH_TEST_DATASET = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/'

PATH_TEST_DATASET = '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/'

# 
# COMPOSITION_NAME = 'nihavent--sarki--aksak--koklasam_saclarini--artaki_candan'
# RECORDING_DIR = '20_Koklasam_Saclarini'
#   
# COMPOSITION_NAME = 'nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi'
# RECORDING_DIR = '03_Bekir_Unluataer_-_Kimseye_Etmem_Sikayet_Aglarim_Ben_Halime'
# # 
# # 
# COMPOSITION_NAME = 'segah--sarki--curcuna--olmaz_ilac--haci_arif_bey'
# RECORDING_DIR = '21_Recep_Birgit_-_Olmaz_Ilac_Sine-i_Sad_Pareme'
# # 
# COMPOSITION_NAME = 'nihavent--sarki--turkaksagi--nerelerde_kaldin--ismail_hakki_efendi'
# RECORDING_DIR = '3-12_Nerelerde_Kaldin'

OUTPUT_PATH = '/tmp/testAudio'
MODEL_URI = '/Users/joro/Documents/Phd/UPF/METUdata/model_output/multipleGaussians/hmmdefs9/iter9/hmmdefs'

class RecordingSegmenter(object):
   
                  
                
    def __init__(self):
        return
    
    
        ##################################################################################
    
    '''
    Loads all lyrics , divides them line-wise and writes new files
    
    '''
    def loadMakamScore(self, pathTotxt, pathToSectionTsv):
        
     # initialize makam lyrics
            makamScore = MakamScore(pathTotxt, pathToSectionTsv)
            
            # individual lyrics line written to separate files. 
            # then these files loaded fro each segment
            # done because might be needed at evaulation
#             makamScore.serializeLyricsToFile()    
            return makamScore              


    def segment(self, makamScore, pathToAudioFile, pathToSectionAnnotations):
            makamRecording = MakamRecording(makamScore, pathToAudioFile, pathToSectionAnnotations)
            
            # convert to wav 
            makamRecording.mp3ToWav()
            
            # divide into segments
#             makamRecording.divideAudio()
            makamRecording.divideAudioLinksNew()
            
            makamRecording.markUsedChunks()
            return makamRecording

##################################################################################

        
    ''' align one recording from symbTr
        split into chunks using manually annotated sections from @param pathToSectionAnnotations, and align each  
    
    '''
#     def alignOneRecording(self, pathToHtkModel, makamRecording, path_TO_OUTPUT, withSynthesis):
# 
#         
#             # prepare eval metric:
#             numParts = 0;
#             listAllAlignmnetErrors = []
#             
#             for whichChunk in range(len(makamRecording.sectionIndices)):
#                 sectionIndex =  makamRecording.sectionIndices[whichChunk]
#                 # section not described in score
#                 if sectionIndex == 0:
#                     continue
#                 
#                 lyrics = makamRecording.makamScore.sectionToLyricsMap[sectionIndex-1][1]
#                 
#                 # some sections have errors in melodia. so dont use them.
# #                 if not makamRecording.isChunkUsed[whichChunk]:
# #                     continue
#                 
#                 # skip non-vocal sections
#                 if lyrics == "" or "." in lyrics:
#                     continue 
#                 
#                 ####=================================
#                 # run alignment
#                 currPathToAudioFile = makamRecording.pathToDividedAudioFiles[whichChunk]
#                 
#                 
#                 
#                 outputHTKPhoneAlignedURI = RecordingSegmenter.alignOneChunk(pathToHtkModel, path_TO_OUTPUT, lyrics, currPathToAudioFile, 0, withSynthesis)
#                 basenAudioFile = os.path.splitext(currPathToAudioFile)[0]
#                 phraseAnnoURI = basenAudioFile  + PHRASE_ANNOTATION_EXT
#                 
#                 
#                 currChunkAlignmentErrors = evalAlignmentError(phraseAnnoURI, outputHTKPhoneAlignedURI)
#                 listAllAlignmnetErrors.extend(currChunkAlignmentErrors)
#                 print( "error is {1} for {0} ".format(currPathToAudioFile,currChunkAlignmentErrors))  
#                 
#                 ### OPTIONAL : open in praat
#                 praseAnno = os.path.splitext(currPathToAudioFile)[0] + PHRASE_ANNOTATION_EXT
#                 openAlignmentInPraat(praseAnno, outputHTKPhoneAlignedURI, 0, currPathToAudioFile)
#                 
#                 numParts +=1
#                 # numPArts not needed for now
#                 
#             return listAllAlignmnetErrors


    
    ''' align one audio chunk 
    @param isLyricsFromFile - option to load lyrics from file with ext .txtTur
    if isLyricsFromFile=1, loads lyrics from  
    else lyrics  are the  @param lyrics itself 
    '''

    @staticmethod
    def alignOneChunk( pathToHtkModel, path_TO_OUTPUT, lyrics, currPathToAudioFile, isLyricsFromFile, withSynthesis):
        
        
        if  not(os.path.isdir(path_TO_OUTPUT)):
            os.mkdir(path_TO_OUTPUT);
        
        chunkAligner = Aligner(pathToHtkModel, currPathToAudioFile, lyrics, isLyricsFromFile,  withSynthesis)
    

        baseNameAudioFile = os.path.splitext(os.path.basename(chunkAligner.pathToAudioFile))[0]
        
        
        outputHTKPhoneAlignedURI = os.path.join(path_TO_OUTPUT, baseNameAudioFile) + HTK_MLF_ALIGNED_SUFFIX
      
        chunkAligner.alignAudio(0, path_TO_OUTPUT, outputHTKPhoneAlignedURI)
        
     
        
        
        return outputHTKPhoneAlignedURI
        
def doitForTestPiece(compositionName, recordingDir, withSynthesis=0):
    
        
   
    ####### prepare composition! ############
        
        pathToComposition = os.path.join(PATH_TEST_DATASET, compositionName)
        makamScore = loadLyrics(pathToComposition, whichSection=1)

                
                    # TODO: issue 14
        
        ###########        ----- align one recording
        
        pathToRecording = os.path.join(pathToComposition, recordingDir)
         
        os.chdir(pathToRecording)
#         pathToSectionAnnotations = os.path.join(pathToRecording, glob.glob('*.sectionAnno.txt')[0]) #             pathToAudio =  os.path.join(pathToRecording, glob.glob('*.wav')[0])
        
        listExtensions = ["sectionAnno.json", "sectionAnno.txt", "sectionAnno.tsv" ]
        sectionAnnoFiles = findFileByExtensions(pathToRecording, listExtensions)
        pathToSectionAnnotations = os.path.join(pathToRecording, sectionAnnoFiles[0]) 
        
        pathToAudio = os.path.join(pathToRecording, recordingDir) + '.wav'
        
        # TODO: issue 14
        recordingSegmenter = RecordingSegmenter()
        makamRecording= recordingSegmenter.segment(makamScore, pathToAudio, pathToSectionAnnotations)
        
        alignmentErrors = []
#         alignmentErrors = recordingSegmenter.alignOneRecording(MODEL_URI, makamRecording, OUTPUT_PATH, withSynthesis)
        
        return alignmentErrors

def doit(argv):
        
        if len(argv) != 4  :
           sys.exit ("usage: {}  <recordingURI.wav> <sectionAnnoPath> <scorePath>".format(argv[0]) )
        recordingURI = argv[1]
        sectionAnnoPath = argv[2]
        scorePath = argv[3]
        
        makamScore = loadLyrics(scorePath, whichSection=1)

        os.chdir(sectionAnnoPath)
        
        listExtensions = ["sectionLinks.json", "sectionAnno.txt", "sectionAnno.tsv"]
        sectionAnnoFiles = findFileByExtensions(sectionAnnoPath, listExtensions)
        pathToSectionAnnotations = os.path.join(sectionAnnoPath, sectionAnnoFiles[0]) 


        recordingSegmenter = RecordingSegmenter()
        makamRecording= recordingSegmenter.segment(makamScore, recordingURI, pathToSectionAnnotations)

if __name__ == '__main__':
       
    print 'in recording segmenter main method'
#     compositionName = 'ussak--sarki--aksak--bu_aksam_gun--tatyos_efendi/'
#     recordingDir = 'Sakin--Gec--Kalma'
#     
#     compositionName = 'nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi/'
#     recordingDir = 'Melihat_Gulses'
#     

    compositionName = 'rast--sarki--curcuna--nihansin_dideden--haci_faik_bey/'
    recordingDir = 'Nurten_Demirkol'

    
#     doitForTestPiece(compositionName, recordingDir, withSynthesis=0)
    doit(sys.argv)
    
#         ----
        
#