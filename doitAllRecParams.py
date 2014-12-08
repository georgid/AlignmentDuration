'''
Created on Dec 5, 2014

@author: joro
'''
from doitAllRecordings import doit
import logging
import sys
import numpy

def runWithParameters(argv):
    
    if len(argv) != 4 and  len(argv) != 5 :
            print ("usage: {}  <pathToCompositions>  <pathToRecordings> <ONLY_MIDDLE_STATE>  <usePersistentFiles=False>".format(argv[0]) )
            sys.exit();
    
    ALPHAs = numpy.arange(0.81,1.0,0.01)
    
    for ALPHA in ALPHAs:
        logging.info("ALPHA = " + str(ALPHA))
        
        
        usePersistent = False
        if len(argv) == 5:
            if argv[4] == 'False': 
                usePersistent =  False
            elif argv[4] == 'True':
                usePersistent =  True

        doit([argv[0], argv[1], argv[2], ALPHA,  argv[3], usePersistent ]  )
        
            
            

if __name__ == '__main__':
    runWithParameters(sys.argv)