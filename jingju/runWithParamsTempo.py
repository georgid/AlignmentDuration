'''
Created on Dec 5, 2014

@author: joro
'''
import logging
import sys
import numpy
from MusicXmlParser import MusicXMLParser
from lyricsParser import divideIntoSentencesFromAnnoOld
from hmm.ParametersAlgo import ParametersAlgo
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
        listSentences = divideIntoSentencesFromAnnoOld(lyricsTextGrid)
        
        musicXMLParser = None
    
        if withScores:
            musicXmlURI = URIrecordingNoExt + '_score.xml'
            musicXMLParser = MusicXMLParser(musicXmlURI, lyricsTextGrid)
        
    
        
        for whichSentence, currSentence in  enumerate(listSentences):
            currToSyllable = currSentence[3]
            print "currToSyllable {}".format(currToSyllable)
             
            if currToSyllable < tempoIndices[0]-1 or currToSyllable > tempoIndices[1]-1:
                continue 
            currCorrectDuration, currTotalDuration = doitOneChunkAlign(URIrecordingNoExt, musicXMLParser,  whichSentence, currSentence, withScores, withVocalPrediction)  
            currAcc = currCorrectDuration / currTotalDuration
            print "sentence {}: acc ={:.2f}".format(whichSentence, currAcc)
            correctDuration += currCorrectDuration
            totalDuration += currTotalDuration
            
    print "final: {:.2f}".format(correctDuration / totalDuration * 100)     

if __name__ == '__main__':
    runWithParameters(sys.argv)
#     example: 
# python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/Jingju/runWithParams.py /Users/joro/Documents/Phd/UPF/arias/ 1 0.1