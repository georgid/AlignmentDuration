# -*- coding: utf-8 -*-
'''
contains SymbTr Parser class 
 
@author: joro
'''
import codecs
import os
import sys
from Word import Word
from Syllable import Syllable, MINIMAL_DURATION_UNIT
from Lyrics import Lyrics
from _SymbTrParserBase import _SymbTrParserBase
from Phonetizer import Phonetizer

# parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
# pathUtils = os.path.join(parentDir, 'utilsLyrics') 
# # pathUtils = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/utilsLyrics'
# 
# # utils_ = imp.load_source('Utils', pathUtils  )
# 
# sys.path.append(pathUtils )

from utilsLyrics.Utilz import  loadTextFile


class SymbTrParser(_SymbTrParserBase):
    '''
    Parses lyrics from symbTr v 1.0 and Sections from tsv file.
    
    a list of syllables from column 12: soz1/söz1 is parsed. 
    Then concatenated into words if needed 
    TODO: take only section names from tsv file. parse sections from symbTr double s 
    '''


    
    def __init__(self, pathToSymbTrFile, URI_SectionFile):
        '''
        Constructor
        '''
        _SymbTrParserBase.__init__(self,pathToSymbTrFile,URI_SectionFile)
        
        
   
    
   
   
   ##################################################################################
     
    '''
    load all notes with syllables from symbTr file. 
    ignores all notes with no syllable!
    calculate syllable duration from the associated notes 
    '''

   

    def _loadSyllables(self, pathToSymbTrFile):
        '''
        top-most function
        '''
             
        allLines = loadTextFile(pathToSymbTrFile)
        
        currSyllable = None
        currSyllTotalDuration = None
        
        # skip first line. 
        for  i in range( 1, len(allLines) ):
            
            line = allLines[i]
            line = line.replace(os.linesep,'') # remove end line in an os-independent way 
            line = line.replace('\r','') 
            
            tokens = line.split("\t")
            if len(tokens) < 12:
                print "TOKENS ARE 11, no syllable ";  sys.exit()
            
            # sanity check  MINIMAL_DURATION of embelishments. 
#             hack: change crazy small notes to min duration. it does not matter a lot
            if tokens[7] > MINIMAL_DURATION_UNIT and  tokens[1] == '8':
                tokens[7] = MINIMAL_DURATION_UNIT


            currNoteDuration = float(tokens[6]) / float(tokens[7]) * MINIMAL_DURATION_UNIT
                
            currSyllable, currSyllTotalDuration = self.parseCurrTxtToken(currSyllable, currSyllTotalDuration, tokens, currNoteDuration)
            
            
        #end parsing loop
            
        # store last
        currSyllable.setDurationInMinUnit(currSyllTotalDuration)
        self.listSyllables.append(currSyllable)
    
    


    def parseCurrTxtToken(self, currSyllable, syllTotalDuration, tokens, currDuration):
        '''
        parse  the text: (soz1/söz1 token) containing the  syllable text. discriminate between cases of SAZ and so on
        '''
        currTxtToken = tokens[11]
        
        # skip ARANAGME sections
#         if currTxtToken.startswith(u'ARANA\u011eME') or currTxtToken.startswith(u'ARANAGME'): #             or tokens[1] == '8':             # skip embellishments. they dont count in duration
#             return None,None
        
         # '' (no lyrics at note) so still at same syllable
        if currTxtToken == '' and not (currSyllable is None) and not (syllTotalDuration is None):
            syllTotalDuration = syllTotalDuration + currDuration 
        
        elif currTxtToken.startswith('.'): #still in same _SAZ_ syllable
            if not (currSyllable is None) and not (syllTotalDuration is None) and currSyllable.text ==  "_SAZ_ ":
                syllTotalDuration = syllTotalDuration + currDuration
            
            # new syllable starting with '.'
            else:
                currSyllable, syllTotalDuration = self.finishCurrentAndCreateNewSyllable(currSyllable, syllTotalDuration, tokens, currDuration)
        
        #  not '' and not '.'   thus new syllable starts
        else:
            currSyllable, syllTotalDuration = self.finishCurrentAndCreateNewSyllable(currSyllable, syllTotalDuration, tokens, currDuration)
        
      
        return currSyllable, syllTotalDuration        


    
    
    def finishCurrentAndCreateNewSyllable(self, currSyllable, syllTotalDuration, tokens, currDuration):
        '''
        when syllable finished
        '''
        if not (currSyllable is None) and not (syllTotalDuration is None): # save last syllable and duration
            currSyllable.setDurationInMinUnit(syllTotalDuration)
            self.listSyllables.append(currSyllable)
        
        # init next syllable and its duration
        currSyllable = self.createSyllable(tokens)
        syllTotalDuration = currDuration
        return currSyllable, syllTotalDuration



    
    def createSyllable(self, tokens):
        '''
        create new syllable
        distinguish btw vocal syllable and instrumental syllable  
        '''
            
        currTxtToken = tokens[11]
        if currTxtToken.startswith('SAZ') or currTxtToken.startswith('.') or  currTxtToken.startswith(u'ARANA\u011eME') or currTxtToken.startswith(u'ARANAGME'):
            #  indicates end of word, it is stripped later by the code
            currSyllable = Syllable("_SAZ_ ", tokens[0])
        else:
            text = tokens[11].replace('_',' ')
            currSyllable = Syllable(text, tokens[0])
        
        return currSyllable
    
                    
