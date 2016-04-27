'''
Created on Dec 5, 2014

@author: joro
'''

import sys
import os
import subprocess


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathHMMDuration = os.path.join(parentDir, 'JingjuAlignment')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)


from doitOneChunkAlign import doitOneChunkAlign

from lyricsParser import divideIntoSentencesFromAnnoWithSil

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)
from LyricsWithGMMs import LyricsWithGMMs

#  evaluation  
pathEvaluation = os.path.join(parentDir, 'AlignmentEvaluation')
if pathEvaluation not in sys.path:
    sys.path.append(pathEvaluation)

from AccuracyEvaluator import evalAccuracy
from parse.TextGrid_Parsing import tierAliases

def runitHTK(argv):
    
    if len(argv) != 2:
            print ("Tool to get alignment accuracy of of one jingju aria with htk ")
            print ("usage: {}   <URIRecording No Extension> ".format(argv[0]) )
            sys.exit()


    URIrecordingNoExt =  argv[1]
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'

    # load total # different sentences + their rspective ts
#         fromTss, toTss = loadSectionTimeStamps(sectionAnnoURI)
    listSentences = divideIntoSentencesFromAnnoWithSil(lyricsTextGrid, False) #uses TextGrid annotation to derive structure. TODO: instead of annotation, uses score
    

        
    correctDuration = 0
    totalDuration = 0
    accuracyList = []
    
    

    
#     for whichSentence, currSentence in  reversed(list(enumerate(listSentences))):
    for whichSentence, currSentence in  enumerate(listSentences):
        
        #     read from file result

        URIRecordingChunkNoExt = URIrecordingNoExt + "_" + str(currSentence.beginTs) + '_' + str(currSentence.endTs)
        
        ### these 3 lines needed for baseline with htk
        lyricsWithModels = LyricsWithGMMs(currSentence,  'True', 2 , URIrecordingNoExt)
        dict_ = URIRecordingChunkNoExt + '.dict'
        mlf = URIRecordingChunkNoExt + '.mlf'
        lyricsWithModels.printDict(dict_, 0)
        lyricsWithModels.printDict(mlf, 1)

        
        outputHTKPhoneAlignedURI = alignWithHTK(URIRecordingChunkNoExt, dict_, mlf)
#         currCorrectDuration, currTotalDuration = doitOneChunkAlign(URIrecordingNoExt, musicXMLParser, whichSentence, currSentence, withOracle, withDurations, withVocalPrediction)  
        
        # calc local accuracy
        URIrecordingAnno = URIrecordingNoExt + '.TextGrid'
        evalLevel =  tierAliases.pinyin
        fromSyllableIdx = currSentence.fromSyllableIdx
        toSyllableIdx = currSentence.toSyllableIdx
        currCorrectDuration, currTotalDuration = evalAccuracy(URIrecordingAnno, outputHTKPhoneAlignedURI, evalLevel, fromSyllableIdx, toSyllableIdx)
        
        acc = currCorrectDuration / currTotalDuration
        accuracyList.append(acc)
        
        print "result is: " + str(acc)
        
        correctDuration += currCorrectDuration
        totalDuration += currTotalDuration  

    print "final: {:.2f}".format(correctDuration / totalDuration * 100)     
    import matplotlib.pyplot as plt
    plt.plot(accuracyList, 'ro')
#     plt.show()
    return correctDuration, totalDuration, accuracyList
    

def alignWithHTK(URIRecordingChunkNoExt, dict_, mlf):
#     
#     pipe = subprocess.Popen([PATH_TO_HVITE, '-l', "'*'", '-A', '-D', '-T', '1', '-b', 'sil', '-C', PATH_TO_CONFIG_FILES + 'config_singing', '-a', \
#                                  '-H', self.pathToHtkModel, '-H',  DUMMY_HMM_URI , '-H',  MODEL_NOISE_URI , '-i', '/tmp/phoneme-level.output', '-m', \
#                                  '-w', wordNetwURI, '-y', 'lab', dictName, PATH_TO_HMMLIST, mfcFileName], stdout=self.currLogHandle)
    
    logName = '/tmp/log_all'
    currLogHandle = open(logName, 'w')
    currLogHandle.flush()
    decodedWordlevelMLF = URIRecordingChunkNoExt + '.out.mlf'    
        
    PATH_TO_HVITE = '/Users/joro/Documents/Fhg/htk3.4.BUILT/bin/HVite'
    PATH_TO_CONFIG_FILES = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/models/'
    
    path, fileName = os.path.split(URIRecordingChunkNoExt)
    path, fold = os.path.split(path) # which Fold
    
    PATH_HTK_MODELS = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation//lyrics2audio/models/hmmdefs_' + fold 
    PATH_TO_HMMLIST = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/models/hmmlist'
       
    command = [PATH_TO_HVITE, '-a', '-m', '-I', mlf, '-C', PATH_TO_CONFIG_FILES + 'config',  \
                                 '-H', PATH_HTK_MODELS,  '-i', decodedWordlevelMLF,  \
                                  dict_, PATH_TO_HMMLIST, URIRecordingChunkNoExt + '.wav']   
    pipe = subprocess.Popen(command, stdout = currLogHandle)
        
    pipe.wait()      
    return decodedWordlevelMLF
    
    
if __name__ == '__main__':
    runitHTK(sys.argv)

