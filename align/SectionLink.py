'''
Created on Dec 28, 2015

@author: joro
'''

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
        
#         self.fromSyllableIdx = fromSyllableIdx
#         self.toSyllableIdx = toSyllableIdx
#         
    def setSelectedSections(self, sections):
        '''
        selected sections after alignment 
        '''
        self.selectedSections = sections