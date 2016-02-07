# -*- coding: utf-8 -*-

'''



@author: joro
'''


import codecs
import os
import sys
import json

# parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
# pathUtils = os.path.join(parentDir, 'utilsLyrics') 
# # pathUtils = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/utilsLyrics'
# 
# # utils_ = imp.load_source('Utils', pathUtils  )
# 
# sys.path.append(pathUtils )

from utilsLyrics.Utilz import  loadTextFile


'''
Parses lyrics from symbTr v 1.0. Sections from tsv file
a list of syllables is parsed. 
Base class. DO not instantiate

TODO: take only section names from tsv file. parse sections from symbTr double spaces 
'''
class _SymbTrParserBase(object):
    
    def __init__(self, pathToSymbTrFile,  pathToSectionFile):
        '''
        Constructor
        '''
        # list of note number and syllables
        self.listSyllables =[]
        self._loadSyllables( pathToSymbTrFile)


        # section boundaries.                 #  triples of sectin name, start note, edn note 
        self.sectionboundaries = []
        self._loadSectionBoundaries(pathToSectionFile)
        
        # list of  section names and their lyrics. 
        self.sectionLyrics = []
    
    def  _loadSyllables(self, pathToSymbTrFile):
        raise NotImplementedError("a parsing function must be implemented")

   ##################################################################################

    def _loadSectionBoundaries(self, URISectionFIle):
            if not os.path.isfile(URISectionFIle):
                sys.exit("no file {}".format(URISectionFIle))
            
            ext = os.path.splitext(os.path.basename(URISectionFIle))[1] 
            if ext == '.tsv':
                allLines = loadTextFile(URISectionFIle)
    
                for line in allLines[1:]:
                    #  triples of sectin name, start note number, end note number 
                    tokens = line.strip().split("\t")
                    if not len(tokens)==3:
                        sys.exit("tokens in line {} from file {} are not 3. make sure /t  are used".format( line, URISectionFIle))
                        
                    tmpTriplet = tokens[0], int(tokens[1]), int(tokens[2]) 
                    self.sectionboundaries.append(tmpTriplet)
            ######################
            elif ext == '.json':
                
                b = open (URISectionFIle)
                scoreAnno = json.load(b)
                b.close()
                scoreSectionAnnos = scoreAnno['sections']
                
                for section in scoreSectionAnnos:
                    tmpTriplet = section['name'],  int(section['startNote']), int(section['endNote']) 
                    self.sectionboundaries.append(tmpTriplet)
    
    def syllables2Lyrics(self):
        '''
        put lyrics into self.sectionLyrics = []
        '''
        raise NotImplementedError("a syllable2Lyrics function must be implemented")