'''
    phonetizer class used to do the expansion of the graphemes in a syllable to phonemes
    For all entities of lyrics the g2p rules are the same, so Phonetizer.lookupTable should be instantiated only once on highest level  
@author: joro
'''
import sys
import os

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics')

if not pathUtils in sys.path:
    sys.path.append(pathUtils )
from Utilz import loadTextFile


def readLookupTable(URItable):
        '''
        read lookup table from file
        '''
        lookupTableURI= os.path.join(os.path.dirname(os.path.realpath(__file__)) , URItable)
            

        lookupTableRaw = loadTextFile(lookupTableURI)
        lookupTable = dict()
        for lineTable in lookupTableRaw:
            tokens = lineTable.split("\t")
            grapheme = tokens[0]
            if not isinstance(grapheme, unicode):
                    grapheme = unicode(grapheme,'utf-8')
            #non-ascii represented by digit. becasue table is reuse din matlab, who does not understand utf 
            if len(grapheme) == 4 and grapheme[0].isdigit(): 
                grapheme = "\u" + grapheme
                grapheme = grapheme.decode('unicode-escape')
            
            # one-to-one
            if len(tokens) == 2:
                phonemeTokens = tokens[1].rstrip().split()
                
                if len(phonemeTokens) == 1:
                    lookupTable[grapheme] = phonemeTokens[0]
                elif len(phonemeTokens) == 0:
                    lookupTable[grapheme] = tokens[1].rstrip()

#              one-to-more, more are separated by space
                else:
                    lookupTable[grapheme] = phonemeTokens 
            
            # one-to-more
            elif  len(tokens) > 2:
                phonemes = []
                for phonemeCurr in tokens[1:]:
                    phonemes.append(phonemeCurr.strip())  
                
                lookupTable[grapheme] = phonemes

        return lookupTable
         
      
def combineDiacriticsChars( listA, utfCode):
    '''
    if there are diaresis expressed as two chars in utf, combines them together
       @param - listA - list with letters of a word
       @return listWithCombined  
    '''
    diaresisIndeces = []
    for i, j in enumerate(listA): 
        if j == utfCode:
           diaresisIndeces.append(i)
    
    # transform diaresis
    for indexL in diaresisIndeces:
        diaresisLetter = listA.pop(indexL - 1)
        newLetter = diaresisLetter + utfCode
        listA.insert(indexL - 1, newLetter)

    # remove diaresis    
    counter = 0
    for indexL in diaresisIndeces:
         indexL = indexL - counter;  listA.pop(indexL); counter = counter + 1
    return  listA


class Phonetizer(object):
    lookupTable = dict()
    withSynthesis = 0
    phoneticDict = dict() 
    
    @staticmethod
    def initLookupTable(withSynthesis, URItable):
        # if not yet created:
        if not Phonetizer.lookupTable:
            Phonetizer.lookupTable = readLookupTable(URItable)
            Phonetizer.withSynthesis = withSynthesis
    
    @staticmethod    
    def initPhoneticDict(URLdict):
        # if not yet created:
        if not Phonetizer.phoneticDict:
            Phonetizer.phoneticDict = readLookupTable(URLdict)
        
    
#     def __init__(self):
#         
#         lookupTableURI= os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'grapheme2METUphonemeLookupTable' )
#         self.lookupTable = self._readLookupTable(lookupTableURI)
#         lookupTable = self.lookupTable
        

    @staticmethod
    def grapheme2phonemeList(grapheme, phonemesList):
        '''
        map a grapheme to a list of phonemes. used in JingJu 
        '''
        if grapheme in Phonetizer.lookupTable:
            currPhoneme = Phonetizer.lookupTable[grapheme]
            if currPhoneme != "":
                if isinstance(currPhoneme, list):
                    phonemesList.extend(currPhoneme)
                else:
                    phonemesList.append(currPhoneme)
        else:
            sys.exit("grapheme {0} not in graheme-to-phoneme lookup table".format(grapheme))
        return phonemesList
    
    @staticmethod
    def grapheme2Phoneme(word):
        '''
        grapheme2phoneme for a whole word
        '''
        
    #     wprd = word.lower()
        s = list(word)
    
        #@@@ combine two-char diacritics: 
        # TODO: not optimal has too loop in word for each diacritic type 
        
        # turkish diaeresis
        s = combineDiacriticsChars(s, u'\u0308')
         
        # telugu macron
        s = combineDiacriticsChars(s, u'\u0304')
         
        # telugu acute
        s = combineDiacriticsChars(s, u'\u0301') 
         
        # telugu dot below
        s = combineDiacriticsChars(s, u'\u0323')                      
         
        # telugu dot above
        s = combineDiacriticsChars(s, u'\u0307')                      
     
    
        phonemesList = []

        for i in range(len(s)):
            s[i] = s[i].lower()
            phonemesList = Phonetizer.grapheme2phonemeList(s[i], phonemesList)
        
                
        return phonemesList



if __name__=="__main__":
#      Phonetizer.initLookupTable(True, 'grapheme2METUphonemeLookupTableSYNTH' )
    Phonetizer.initLookupTable(False, 'phonemeMandarin2METUphonemeLookupTable' )
    print Phonetizer.lookupTable
    