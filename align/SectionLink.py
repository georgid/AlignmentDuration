'''
Created on Dec 28, 2015

@author: joro
'''
import sys
from align.ParametersAlgo import ParametersAlgo
from align.LyricsWithModelsGMM import LyricsWithModelsGMM
from align.LyricsWithModelsHTK import LyricsWithModelsHTK
import logging
from align.LyricsParsing import loadOraclePhonemes
import tempfile
import os
audioTmpDir = tempfile.mkdtemp()

class _SectionLinkBase():

    
    def __init__(self, URIWholeRecording, beginTs, endTs):
        '''
        Constructor
        '''
        basename = os.path.basename(URIWholeRecording)
        self.URIRecordingChunk = os.path.join(audioTmpDir, basename + "_" + "{}".format(beginTs) + '_' + "{}".format(endTs))

        self.beginTs = beginTs
        self.endTs = endTs
        # composition section. could be LyricsSection or ScoreSection
        self.section = None
        
        
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
    
    
    def loadSmallAudioFragment( self, featureExtractor, extractedPitchList,  URIrecordingNoExt,    htkParserOrFold):
        '''
        test duration-explicit HMM with audio features from real recording and htk-loaded htkParserOrFold
        asserts it works. no results provided 
        '''
        
        featureVectors = featureExtractor.loadMFCCs(URIrecordingNoExt, extractedPitchList,  self) #     featureVectors = featureVectors[0:1000]
    
        
        if ParametersAlgo.FOR_JINGJU:
            self.lyricsWithModels = LyricsWithModelsGMM( self.section.lyrics, htkParserOrFold,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
        elif ParametersAlgo.FOR_MAKAM:
            self.lyricsWithModels = LyricsWithModelsHTK( self.section.lyrics, htkParserOrFold,  ParametersAlgo.DEVIATION_IN_SEC, ParametersAlgo.WITH_PADDED_SILENCE)
        else:
            sys.exit('neither JINGJU nor MAKAM.')
    
        if self.lyricsWithModels.getTotalDuration() == 0:
            logging.warning("total duration of segment {} = 0".format(self.URIRecordingChunk))
            return None, None, None
        
        
        # needed only with duration htkParserOrFold
        self.lyricsWithModels.duration2numFrameDuration(featureVectors, URIrecordingNoExt)
    #     lyricsWithModels.printPhonemeNetwork()

        return featureVectors
    
    
    
    def loadSmallAudioFragmentOracle(self):
        raise NotImplementedError('loadSmallAudioFragmentOracle not implemeted')    
        
        
        
        

class SectionLinkMakam(_SectionLinkBase):
    '''
    classdocs
    '''
    

    def __init__(self, URIWholeRecording, melodicStructure, beginTs, endTs):
        '''
        Constructor
        '''
        _SectionLinkBase.__init__(self, URIWholeRecording, beginTs, endTs)
        self.melodicStructure = melodicStructure
  
        
    def loadSmallAudioFragmentOracle( self, htkParser):

        
        # lyricsWithModelsORacle used only as helper to get its stateNetwork with durs, but not functionally - e.g. their models are not used
        withPaddedSilence = False # dont models_makam silence at end and beginnning. this away we dont need to do annotatation of sp at end and beginning 
        self.lyricsWithModels = LyricsWithModelsHTK(self.section.lyrics,  htkParser,  ParametersAlgo.DEVIATION_IN_SEC, withPaddedSilence)
        
        
        URIrecordingTextGrid  = self.URIRecordingChunk  + '.TextGrid'
        fromSyllableIdx = 1; toSyllableIdx = 8
        phonemeAnnotaions = loadOraclePhonemes(URIrecordingTextGrid, fromSyllableIdx, toSyllableIdx)   
    
        
        self.lyricsWithModels.setPhonemeNumFrameDurs( phonemeAnnotaions)
        
        
        
        

        


          
              
        
        
class SectionAnnoMakam(SectionLinkMakam):
    '''
    unlike a like that has only match to melodicStrcuture, sectionAnno has link to exactSetion through tuple (melodicStructure, lyricsStucture)
    SO it can be matched unambigously to a particular ScoreSection
    '''
    
    def __init__(self, URIWholeRecording, melodicStructure, lyricStructure, beginTs, endTs):
        SectionLinkMakam.__init__(self, URIWholeRecording, melodicStructure, beginTs, endTs)
        self.lyricStructure = lyricStructure
        
    
    def matchToSection(self,  scoreSections):
        if self.lyricStructure == None:
           sys.exit('cannot match link to section. No lyricStructure defined')
        
        for scoreSection in scoreSections:
            if self.melodicStructure == scoreSection.melodicStructure and self.lyricStructure == scoreSection.lyricStructure:
                self.setSection(scoreSection)
                break  