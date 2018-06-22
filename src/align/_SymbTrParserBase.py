# -*- coding: utf-8 -*-

# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration
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
Created on Mar 5, 2015

@author: joro
'''


import codecs
import os
import sys
import json



from src.utilsLyrics.Utilz import  loadTextFile
from ScoreSection import ScoreSection


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
        if  'segmentations' in sectionMetadata: # use segmentations instead of sections, if no segmentations, use sections 
             scoreSectionAnnos = sectionMetadata['segmentations'] # if with_section_annotations, it is called segmentations because of symbtrdataextractor
        elif 'sections' in sectionMetadata:
            scoreSectionAnnos = sectionMetadata['sections']
        else:
            sys.exit("cannot find neither key sections nor segmentations in score metadata" )
         
        for section in scoreSectionAnnos:
                    if  'start_note' in section:
                        startNote = int(section['start_note'])
                    else:
                        startNote = int(section['startNote'])
                    
                    if 'end_note' in section:
                        endNote = int(section['end_note'])
                    else:
                        endNote = int(section['endNote']) 
                    
                    if 'lyrics_structure' in section:
                        lyrStruct = section['lyrics_structure']
                    elif 'lyric_structure' in section:
                        lyrStruct = section['lyric_structure']
                    else:
                        lyrStruct = section['lyricStructure']
                        
                    if 'melodic_structure' in section:
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
                    sectionNew = ScoreSection(section['name'],  int(section['startNote']), int(section['endNote']), section['melodicStructure'], section['lyricStructure']) 
                    
                    self.sections.append(sectionNew)
    
    def syllables2Lyrics(self):
        '''
        put lyrics into self.sectionLyrics = []
        '''
        raise NotImplementedError("a syllable2Lyrics function must be implemented")