'''
Created on Jan 10, 2016

@author: joro
'''


class LyricsSection():
    '''
    Section from the composition: used only if section read from score. TODO: deprecate.

    '''
    
    def __init__(self, lyricsTextGrid,  fromSyllableIdx, toSyllableIdx  ):
        
        
        # text Grid of complete recording
        self.lyricsTextGrid = lyricsTextGrid
        self.fromSyllableIdx = fromSyllableIdx
        self.toSyllableIdx = toSyllableIdx
        

class ScoreSection():


    def __init__(self, name, startNote, endNote, melodicStructure, lyricStructure ):
        '''
        section from score, has as well musical notes related information
        '''
      
        
        
        self.name = name
        self.startNote = startNote
        self.endNote = endNote
        self.melodicStructure =  melodicStructure
        self.lyricStructure =  lyricStructure
        

        
        
    def __str__(self):
        
        return "{}\n melodic struct: {}\n lyrics struct: {}".format(self.name, self.melodicStructure, self.lyricStructure) 

