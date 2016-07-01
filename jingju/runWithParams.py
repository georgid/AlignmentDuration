'''
Created on Dec 5, 2014

@author: joro
'''
import sys
from MusicXmlParser import MusicXMLParser
from align.ParametersAlgo import ParametersAlgo

#from runitHTK import runitHTK
from matplotlib.pyplot import legend

import matplotlib.pyplot as plt
from utilsLyrics.Utilz import getMeanAndStDevError, addTimeShift,\
    writeListOfListToTextFile
import os
from jingju.JingjuRecording import JingjuScore, JingjuRecording
from align.LyricsAligner import LyricsAligner
from jingju.lyricsParser import divideIntoSentencesFromAnnoWithSil
import numpy




def runWithParameters(argv):
    
    if len(argv) != 3:
            print ("Tool to get alignment accuracy of one jingju aria with different parameters ")
            print ("usage: {}   <URIRecording No Extension>  <deviation_INSeconds>".format(argv[0]) )
            sys.exit()
    
    ParametersAlgo.FOR_JINGJU = 1
    ParametersAlgo.WITH_ORACLE_ONSETS = -1
    
    URIrecordingNoExt =  argv[1]
    b = os.path.basename(URIrecordingNoExt)
    lyricsTextGrid =  os.path.join(os.path.dirname(URIrecordingNoExt), os.pardir, os.pardir,b+'.TextGrid')
    
    
   
    correctDurationHTK = 0
    totalDurationHTK = 1
    accuracyListHTK = []
#     correctDurationHTK, totalDurationHTK, accuracyListHTK = runitHTK(["dummy", URIrecordingNoExt ])       
    
       
    if float(argv[2]) == 0.0:
       sys.exit('DEVIATION_IN_SEC cannot be 0.0' ) 
    ParametersAlgo.DEVIATION_IN_SEC = float(argv[2])
    musicXMLParser = None
        
    withMusicalScores = 0

    if withMusicalScores == 1:
        musicXmlURI = URIrecordingNoExt + '_score.xml'
        musicXMLParser = MusicXMLParser(musicXmlURI, lyricsTextGrid)

   
   # parse syllRefDurations 
    path, fileName = os.path.split(URIrecordingNoExt + '.wav')
    path, which_fold = os.path.split(path) # which Fold
    path, blah = os.path.split(path)
    path, blah = os.path.split(path)

    syllRefDurations = numpy.loadtxt( os.path.join(path + '/stats/' + which_fold, 'syllRefDurations') )
   
 # load total # different sentences + their rspective ts
    listLyicsSections, annotationLinesListNoPauses = divideIntoSentencesFromAnnoWithSil(lyricsTextGrid, syllRefDurations) #uses TextGrid annotation to derive structure. TODO: instead of annotation, uses score
    jingjuScore = JingjuScore(listLyicsSections)
    
    # 
    jingjuRecording = JingjuRecording('dummymbRecordingID', URIrecordingNoExt + '.wav', jingjuScore, lyricsTextGrid, annotationLinesListNoPauses)
    
    # for Jingju section Annotations are given by TextGrid
    WITH_SECTION_ANNOTATIONS = 1
    lyricsAligner = LyricsAligner(jingjuRecording, WITH_SECTION_ANNOTATIONS, ParametersAlgo.PATH_TO_HCOPY)
    
    extractedPitchList = None
    outputDir = 'test'
    totalDetectedTokenList, sectionLinksDict = lyricsAligner.alignRecording( extractedPitchList, outputDir)
    
    
    ret = {}

    ret['alignedLyricsSyllables'] = totalDetectedTokenList
    ret['sectionlinks'] = sectionLinksDict
#     print ret 
    
