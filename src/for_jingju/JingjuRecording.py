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
Created on May 9, 2016

@author: joro
'''
from for_makam.MakamRecording import _RecordingBase
from parse.TextGrid_Parsing import tierAliases, readNonEmptyTokensTextGrid
from for_jingju.SectionLinkJingju import SectionLinkJingju



class JingjuRecording(_RecordingBase):
    '''
    classdocs
    '''


    def __init__(self, mbRecordingID, audioFileURI, score, annotationURI, annotaionLinesListNoPauses ):
        '''
        Constructor
        '''
        _RecordingBase.__init__(self, mbRecordingID, audioFileURI, score)
        
        self._loadsectionTimeStampsLinks(annotationURI, annotaionLinesListNoPauses)
        self.sectionLinksOrAnnoDict = {}

        # list sections as dicts
        sectionAnnosMelStructList = []
        for i, sectionAnno in enumerate(self.sectionAnnos):
            currSectionMelStruct = {}
            currSectionMelStruct['melodicStructure']= 'line_' + str(i+1)
            currSectionMelStruct['time']= [sectionAnno.beginTs,sectionAnno.endTs]
            sectionAnnosMelStructList.append(currSectionMelStruct)
        self.sectionLinksOrAnnoDict['section_annotations'] = sectionAnnosMelStructList
        
    def _loadsectionTimeStampsLinks(self, annotationURI, annotaionLinesListNoPauses):

        
        isNonKeySyllLevel = tierAliases.isNonKeySyllLong # read lines (sentences) tier
        dummy, isNonKeySyllLongFlags =  readNonEmptyTokensTextGrid(annotationURI, isNonKeySyllLevel, 0, -1)
        
    #     isLastSyllLevel = tierAliases.isLastSyllLong # read lines (sentences) tier
    #     dummy, isLastSyllLongFlags =  readNonEmptyTokensTextGrid(annotationURI, isLastSyllLevel, 0, -1)
        
        # instead stub to avoid preparing isNonKeySyllLong  tier in praat 
        isLastSyllLongFlags = [[0,0,0]] * len(isNonKeySyllLongFlags)
        
        
        for currSentence, currLyricsSection,  isLastSyllLongFlag, isNonKeySyllLongFlag in zip(annotaionLinesListNoPauses, self.score.lyricsSections,  isLastSyllLongFlags, isNonKeySyllLongFlags):
        
            currSentenceBeginTs = currSentence[0]
            currSentenceEndTs = currSentence[1]
    
            
            currSectionLink = SectionLinkJingju(self.recordingNoExtURI, currSentenceBeginTs, currSentenceEndTs, isLastSyllLongFlag[2], isNonKeySyllLongFlag[2])
            currSectionLink.setSection(currLyricsSection)
            
            self.sectionAnnos.append(currSectionLink)


 
class JingjuScore():
    def __init__(self, lyricsSections):
        self.lyricsSections = lyricsSections
        