# -*- coding: utf-8 -*-


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

Created on Mar 3, 2014

@author: joro
'''


import codecs
import os
import sys
import json

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics') 
# pathUtils = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/utilsLyrics'

# utils_ = imp.load_source('Utils', pathUtils  )

sys.path.append(pathUtils )

from utilsLyrics.Utilz import  loadTextFile


'''
Parses lyrics from symbTr v 1.0. Sections from tsv file
a list of syllables is parsed. 
Base class. DO not instantiate

TODO: take only section names from tsv file. parse sections from symbTr double spaces 
'''
class _SymbTrParserBaseOld(object):
    
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
                sectionMetadata = json.load(b)
                b.close()
                
                if  'segmentations' in sectionMetadata: # use segmentations instead of sections, if no segmentations, use sections 
                    scoreSectionAnnos = sectionMetadata['segmentations'] # if with_section_annotations, it is called segmentations because of symbtrdataextractor
                elif 'sections' in sectionMetadata:
                    scoreSectionAnnos = sectionMetadata['sections']
                else:
                    sys.exit("cannot find neither key sections nor segmentations in score metadata" )
         
         
                scoreSectionAnnos = sectionMetadata['sections']

                for section in scoreSectionAnnos:
                            print section
                            if  'start_note' in section:
                                startNote = int(section['start_note'])
                            else:
                                startNote = int(section['startNote'])
                            
                            if 'end_note' in section:
                                endNote = int(section['end_note'])
                            else:
                                endNote = int(section['endNote']) 
                        
                
                            tmpTriplet = (section['name'],  startNote, endNote)
                            self.sectionboundaries.append(tmpTriplet)
    
    def syllables2Lyrics(self):
        '''
        put lyrics into self.sectionLyrics = []
        '''
        raise NotImplementedError("a syllable2Lyrics function must be implemented")