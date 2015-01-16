'''
Created on Jan 13, 2015

@author: joro
'''
import unittest
import Phonetizer2

class Tests(unittest.TestCase):
    
    def testReadTable(self):
        lookupTable = Phonetizer2.readLookupTable(lookupTableURI='lookupTable')
        print lookupTable
        self.assertEquals(2, 2, 'blah')
        