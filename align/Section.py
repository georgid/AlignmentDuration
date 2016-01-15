'''
Created on Jan 10, 2016

@author: joro
'''

class Section(object):
    '''
    classdocs
    '''


    def __init__(self, name, startNote, endNote, melodicStructure, lyricStructure ):
        '''
        Constructor
        '''
        self.name = name
        self.startNote = startNote
        self.endNote = endNote
        self.melodicStructure =  melodicStructure
        self.lyricStructure =  lyricStructure
        
        
        