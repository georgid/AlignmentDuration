'''
Created on Nov 4, 2014

@author: joro
'''
import numpy
import sys
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# in backtracking allow to start this much from end back
TOTAL_ALLOWED_DEV_COEFF= 0.2


class Path(object):
    '''
    Result path postprocessing
    '''

    def __init__(self, chiBackPointers, psiBackPointer):
        '''
        Constructor
        '''
        # detected durations
        self.durations = []
        # ending time for each state
        self.endingTimes = []
        
        if chiBackPointers != None and psiBackPointer != None:
            
            # infer from pointer matrix 
            totalTime, numStates = numpy.shape(chiBackPointers)
            finalTime = totalTime
            numdecodedStates = -1
            totalAllowedDevTime = (totalTime - TOTAL_ALLOWED_DEV_COEFF * totalTime)
            
            while numStates != numdecodedStates and finalTime > totalAllowedDevTime:
                finalTime = finalTime - 1
                logger.debug('backtracking from final time {}'.format(finalTime))

                self.pathRaw = self._backtrackForcedDur(chiBackPointers, psiBackPointer, finalTime)
                self._path2stateIndices()
                numdecodedStates = len(self.indicesStateStarts)
            if numStates != numdecodedStates:
                logger.debug(' backtracking NOT completed! stopped because reached totalAllowedDevTime  {}'.format(totalAllowedDevTime))
            
            
 
        
    
    def setPatRaw(self, pathRaw):
        self.pathRaw = pathRaw
        
    def _backtrackForcedDur(self, chiBackPointers, psiBackPointer, finalTime):
        '''
        starts at last state and assumes states increase by one
        '''
        length, numStates = numpy.shape(chiBackPointers)
        rawPath = numpy.empty( (length), dtype=int )
        # put last state till end of path
        if finalTime < length - 1:
            rawPath[finalTime+1:length] = numStates - 1

        
        # termination: start at end state
        t = finalTime
        currState = numStates - 1
        duration = chiBackPointers[t,currState]

        
        # path backtrakcing. allows to 0 to be starting state, but not to go below 0 state
        while (t>duration and currState > 0):
            if duration <= 0:
                print "Backtracking error: duration for state {} is {}. Should be > 0".format(currState, duration)
                sys.exit()
            
            rawPath[t-duration+1:t+1] = currState
            
            # for DEBUG: track durations: 
            self.durations.append(duration)
            self.endingTimes.append(t)

            
            ###### increment
            # pointer of coming state
            currState = psiBackPointer[t, currState]
            
            t = t - duration
            # sanity check. 
            if currState < 0:
                sys.exit("state {} at time {} < 0".format(currState,t))
            
            duration = chiBackPointers[t,currState]
        rawPath[0:t+1] = currState
        
        # DEBUG: add last t
        self.durations.append(t)
        self.endingTimes.append(t)
        
        self.durations.reverse() 
        self.endingTimes.reverse()    
   
        return rawPath
    
    def _path2stateIndices(self):
        '''
         indices in pathRaw where a new state starts. 
         the array index is the consequtive state count from sequence  
        '''
        self.indicesStateStarts = []
        currState = -1
        for i, p in enumerate(self.pathRaw):
            if not p == currState:
              self.indicesStateStarts.append(i)
              currState = p
              
              
    def printDurations(self):
        '''
        DEBUG: print durations
        ''' 
        print self.durations
    
             
        