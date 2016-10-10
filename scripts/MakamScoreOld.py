# -*- coding: utf-8 -*-
'''
contains a class
Created on Mar 3, 2014

@author: joro
'''


import os
import sys
from align.Phonetizer import Phonetizer
import logging

# trick to make terminal NOT assume ascii
reload(sys).setdefaultencoding("utf-8")

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics')

sys.path.append(pathUtils )

from utilsLyrics.Utilz import writeListToTextFile, findFileByExtensions
import codecs

import glob
from SymbTrParserOld import SymbTrParserOld
# from utils.Utils import writeListToTextFile


# 
# COMPOSITION_NAME = 'muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik'
# COMPOSITION_NAME = 'huseyni--sarki--turkaksagi--hicran_oku--sevki_bey'
# 
# PATH_TEST_DATASET='/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data/'
# PATH_TEST_DATASET = '/Volumes/IZOTOPE/sertan_sarki/'

class MakamScoreOld():
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
        symbTrParser = SymbTrParserOld(pathToSymbTrFile, pathToSectionTsvFile)
       
        # list of Word object
        symbTrParser.syllables2Lyrics()
        lyricsAllSections = symbTrParser.sectionLyrics
        
        # for each section part
        for currSectionBoundary,currSectionLyrics in zip(symbTrParser.sectionboundaries, lyricsAllSections):
            # setionName, melodicSTRucture, lyricStructure, lyrics
            quadrupleSectionNameAndLyrics =  currSectionBoundary[0], currSectionBoundary[1], currSectionBoundary[2],  currSectionLyrics  
            self.sectionToLyricsMap.append(quadrupleSectionNameAndLyrics)
            
    def getLyricsForSection(self,sectionNumber):
        '''
        convenience getter
        '''
        
        if sectionNumber >=  len(self.sectionToLyricsMap) or sectionNumber < 0:
            sys.exit("section withNumber {} not present in score. Check your .sections.tsv file".format(sectionNumber) )

        #python indexing starts from zero
        lyrics = self.sectionToLyricsMap[sectionNumber][3]
        if not lyrics.listWords:
            logging.warn("no lyrics for demanded section {} : {}".format(sectionNumber, self.sectionToLyricsMap[sectionNumber][0] ))
            return None
        return lyrics 
 
  
   ##################################################################################
    def printSectionsAndLyrics(self):
        '''
        utility method to print all lyrics that are read from symbTr
        '''
        for currSection in self.sectionToLyricsMap:
    
            print '\n' + str(currSection[0])  + " " + str(currSection[1]) +  " " + str(currSection[2]) + ':'

            print currSection[3]
#             for word in  currSection[1]:
#                 print word.__str__().encode('utf-8','replace')
        

    def serializePhonemesForSection(self, whichSection, outputFileName):
        '''
        list of all phonemes. print to file @param outputFileName
        '''    
        lyrics = self.getLyricsForSection(whichSection)
        if not lyrics:
            sys.exit("no lyrics")
        
        writeListToTextFile(lyrics.phonemesNetwork, None,  outputFileName )
        return lyrics.phonemesNetwork
    
            
        
        
    def printSyllables(self, whichSection):
        '''
        debug: print syllables 
        '''
        
        lyrics = self.getLyricsForSection(whichSection)
        if not lyrics:
            sys.exit("no lyrics")
            
        lyrics.printSyllables
        
     
               


def loadLyrics(pathToComposition, whichSection):

    Phonetizer.initLookupTable(False,  'grapheme2METUphonemeLookupTable')

    
    os.chdir(pathToComposition)

    pathTotxt = os.path.join(pathToComposition, glob.glob("*.txt")[0])
    
    listExtensions = [ "sectionsMetadata_symbTr1.json", "sections.tsv", "sections.txt"]
    sectionFiles = findFileByExtensions(pathToComposition, listExtensions)
    sectionFile = sectionFiles[0]
        
    pathToSectionTsv = os.path.join(pathToComposition, sectionFile)
    makamScore = MakamScoreOld(pathTotxt, pathToSectionTsv )
    
    # phoneme IDs
    
    lyrics = makamScore.getLyricsForSection(whichSection)
    return lyrics

def loadMakamScore(pathToComposition):
    '''
    same as loadLyrics, but return MakamScoreOld, so that all lyrics can be shown if needed
    '''
    
    lookupTableURI= os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'grapheme2METUphonemeLookupTable')
    Phonetizer.initLookupTable(False,  lookupTableURI)
    
    os.chdir(pathToComposition)

    pathTotxt = os.path.join(pathToComposition, glob.glob("*.txt")[0])
    
    listExtensions = [ "sections.json", "sections.tsv", "sections.txt"]
    sectionFiles = findFileByExtensions(pathToComposition, listExtensions)
    sectionFile = sectionFiles[0]
        
    pathToSectionTsv = os.path.join(pathToComposition, sectionFile)
    print "using section metadata file {}".format(pathToSectionTsv)
    makamScore = MakamScoreOld(pathTotxt, pathToSectionTsv )
    return makamScore
    

def testMakamScore(argv):
        if len(argv) != 2:
            print ("usage: {} <path to symbtTr.txt and symbTr.sections.tsv>".format(argv[0]) )
            sys.exit();
        pathToComposition = argv[1]
        
        makamScore = loadMakamScore(pathToComposition)
        makamScore.printSectionsAndLyrics()
#         lyrics = loadLyrics(pathToComposition, whichSection=0)
     
      

          
             
if __name__ == '__main__':

        # only for unit testing purposes
        
        print "in Makam Score"
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/ussak--sarki--aksak--bu_aksam_gun--tatyos_efendi/']
        
        
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/rast--turku--semai--gul_agaci--necip_mirkelamoglu/']
        
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin/']
        
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/']
        
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/rast--sarki--curcuna--nihansin_dideden--haci_faik_bey/']
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/rast--sarki--sofyan--gelmez_oldu--dramali_hasan/']
        a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-for_makam-lyrics-2-audio-test-data-synthesis/rast--turku--semai--gul_agaci--necip_mirkelamoglu/']

        
        testMakamScore(a)
          
      
         