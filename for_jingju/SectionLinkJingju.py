'''
Created on May 9, 2016

@author: joro
'''
from align.SectionLink import _SectionLinkBase
from for_jingju.ParsePhonemeAnnotation import loadPhonemesAnnoOneSyll

class SectionLinkJingju(_SectionLinkBase):
    
    def __init__(self, URIWholeRecording, beginTs, endTs, isLastSyllLong, isNonKeySyllLong):
        
        _SectionLinkBase.__init__(self, URIWholeRecording, beginTs, endTs)
        self.isLastSyllLong = isLastSyllLong
        self.isNonKeySyllLong = isNonKeySyllLong
        
    
    
    def loadSmallAudioFragmentOracle(self, htkParser):
        
        lyricsTextGrid = self.section.lyricsTextGrid
        # get start and end phoneme indices from TextGrid
        self.lyricsWithModels = []
        for idx, syllableIdx in enumerate(range(self.section.fromSyllableIdx, self.section.toSyllableIdx+1)): # for each  syllable including silent syllables
            # go through the phonemes. load all 
            currSyllable = self.listWordsFromTextGrid[idx].syllables[0]
            phonemesAnno, syllableTxt = loadPhonemesAnnoOneSyll(lyricsTextGrid, syllableIdx, currSyllable)
            self.lyricsWithModels.extend(phonemesAnno)