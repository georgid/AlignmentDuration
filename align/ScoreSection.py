'''
Created on Jan 10, 2016

@author: joro
'''

class _Section():
    '''
    section from the composition: has lyrics
    '''
    def __init__(self):
        self.lyrics = None
    
    def setLyrics(self, lyrics):
        self.lyrics = lyrics
        

class ScoreSection(_Section):


    def __init__(self, name, startNote, endNote, melodicStructure, lyricStructure ):
        '''
        section from score, has as well musical notes related information
        '''
        _Section.__init__(self)
        
        self.name = name
        self.startNote = startNote
        self.endNote = endNote
        self.melodicStructure =  melodicStructure
        self.lyricStructure =  lyricStructure
        
    
        
    def __str__(self):
        
        return "{}\n melodic struct: {}\n lyrics struct: {}".format(self.name, self.melodicStructure, self.lyricStructure) 


class LyricsSection(_Section):
    
    def __init__(self, lyricsTextGrid,  fromSyllableIdx, toSyllableIdx  ):
        
        _Section.__init__(self)
        
        # text Grid of complete recording
        self.lyricsTextGrid = lyricsTextGrid
        self.fromSyllableIdx = fromSyllableIdx
        self.toSyllableIdx = toSyllableIdx