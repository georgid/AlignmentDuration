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
import logging
import sys
import numpy
from MusicXmlParser import MusicXMLParser
from lyricsParser import divideIntoSentencesFromAnnoWithSil_andCreateLyrics
from ParametersAlgo import ParametersAlgo
from doitOneChunkAlign import doitOneChunkAlign

def runWithParameters(argv):
    
    if len(argv) != 6:
            print ("Tool to get alignment accuracy of jingu with different parameters. Sort all results according to tempo")
            print ("usage: {}   <pathToRecordings> <withScores> <deviationINSec> <whichTempo>  <withVocalPrediction>".format(argv[0]) )
            sys.exit()
    
    rootURI = argv[1]
#     rootURI = '/Users/joro/Documents/Phd/UPF/arias/'
    
    listRecordingURIs =  [ rootURI + 'laosheng-erhuang_04',  rootURI + 'laosheng-xipi_02', rootURI + 'dan-xipi_01' ]
    withScores  = int(argv[2])
    ParametersAlgo.DEVIATION_IN_SEC = float(argv[3])
    tempo = argv[4]
    withVocalPrediction = int(argv[5])
    
    # hard-code tempo sections for 3 arias 
    tempiDict = {}
    tempiDict["slow"] = [(14,202),(163,173),()]
    tempiDict["mid"] = [(212,420),(29,112),(11,72)]
    tempiDict["fast"] = [(),(124,161),(80,423)]
    
    correctDuration = 0
    totalDuration = 0
    
    for i, URIrecordingNoExt in enumerate(listRecordingURIs):
        lyricsTextGrid = URIrecordingNoExt + '.TextGrid'
        tempoIndices = tempiDict[tempo][i] # tempoIndices for the recording
        if len(tempoIndices) == 0:
            continue
        
    
        # load ts for different sentences
    #         fromTss, toTss = loadSectionTimeStamps(sectionAnnoURI)
        listSentences = divideIntoSentencesFromAnnoWithSil_andCreateLyrics(lyricsTextGrid)
        
        musicXMLParser = None
    
        if withScores:
            musicXmlURI = URIrecordingNoExt + '_score.xml'
            musicXMLParser = MusicXMLParser(musicXmlURI, lyricsTextGrid)
        
    
        
        for whichSentence, currSentence in  enumerate(listSentences):
            currToSyllable = currSentence[3]
            print "currToSyllable {}".format(currToSyllable)
             
            if currToSyllable < tempoIndices[0]-1 or currToSyllable > tempoIndices[1]-1:
                continue 
            currCorrectDuration, currTotalDuration = doitOneChunkAlign(URIrecordingNoExt, lyricsTextGrid, musicXMLParser,  whichSentence, currSentence, withScores, withVocalPrediction)  
            currAcc = currCorrectDuration / currTotalDuration
            print "sentence {}: acc ={:.2f}".format(whichSentence, currAcc)
            correctDuration += currCorrectDuration
            totalDuration += currTotalDuration
            
    print "final: {:.2f}".format(correctDuration / totalDuration * 100)     

if __name__ == '__main__':
    runWithParameters(sys.argv)
#     example: 
# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/Jingju/runWithParams.py /Users/joro/Documents/Phd/UPF/arias/ 1 0.1