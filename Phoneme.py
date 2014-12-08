'''
Created on Oct 8, 2014

@author: joro
'''
from Phonetizer import Phonetizer
import sys
class Phoneme:
    def __init__(self, phonemeID):
        self.ID = phonemeID;
        self.duration = None;
        self.numFirstState = -1
            
    def setNumFirstState(self, numFirstState):
            self.numFirstState = numFirstState
        
    def setDuration(self, duration):
        self.duration = duration
        
    def getDuration(self):
        return self.duration
    
    def setHTKModel(self, hmmModel):
        self.htkModel = hmmModel
        
    def getNumStates(self):
        try: self.htkModel
        except NameError:
            sys.exit("cannot get numsttes. phoneme {} has no model assigned ", self.ID)
        
        return len(self.htkModel.states)
            
            
    
    def __str__(self):
        return self.ID
    
    def isVowel(self):
        
        if (self.ID == Phonetizer.METUlookupTable.get('a') or
        self.ID == Phonetizer.METUlookupTable.get('o') or
        self.ID == Phonetizer.METUlookupTable.get('O') or
        self.ID == Phonetizer.METUlookupTable.get('e') or
        self.ID == Phonetizer.METUlookupTable.get('i') or
        self.ID == Phonetizer.METUlookupTable.get('u') or
        self.ID == Phonetizer.METUlookupTable.get('U') or
        self.ID == Phonetizer.METUlookupTable.get('I') ):
            return True
        return False
    
        