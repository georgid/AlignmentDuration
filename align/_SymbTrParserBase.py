# -*- coding: utf-8 -*-

'''



@author: joro
'''


import codecs
import os
import sys
import json
from Section import Section



from utilsLyrics.Utilz import  loadTextFile


'''
Parses lyrics from symbTr v 1.0. Sections from tsv file
a list of syllables is parsed. 
Base class. DO not instantiate

TODO: take only section names from tsv file. parse sections from symbTr double spaces 
'''
class _SymbTrParserBase(object):
    
    def __init__(self, pathToSymbTrFile,  sectionMetadata):
        '''
        Constructor
        '''
        # list of note number and syllables
        self.listSyllables =[]
        self._loadSyllables( pathToSymbTrFile)


        #  list of objects of Section class
        self.sections = []
        self._loadSectionBoundaries(sectionMetadata)
#         self._loadSectionBoundaries_fileURI(sectionMetadata)

        
    
    def  _loadSyllables(self, pathToSymbTrFile):
        raise NotImplementedError("a parsing function must be implemented")

   ##################################################################################
    
    def _loadSectionBoundaries(self, sectionMetadata):
        scoreSectionAnnos = sectionMetadata['sections']
        for section in scoreSectionAnnos:
                    sectionNew = Section(section['name'],  int(section['startNote']), int(section['endNote']), section['melodicStructure'], section['lyricStructure']) 
                    
                    self.sections.append(sectionNew)
    
    def _loadSectionBoundaries_fileURI(self, sectionMetadataFileURI):
            '''
            load section boundaries from sectionMetadatafile
            '''
            if not os.path.isfile(sectionMetadataFileURI):
                sys.exit("no file {}".format(sectionMetadataFileURI))
            
            ext = os.path.splitext(os.path.basename(sectionMetadataFileURI))[1] 
            if ext == '.tsv':
                allLines = loadTextFile(sectionMetadataFileURI)
    
                for line in allLines[1:]:
                    #  triples of sectin name, start note number, end note number 
                    tokens = line.strip().split("\t")
                    if not len(tokens)==3:
                        sys.exit("tokens in line {} from file {} are not 3. make sure /t  are used".format( line, sectionMetadataFileURI))
                        
                    tmpTriplet = tokens[0], int(tokens[1]), int(tokens[2]) 
                    self.sections.append(tmpTriplet)
            ######################
            elif ext == '.json':
                
                b = open (sectionMetadataFileURI)
                scoreAnno = json.load(b)
                b.close()
                scoreSectionAnnos = scoreAnno['sections']
                
                for section in scoreSectionAnnos:
                    sectionNew = Section(section['name'],  int(section['startNote']), int(section['endNote']), section['melodicStructure'], section['lyricStructure']) 
                    
                    self.sections.append(sectionNew)
    
    def syllables2Lyrics(self):
        '''
        put lyrics into self.sectionLyrics = []
        '''
        raise NotImplementedError("a syllable2Lyrics function must be implemented")