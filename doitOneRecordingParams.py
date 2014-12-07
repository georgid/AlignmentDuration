'''
Created on Dec 5, 2014

@author: joro
'''
from doitOneRecording import doitOneRecording
import logging
import sys
import numpy

def runWithParameters(argv):
    
    ALPHAs = numpy.arange(0.81,1.0,0.01)
    
    for ALPHA in ALPHAs:
        logging.info("ALPHA = " + str(ALPHA))
        doitOneRecording([argv[0], argv[1], argv[2], ALPHA, True]  )
        
            
            

if __name__ == '__main__':
    runWithParameters(sys.argv)