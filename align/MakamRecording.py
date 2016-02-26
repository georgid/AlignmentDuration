'''
Created on Feb 9, 2016

@author: joro
'''

from utilsLyrics.Utilz import loadTextFile
from align.SectionLink import SectionLink, SectionAnno
import sys
from align.Decoder import logger

class MakamRecording:
    '''
    classdocs
    '''


    def __init__(self, makamScore, sectionLinksDict, sectionAnnosDict, withAnnotations):
        '''
        Constructor
        '''
        self.makamScore = makamScore
        
        if not withAnnotations:
            sectionLinks = parseSectionLinks(sectionLinksDict)
            self._loadsectionTimeStampsLinksNew(sectionLinks)
        else:
            self._loadsectionTimeStampsAnno(sectionAnnosDict)
        
    
    def _loadsectionTimeStampsLinksNew(self, sectionLinksTxt):

    
        self.sectionLinks = [] 
        

        for sectionLink in sectionLinksTxt:
                        
                        melodicStruct = sectionLink['name']
                        beginTs, endTs = parseTimeSectionLinkTxt(sectionLink)
                        
                        currSectionLink = SectionLink (melodicStruct, beginTs, endTs)
                        
                        self.sectionLinks.append(currSectionLink )
                        
                        
        
 
    def _loadsectionTimeStampsAnno(self, sectionAnnosDict):
            '''
            loads annotations in the form of SectionLinks from file .sectionAnno
            '''
            
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
                    
            if 'section_annotations' not in sectionAnnosDict:
                sys.exit('annotation should have key section_annotations')
                
            sectionAnnosTxt = sectionAnnosDict['section_annotations']
            self.sectionAnnos = []
            for sectionAnnoTxt in sectionAnnosTxt:
                    if 'melodicStructure' not in sectionAnnoTxt or 'lyricStructure' not in sectionAnnoTxt:
                         logger.warning("skipping parsing secionAnno {} with no lyric/melodic struct defined ...".format(sectionAnnoTxt))
                         continue
                    melodicStruct = sectionAnnoTxt['melodicStructure']
                    beginTs, endTs = parseTimeSectionLinkTxt(sectionAnnoTxt)
                        
                        
                    currSectionAnno = SectionAnno (melodicStruct, sectionAnnoTxt['lyricStructure'], beginTs, endTs )
                    currSectionAnno.matchToSection(self.makamScore.symbTrParser.sections)
                    
                    
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

