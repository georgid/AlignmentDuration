# -*- coding: utf-8 -*-

'''



@author: joro
'''


import codecs
import os
import sys
import json



from utilsLyrics.Utilz import  loadTextFile
from align.ScoreSection import ScoreSection


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
        if hasattr(sectionMetadata, 'segmentations'):
            scoreSectionAnnos = sectionMetadata['segmentations'] # if with_section_annotations, it is called segmentations because of symbtrdataextractor
        else:
            scoreSectionAnnos = sectionMetadata['sections']
        
         
        for section in scoreSectionAnnos:
                    print section
                    if hasattr(section, 'start_note'):
                        startNote = int(section['start_note'])
                    else:
                        startNote = int(section['startNote'])
                    
                    if hasattr(section, 'end_note'):
                        endNote = int(section['end_note'])
                    else:
                        endNote = int(section['endNote']) 
                    
                    if hasattr(section, 'lyrics_structure'):
                        lyrStruct = section['lyrics_structure']
                    else:
                        lyrStruct = section['lyricStructure']
                        
                    if hasattr(section, 'melodic_structure'):
                        melStruct = section['melodic_structure']
                    else:
                        melStruct = section['melodicStructure']
                    
                        
                    sectionNew = ScoreSection(section['name'],  startNote, endNote, melStruct, lyrStruct) 
                    
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