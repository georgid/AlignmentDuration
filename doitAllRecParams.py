'''
Created on Dec 5, 2014

@author: joro
'''
from doitAllRecordings import doit
import logging
import sys
import numpy

def runWithParameters(argv):
    
    ALPHAs = numpy.arange(0.8,1.0,0.01)
    
    for ALPHA in ALPHAs:
        logging.info("ALPHA = " + str(ALPHA))
        doit([argv[0], argv[1], argv[2], ALPHA, True]  )
        
            
            

if __name__ == '__main__':
    runWithParameters(sys.argv)