#                         self.listSyllables.append(tupleSyllable)
            
     

       
     ##################################################################################
   
     
     
    def syllables2Lyrics(self): 
        """
        construct words from syllables for all  sections
        use Lyrics and Syllable classes.
        """  
        words = []
              
        for currSectionBoundary in self.sectionboundaries:
            
            # double empty space marks section end, but we dont use it for now             
            words = self.syllable2LyricsOneSection(currSectionBoundary[1], currSectionBoundary[2])
            
            # store lyrics
            lyrics = Lyrics(words)            
            self.sectionLyrics.append(lyrics)
            
          


    def syllable2LyricsOneSection(self, startNoteNumber, endNoteNumber):
        """
             combine syllables into listWords. use Word and Syllable classes. 
                for one section only .
                add syllables until noteNumber of current Syllable reaches  
            @param endNoteNumber:
             
            @param beginIndex: - beginning current index syllable
        """
        syllablesInCurrWord  = []
        listWords = []
        
        beginIndex = self._findSyllableIndex(startNoteNumber)
        # wrong noteNumber for section begin or no lyrics in section
        if (beginIndex == -1):
            return listWords
        
        
        while (beginIndex <= len(self.listSyllables)-1 # sanity check
                    and self.listSyllables[beginIndex].noteNum <= endNoteNumber ): # while note number associated with syllable is less than last note number in section 
                    
                        currSyllable = self.listSyllables[beginIndex]
                        
                        # construct new word at whitespace
                        if currSyllable.text[-1].isspace():
                            
                            word, syllablesInCurrWord = createWord(syllablesInCurrWord, currSyllable)
                            
                            # ignore SAZ
#                             if not word.text == '_SAZ_':
                            listWords.append(word)
                            
                            #restart counting
                            syllablesInCurrWord = []
                        
                        # still same word    
                        else:
                            syllablesInCurrWord.append(currSyllable)
                            
                            
                        beginIndex = beginIndex + 1
                        
        return listWords
  

    
        
    def _findSyllableIndex(self, noteNumberQuery):
        '''
        find which syllable has  queried note number 
        @param noteNumberQuery:  
        used only for begin syllables
        use binary search
        '''
        lo = 0
        high = len(self.listSyllables)
        
        while lo<high:
            mid = (lo+high)//2
            noteNum = self.listSyllables[mid].noteNum
            if noteNumberQuery < noteNum:
                high = mid
            elif noteNumberQuery > noteNum:
                lo = mid + 1
            else:
                return mid
       
        # no syllable with lyrics (case of lyrics starting after auftakt on istrument at begining of section) => return closest following syllable with lyrics  
      
        return high
             
            
        
        
# begin index does not update, because no change in aranagme. 
    def syllable2WordOneSectionOld(self, beginIndex, endNoteNumber):
        """    
            @deprecated: 
             combine syllables into listWords. use Word and Syllable classes. 
                for one section only .
                add syllables until noteNumber of current Syllable reaches  @param endNoteNumber 
            @param beginIndex - beginning current index syllable
            @return beginIndex - final current index syllable
        """
        syllablesInCurrWord  = []
        listWords = []
        
        beginSyllable = self.listSyllables[beginIndex]
        while (beginIndex <= len(self.listSyllables)-1 # sanity check
                    and beginSyllable.noteNum <= endNoteNumber ): # while note number associated with syllable is less than last note number in section 
                    
                        currSyllable = self.listSyllables[beginIndex]
    
                            
                        
                        # construct new word at whitespace
                        if currSyllable.text[-1].isspace():
                            
                            # dont need whitespaces in syllables
                            currSyllable.text = currSyllable.text.rstrip()
                            syllablesInCurrWord.append(currSyllable)
                        
                            word = Word(syllablesInCurrWord)
                            listWords.append(word)
                            
                            #restart counting
                            syllablesInCurrWord = []

                        else:
                            syllablesInCurrWord.append(currSyllable)
                            
                        beginIndex = beginIndex + 1
                        
        return listWords, beginIndex
        
     
# begin index does not update, because no change in aranagme. 

def createWord(syllablesInCurrWord, currSyllable):
        '''
        create a new word ending in currect syllable  
        '''        
        currSyllable.text = currSyllable.text.rstrip()
        currSyllable.setHasShortPauseAtEnd(False)
        syllablesInCurrWord.append(currSyllable)
    # create new word
        word = Word(syllablesInCurrWord)
        return word, syllablesInCurrWord
    

#################################################################################

if __name__ == "__main__":
    
    pathTxt=  '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey.txt'
    pathTsv= '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey/nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey.sections.tsv'
    
    pathTxt=  '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin.txt'
    pathTsv= '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin.sections.tsv'
    
    
    
    Phonetizer.initLookupTable(False,  'grapheme2METUphonemeLookupTable')

    symbTrParser = SymbTrParser(pathTxt, pathTsv)
        
    symbTrParser.syllables2Lyrics()

    # print them, put instrument as name
    print symbTrParser.sectionLyrics[5]
    print symbTrParser.sectionLyrics[0]
