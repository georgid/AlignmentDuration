'''
Created on Apr 27, 2016

@author: joro
'''

### include src folder
import os
import sys
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if parentDir not in sys.path:
    sys.path.append(parentDir)
    
from src.utilsLyrics.Utilz import readLookupTable


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