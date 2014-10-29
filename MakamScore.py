# -*- coding: utf-8 -*-
'''
contains a class
Created on Mar 3, 2014

@author: joro
'''


import os
import sys
import imp

# trick to make terminal NOT assume ascii
reload(sys).setdefaultencoding("utf-8")

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics')

sys.path.append(pathUtils )

from Utilz import writeListToTextFile
import codecs

import glob
from SymbTrParser import SymbTrParser
from Phonetizer import Phonetizer
from Phoneme import Phoneme
# from utils.Utils import writeListToTextFile


# 
# COMPOSITION_NAME = 'muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik'
# COMPOSITION_NAME = 'huseyni--sarki--turkaksagi--hicran_oku--sevki_bey'
# 
# PATH_TEST_DATASET='/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/'
# PATH_TEST_DATASET = '/Volumes/IZOTOPE/sertan_sarki/'

class MakamScore():
    '''
    classdocs
    '''


##################################################################################

    def __init__(self, pathToSymbTrFile, pathToSectionTsvFile):
        '''
        Constructor
        
        '''
        self.compositionName = os.path.splitext(pathToSymbTrFile)[0]
        
        ''' lyrics divided into sectons.
        # e.g. "nakarat" : [ word1 word2 ] '''
        self.sectionToLyricsMap = []
        
        self._loadSectionsAndSyllablesFromSymbTr(pathToSymbTrFile, pathToSectionTsvFile)
        
        
        # pats to individual ..txt lyrics files. 
        self.pathsTolyricSectionFiles = []
        
      
  ##################################################################################
    '''
    parses symbTr file. Reads lyrics, 
    reads section names
    groups together section names and lyrics 
    '''
    def _loadSectionsAndSyllablesFromSymbTr(self, pathToSymbTrFile, pathToSectionTsvFile):
        symbTrParser = SymbTrParser(pathToSymbTrFile)
       
        symbTrParser._loadSectionBoundaries(pathToSectionTsvFile)
        
        # list of Word object
        lyricsAllSections = symbTrParser.syllables2Words()
        
        # for each section part
        for currSectionBoundary,currSectionLyrics in zip(symbTrParser.sectionboundaries, lyricsAllSections):
            tupleSectionNameAndLyrics =  currSectionBoundary[0], currSectionLyrics  
            self.sectionToLyricsMap.append(tupleSectionNameAndLyrics)
            
    def getLyricsForSection(self,sectionNumber):
        '''
        convenience getter
        '''
        #python indexing starts from zero
        sectionNumber = sectionNumber - 1
        return self.sectionToLyricsMap[sectionNumber][1]
 
  
   ##################################################################################
    def printSectionsAndLyrics(self):
        '''
        utility method to print all lyrics that are read from symbTr
        '''
        for currSection in self.sectionToLyricsMap:
    
            print '\n' + str(currSection[0]) + ':'
            
            for word in  currSection[1]:
                print word.__str__().encode('utf-8','replace')
    #             string_for_output = currSection[1].encode('utf-8','replace')
        

    def serializePhonemesForSection(self, whichSection, outputFileName):
        '''
        list of all phonemes. print to file @param outputFileName
        '''    
        lyrics = self.getLyricsForSection(whichSection)
    
        
        writeListToTextFile(lyrics.phonemesNetwork, None,  outputFileName )
        return lyrics.phonemesNetwork
    
    def _calcPhonemeDurations(self, whichSection):
        lyrics = self.getLyricsForSection(whichSection)
        for word_ in lyrics.listWords:
            for syllable in word_.syllables:
                syllable.calcPhonemeDurations()
        
        
    def printSyllables(self, whichSection):
        '''
        debug: print syllables 
        '''
        
        lyrics = self.getLyricsForSection(whichSection)
        lyrics.printSyllables
        
     
               




    
     ##################################################################################
    

def loadScore(pathToComposition):
    '''
    load all score-related info into an object
    '''
    os.chdir(pathToComposition)
    pathTotxt = os.path.join(pathToComposition, glob.glob("*.txt")[0])
    pathToSectionTsv = os.path.join(pathToComposition, glob.glob("*.sections.tsv")[0])
    makamScore = MakamScore(pathTotxt, pathToSectionTsv)
    return makamScore


def main(argv):
        if len(argv) != 2:
            print ("usage: {} <path to symbtTr.txt and symbTr.tsv>".format(argv[0]) )
            sys.exit();
        pathToComposition = argv[1]
        
        makamScore = loadScore(pathToComposition)
        
        makamScore.printSectionsAndLyrics()
        # is this needed? 
        
        
     
      

          
             
if __name__ == '__main__':

        # only for unit testing purposes
        
        print "in Makam Score"
        
        main(sys.argv)
          
      
         