#     if detectedTokenList != None:
#         currAcc, correctDuration, totalDuration = calcAccuracy(whichSentence, currCorrectDuration, currTotalDuration, correctDuration, totalDuration)
#     accuracyList.append(currAcc)
#      
#      
#     correctDuration, totalDuration = _evalAccuracy(currSectionLink.section.lyricsTextGrid, detectedTokenList, evalLevel, currSectionLink.fromSyllableIdx, currSectionLink.toSyllableIdx  )
#     acc = correctDuration / totalDuration
#     print "result is: " + str(acc)
     
    lyricsAligner.evalAccuracy()
    
    
    correctDurationOracle = 0
    totalDurationOracle = 1
    accuracyListOracle = []
    
    
    correctDuration = 0
    totalDuration = 1
    accuracyList = []
    tokenListAlignedAll = []

    

#         correctDurationOracle, totalDurationOracle, dummy, dummy = doit(withOracle, URIrecordingNoExt, lyricsTextGrid, musicXMLParser, withMusicalScores, correctDurationOracle, totalDurationOracle, accuracyListOracle, withVocalPrediction, whichSentence, currSectionLink)

        
            
            
            ##### write all decoded output persistently to files
    phonemeAlignedfileName = URIrecordingNoExt + '.syllables_total_dev_' + str(ParametersAlgo.DEVIATION_IN_SEC)
    writeListOfListToTextFile(tokenListAlignedAll, 'startTs \t endTs \t phonemeOrSyllorWord \t beginNoteNumber \n', phonemeAlignedfileName)
    

    plotAccuracyList(accuracyListOracle, 'oracle', 'r')
    plotAccuracyList(accuracyList, 'DHMM', 'g')
    plotAccuracyList(accuracyListHTK, 'baseline', 'b')
    
    
    legend(loc=3, fontsize=12)
    plt.axvline(2.5)
    plt.axvline(7.5)
    plt.xlabel('lyrics lines', fontsize=12)
    plt.ylabel('overall accuracy', fontsize=12)

#     plt.show()
    
    
    return  correctDurationHTK, totalDurationHTK, correctDurationOracle, totalDurationOracle, correctDuration, totalDuration




def calcAccuracy(whichSentence, currCorrectDuration, currTotalDuration, correctDuration, totalDuration):
    
    '''
    helper calc correct duration 
    '''
    currAcc = currCorrectDuration / currTotalDuration
   
    print "sentence {}: acc ={:.2f}".format(whichSentence, currAcc)
    correctDuration += currCorrectDuration
    totalDuration += currTotalDuration
    
    return currAcc, correctDuration, totalDuration




def doit( withOracle,  URIrecordingNoExt,  musicXMLParser, withDurations, correctDuration, totalDuration, accuracyList, withVocalPrediction, whichSentence, currSentence):
   
    currCorrectDuration, currTotalDuration, detectedTokenList, sentenceBeginTs = doitOneChunkAlign(URIrecordingNoExt,  musicXMLParser, whichSentence, currSentence, withOracle,  withDurations, withVocalPrediction) # calc local accuracy
    if detectedTokenList != None:
        currAcc, correctDuration, totalDuration = calcAccuracy(whichSentence, currCorrectDuration, currTotalDuration, correctDuration, totalDuration)
    accuracyList.append(currAcc)
    
    return correctDuration, totalDuration, detectedTokenList, sentenceBeginTs


def plotAccuracyList(accuracyList, labelText, colorText):
    
    point  = colorText + 'o' 
    plt.plot(accuracyList, point, label=labelText) # plot mean and st dev
    mean, stDev, median = getMeanAndStDevError(accuracyList)
#     plt.errorbar(len(accuracyList) / 2.0, mean, stDev, ecolor=colorText, linestyle='None', marker='^')
    
      
  
  
    
if __name__ == '__main__':
    runWithParameters(sys.argv)
#     runWithParametersAll(sys.argv)


#     example: 
# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/runWithParams.py /Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/ 1 0.1 dan-xipi_01 0
# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/runWithParams.py /Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/ 1 0.1 laosheng-xipi_02 0

# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/JingjuAlignment/runWithParams.py /Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/fold2/wangjiangting_dushoukong 2
# 

# output is printed on the console after each aria is done