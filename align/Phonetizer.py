'''
Created on Apr 27, 2016

@author: joro
'''
from utilsLyrics.Utilz import readLookupTable


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