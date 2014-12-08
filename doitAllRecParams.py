'''
Created on Dec 5, 2014

@author: joro
'''
from doitAllRecordings import doit
import logging
import sys
import numpy

def runWithParameters(argv):
    
    ALPHAs = numpy.arange(0.81,1.0,0.01)
    
    for ALPHA in ALPHAs:
        logging.info("ALPHA = " + str(ALPHA))
        if argv[3] == 'False': 
            usePersistent =  False
        elif argv[3] == 'True':
            usePersistent =  True

        doit([argv[0], argv[1], argv[2], ALPHA, usePersistent ]  )
        
            
            

if __name__ == '__main__':
    runWithParameters(sys.argv)