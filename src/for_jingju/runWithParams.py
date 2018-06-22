# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/


'''
Created on Dec 5, 2014

@author: joro
'''
import sys

from align.ParametersAlgo import ParametersAlgo

#from runitHTK import runitHTK
from matplotlib.pyplot import legend

import matplotlib.pyplot as plt
from utilsLyrics.Utilz import getMeanAndStDevError, addTimeShift,\
    writeListOfListToTextFile
import os
from for_jingju.JingjuRecording import JingjuScore, JingjuRecording
from align.LyricsAligner import LyricsAligner
from for_jingju.lyricsParser import divideIntoSentencesFromAnnoWithSil_andCreateLyrics
import numpy
import logging




def runWithParameters(argv):
    
    if len(argv) != 4:
            print ("Tool to get alignment accuracy of one for_jingju aria with different parameters ")
            print ("usage: {}   <URIRecording No Extension>  <deviation_INSeconds> <withRefSyllDurations>".format(argv[0]) )
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
        from MusicXmlParser import MusicXMLParser
        musicXmlURI = URIrecordingNoExt + '_score.xml'
        musicXMLParser = MusicXMLParser(musicXmlURI, lyricsTextGrid)
    
    withRefSyllDurations = int(argv[3])
    syllRefDurations = None

    if withRefSyllDurations:
        
        # parse syllRefDurations 
        path, fileName = os.path.split(URIrecordingNoExt + '.wav')
        path, which_fold = os.path.split(path) # which Fold
        path, blah = os.path.split(path)
        path, blah = os.path.split(path)
        syllRefDurations_URI =  os.path.join(path + '/stats/' + which_fold, 'syllRefDurations')
        if not os.path.isfile(syllRefDurations_URI):
            sys.exit("you specified withRedSyllDur=1. Then add file {} ".format( syllRefDurations_URI))
        syllRefDurations = numpy.loadtxt( syllRefDurations_URI )
 # load total # different sentences + their rspective ts
    listLyicsSections, annotationLinesListNoPauses = divideIntoSentencesFromAnnoWithSil_andCreateLyrics(lyricsTextGrid, syllRefDurations) #uses TextGrid annotation to derive structure. TODO: instead of annotation, uses score
    
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
     
#     lyricsAligner.evalAccuracy()
    
    
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