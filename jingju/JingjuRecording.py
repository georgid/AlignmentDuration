'''
Created on May 9, 2016

@author: joro
'''
from makam.MakamRecording import _RecordingBase
from parse.TextGrid_Parsing import tierAliases, readNonEmptyTokensTextGrid
from jingju.SectionLinkJingju import SectionLinkJingju



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
        