'''
    phonetizer class used to do the expansion of the graphemes in a syllable to phonemes
    For all entities of lyrics the g2p rules are the same, so PhonetizerMakam.lookupTable should be instantiated only once on highest level  
@author: joro
'''
import sys
from utilsLyrics.Utilz import readLookupTable




      
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


class PhonetizerMakam(object):
    lookupTable = dict()
    withSynthesis = 0
    phoneticDict = dict() 
    
    @staticmethod
    def initLookupTable(withSynthesis, URItable):
        # if not yet created:
        if not PhonetizerMakam.lookupTable:
            PhonetizerMakam.lookupTable = readLookupTable(URItable)
            PhonetizerMakam.withSynthesis = withSynthesis
    
    @staticmethod    
    def initPhoneticDict(URLdict):
        # if not yet created:
        if not PhonetizerMakam.phoneticDict:
            PhonetizerMakam.phoneticDict = readLookupTable(URLdict)
        
    
       

    @staticmethod
    def grapheme2phonemeList(grapheme, phonemesList):
        '''
        map a grapheme to a list of phonemes. used in JingJu 
        '''
        if grapheme in PhonetizerMakam.lookupTable:
            currPhoneme = PhonetizerMakam.lookupTable[grapheme]
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
            phonemesList = PhonetizerMakam.grapheme2phonemeList(s[i], phonemesList)
        
                
        return phonemesList



if __name__=="__main__":
#      PhonetizerMakam.initLookupTable(True, 'grapheme2METUphonemeLookupTableSYNTH' )
    PhonetizerMakam.initLookupTable(False, 'phonemeMandarin2METUphonemeLookupTable' )
    print PhonetizerMakam.lookupTable
    