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
Created on Feb 9, 2016

@author: joro
'''

from src.align.SectionLink import SectionLinkMakam, SectionAnnoMakam
import sys
from src.align.Decoder import logger
import os



class _RecordingBase():

    def __init__(self, mbRecordingID, audioFileURI, score):
        '''
        Constructor
        '''
        
        self.mbRecordingID = mbRecordingID
        
        self.recordingNoExtURI = os.path.splitext(audioFileURI)[0]  
        
        path, fileName = os.path.split(audioFileURI)
        path, self.which_fold = os.path.split(path) # which Fold
        
        self.score = score
        
        self.sectionAnnos = []

        self.sectionLinks = []
        
        self.sectionLinksOrAnnoDict = {}
    
    
    def _loadsectionTimeStampsLinks(self, sectionAnnosDict):
        raise NotImplementedError('_loadsectionTimeStamps links not impl')
             

class MakamRecording(_RecordingBase):
    '''
    classdocs
    '''


    def __init__(self, mbRecordingID, audioFileURI, score, sectionLinksOrAnnoDict, withAnnotations):
        '''
        Constructor
        '''
        _RecordingBase.__init__(self, mbRecordingID, audioFileURI, score)
        
        '''
        the dict as it is stored for later usage
        '''
        self.sectionLinksOrAnnoDict = sectionLinksOrAnnoDict
        
        # expand dict to objects
        if not withAnnotations:
            sectionLinks = parseSectionLinks(sectionLinksOrAnnoDict)
            self._loadsectionTimeStampsLinks(sectionLinks)
        else: # sectionLinksOrAnnoDict is alias for sectionAnnosDict
            self._loadsectionTimeStampsAnno(sectionLinksOrAnnoDict)
        
    
    def _loadsectionTimeStampsLinks(self, sectionLinksTxt):

    
        for idx, sectionLink in enumerate(sectionLinksTxt):
                        
                        melodicStruct = sectionLink['name']
                        beginTs, endTs = parseTimeSectionLinkTxt(sectionLink)
                        
                        currSectionLink = SectionLinkMakam (self.recordingNoExtURI, melodicStruct, beginTs, endTs)
                        currSectionLink.counter = idx
                        self.sectionLinks.append(currSectionLink )
                        
                        
        
 
    def _loadsectionTimeStampsAnno(self, sectionAnnosDict):
            '''
            loads annotations in the same format as SectionLinks from file .sectionAnno
            '''
            
#################### from file ####################            
#             if not os.path.isfile(URISectionsAnnotationsFile):
#                     sys.exit("no file {}".format(URISectionsAnnotationsFile))
#             
#             ext = os.path.splitext(os.path.basename(URISectionsAnnotationsFile))[1] 
#             if ext == '.txt' or ext=='.tsv':
#                 lines = loadTextFile(URISectionsAnnotationsFile)
#                 
#                 for line in lines:
#                     tokens =  line.split()
#             
#                              
#                     self.beginTs.append(float(tokens[0]))
#                     self.endTs.append(float(tokens[1]))
#                     self.sectionNamesSequence.append(tokens[2])
#     
#     
#             elif ext == '.json':

################ from dict as json directly                    
            if 'section_annotations' not in sectionAnnosDict:
                sys.exit('annotation should have key section_annotations')
                
            sectionAnnosTxt = sectionAnnosDict['section_annotations']
            
            for idx, sectionAnnoTxt in enumerate(sectionAnnosTxt):
                    if 'melodicStructure' not in sectionAnnoTxt or 'lyricStructure' not in sectionAnnoTxt:
                         logger.warning("skipping parsing secionAnno {} with no lyric/melodic struct defined ...".format(sectionAnnoTxt))
                         continue
                    melodicStruct = sectionAnnoTxt['melodicStructure']
                    beginTs, endTs = parseTimeSectionLinkTxt(sectionAnnoTxt)
                        
                        
                    currSectionAnno = SectionAnnoMakam (self.recordingNoExtURI, melodicStruct, sectionAnnoTxt['lyricStructure'], beginTs, endTs )
                    sections = self.score.symbTrParser.sections
                    currSectionAnno.matchToSection(sections)
                    currSectionAnno.counter = idx
                    
                    self.sectionAnnos.append(currSectionAnno )
                                                       
                          
                    
                   
#             else: 
#                 sys.exit("section annotation file {} has not know file extension.".format(URISectionsAnnotationsFile) )       
            
 

def parseSectionLinks(sectionLinksDict):
    '''
    helper method. vesion seciton Links 0.2
    '''
    if len(sectionLinksDict.keys()) != 1:
        raise Exception('More than one work for recording {} Not implemented!'.format(sectionLinksDict))
# first work only. sectionLinks format 0.2
    work = sectionLinksDict[sectionLinksDict.keys()[0]]
    sectionLinks = work['links']
    return sectionLinks 



def parseTimeSectionLinkTxt(sectionLink):

       
        
        beginTimeStr = str(sectionLink['time'][0])
        beginTimeStr = beginTimeStr.replace("[", "")
        beginTimeStr = beginTimeStr.replace("]", "")
        beginTs = float(beginTimeStr)
        
        endTimeStr = str(sectionLink['time'][1])
        endTimeStr = endTimeStr.replace("[", "")
        endTimeStr = endTimeStr.replace("]", "")
        endTs = float(endTimeStr)
        
        return beginTs, endTs

