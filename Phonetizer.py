'''
    phonetizer class used to do the expansion of the graphemes in a syllable to phonemes
    For all entities of lyrics the g2p rules are the same, so Phonetizer.lookupTable should be instantiated only once on highest level  
@author: joro
'''
import sys
import os

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 
pathUtils = os.path.join(parentDir, 'utilsLyrics')

if not pathUtils in sys.path:
    sys.path.append(pathUtils )
from Utilz import loadTextFile


def readLookupTable():
        '''
        read lookup table from file
        '''
        lookupTableURI= os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'grapheme2METUphonemeLookupTable' )
        
        lookupTableRaw = loadTextFile(lookupTableURI)
        lookupTable = dict()
        for lineTable in lookupTableRaw:
            tokens = lineTable.split("\t")
            grapheme = tokens[0]
            if not isinstance(grapheme, unicode):
                    grapheme = unicode(grapheme,'utf-8')
            if len(grapheme) == 4 and grapheme[0].isdigit(): 
                grapheme = "\u" + grapheme
                grapheme = grapheme.decode('unicode-escape')
            
            lookupTable[grapheme] = tokens[1].rstrip()
            
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
    lookupTable = {}
    
    @staticmethod
    def initLookupTable():
        if not Phonetizer.lookupTable:
            Phonetizer.lookupTable = readLookupTable()
    
#     def __init__(self):
#         
#         lookupTableURI= os.path.join(os.path.dirname(os.path.realpath(__file__)) , 'grapheme2METUphonemeLookupTable' )
#         self.lookupTable = self._readLookupTable(lookupTableURI)
#         lookupTable = self.lookupTable
        

    @staticmethod
    def grapheme2Phoneme(word):
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
            if s[i] in Phonetizer.lookupTable:
                currPhoneme = Phonetizer.lookupTable[s[i]]
                if currPhoneme != "":
                        phonemesList.append(currPhoneme)
            else:
                sys.exit("grapheme {0} not in gpraheme-to-phoneme lookup table".format(s[i]) )
        
                
        return phonemesList



if __name__=="__main__":
     Phonetizer.initLookupTable()
     print Phonetizer.lookupTable
    