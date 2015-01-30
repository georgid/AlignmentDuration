# -*- coding: utf-8 -*-
'''
contains a class
Created on Mar 3, 2014

@author: joro
'''


import os
import sys
import imp
from Phonetizer import Phonetizer
from Decoder import logger

# trick to make terminal NOT assume ascii
reload(sys).setdefaultencoding("utf-8")

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics')

sys.path.append(pathUtils )

from Utilz import writeListToTextFile, findFileByExtensions
import codecs

import glob
from SymbTrParser import SymbTrParser
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
        symbTrParser = SymbTrParser(pathToSymbTrFile, pathToSectionTsvFile)
       
        # list of Word object
        symbTrParser.syllables2Lyrics()
        lyricsAllSections = symbTrParser.sectionLyrics
        
        # for each section part
        for currSectionBoundary,currSectionLyrics in zip(symbTrParser.sectionboundaries, lyricsAllSections):
            tupleSectionNameAndLyrics =  currSectionBoundary[0], currSectionLyrics  
            self.sectionToLyricsMap.append(tupleSectionNameAndLyrics)
            
    def getLyricsForSection(self,sectionNumber):
        '''
        convenience getter
        '''
        
        if sectionNumber >  len(self.sectionToLyricsMap):
            sys.exit("section withNumber {} not present in score. Chech your .sections.tsv file".format(sectionNumber) )

        #python indexing starts from zero
        lyrics = self.sectionToLyricsMap[sectionNumber][1]
        if not lyrics.listWords:
            logger.warn("no lyrics for demanded section {} : {}".format(sectionNumber, self.sectionToLyricsMap[sectionNumber][0] ) )
        return lyrics 
 
  
   ##################################################################################
    def printSectionsAndLyrics(self):
        '''
        utility method to print all lyrics that are read from symbTr
        '''
        for currSection in self.sectionToLyricsMap:
    
            print '\n' + str(currSection[0]) + ':'

            print currSection[1]
#             for word in  currSection[1]:
#                 print word.__str__().encode('utf-8','replace')
        

    def serializePhonemesForSection(self, whichSection, outputFileName):
        '''
        list of all phonemes. print to file @param outputFileName
        '''    
        lyrics = self.getLyricsForSection(whichSection)
    
        
        writeListToTextFile(lyrics.phonemesNetwork, None,  outputFileName )
        return lyrics.phonemesNetwork
    
            
        
        
    def printSyllables(self, whichSection):
        '''
        debug: print syllables 
        '''
        
        lyrics = self.getLyricsForSection(whichSection)
        lyrics.printSyllables
        
     
               


def loadLyrics(pathToComposition, whichSection):

    Phonetizer.initLookupTable(False)
    
    os.chdir(pathToComposition)

    pathTotxt = os.path.join(pathToComposition, glob.glob("*.txt")[0])
    
    listExtensions = ["sections.txt", "sections.tsv", "sections.json"]
    sectionFile = findFileByExtensions(pathToComposition, listExtensions)
        
    pathToSectionTsv = os.path.join(pathToComposition, sectionFile)
    makamScore = MakamScore(pathTotxt, pathToSectionTsv )
    
    # phoneme IDs
    lyrics = makamScore.getLyricsForSection(whichSection)
    return lyrics


def testMakamScore(argv):
        if len(argv) != 2:
            print ("usage: {} <path to symbtTr.txt and symbTr.sections.tsv>".format(argv[0]) )
            sys.exit();
        pathToComposition = argv[1]
        
        lyrics = loadLyrics(pathToComposition, whichSection=0)
        
        print lyrics
        
     
      

          
             
if __name__ == '__main__':

        # only for unit testing purposes
        
        print "in Makam Score"
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/ussak--sarki--aksak--bu_aksam_gun--tatyos_efendi/']
        
        
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/rast--turku--semai--gul_agaci--necip_mirkelamoglu/']
        
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin/']
        testMakamScore(a)
          
      
         