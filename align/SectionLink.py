'''
Created on Dec 28, 2015

@author: joro
'''
import sys

class SectionLink(object):
    '''
    classdocs
    '''


    def __init__(self, melodicStructure, beginTs, endTs):
        '''
        Constructor
        '''
        self.melodicStructure = melodicStructure
        self.beginTs = beginTs
        self.endTs = endTs
        # composition section. could be LyricsSection or ScoreSection
        self.section = None
        


#   
    def setSection(self, section):
        '''
        could be LyricsSection or ScoreSection
        '''
        self.section = section
        
      
    def setSelectedSections(self, sections):
        '''
        selected sections after alignment with lyrics refinent 
        '''
        self.selectedSections = sections
        

class SectionLinkJingju(SectionLink):
    
    def __init__(self,  beginTs, endTs, isLastSyllLong, isNonKeySyllLong):
        
        SectionLink.__init__(self, 'dummyMelStruct', beginTs, endTs)
        self.isLastSyllLong = isLastSyllLong
        self.isNonKeySyllLong = isNonKeySyllLong
          
        
        
class SectionAnno(SectionLink):
    '''
    unlike a like that has only match to melodicStrcuture, sectionAnno has link to exactSetion through tuple (melodicStructure, lyricsStucture)
    SO it can be matched unambigously to a particular ScoreSection
    '''
    
    def __init__(self, melodicStructure, lyricStructure, beginTs, endTs):
        SectionLink.__init__(self,melodicStructure, beginTs, endTs)
        self.lyricStructure = lyricStructure
        
    
    def matchToSection(self,  scoreSections):
        if self.lyricStructure == None:
           sys.exit('cannot match link to section. No lyricStructure defined')
        
        for scoreSection in scoreSections:
            if self.melodicStructure == scoreSection.melodicStructure and self.lyricStructure == scoreSection.lyricStructure:
                self.setSection(scoreSection)
                break  