'''
Created on Oct 31, 2014

@author: joro
'''
import numpy
import os
import sys
import math

from numpy.core.numeric import Infinity

from _ContinuousHMM import _ContinuousHMM
from hmm.continuous.DurationPdf  import DurationPdf, NUMFRAMESPERSEC

from hmm.continuous.ExpDurationPdf import ExpDurationPdf

import essentia.standard
import logging
from hmm.continuous._HMM import _HMM

# to replace 0: avoid log(0) = -inf. -Inf + p(d) makes useless the effect of  p(d)
MINIMAL_PROB = sys.float_info.min



from utilsLyrics.Utilz import writeListOfListToTextFile, writeListToTextFile

# put intermediate output in examples dir
PATH_LOGS= os.path.dirname(os.path.realpath(sys.argv[0]))
# print 'PATH_LOGS is '  + PATH_LOGS



ALPHA =  0.99
# OVER_MAX_DUR_FACTOR = 1.3



class _DurationHMM(_HMM):
    '''
    Implements the decoding with duration probabilities, but should not be used directly.
    '''
    
    def __init__(self,statesNetwork, numMixtures, NUM_DIMENSIONS):
    
#     def __init__(self,n,m,d=1,A=None,means=None,covars=None,w=None,pi=None,min_std=0.01,init_type='uniform',precision=numpy.double, verbose=False):
            '''
            See _ContinuousHMM constructor for more information
            '''
            _HMM.__init__(self, statesNetwork, numMixtures, NUM_DIMENSIONS, transMatrix=None, transMatrixOnsets=None)
            
            self.setDurForStates(listDurations=[])
            
            self.ALPHA = ALPHA # could be redefined by setAlpha() method

                
    def setALPHA(self, ALPHA):
        # DURATION_WEIGHT 
        self.ALPHA = ALPHA
    

    
    def setDurForStates(self, listDurations):
        '''
        mapping of state to its duration (in number of frames).
        @param listDurations read from  state.Durations
        
        '''
        if listDurations == []:
            for  stateWithDur_ in self.statesNetwork:
                listDurations.append(stateWithDur_.getDurationInFrames())
                
        # sanity check  
        if len(listDurations) != self.n:
            sys.exit("#Durations from list = {}, whereas #states={}".format(len(listDurations), self.n ))

        self.durationMap =  numpy.array(listDurations, dtype=int)
        # DEBUG: 
        writeListToTextFile(self.durationMap, None , PATH_LOGS + '/durationMap') 

#         STUB
#         self.durationMap =  numpy.arange(1,self.n+1)
       
#         self.durationPdf = DurationPdf(self.R_MAX, self.usePersistentFiles)
        self.R_MAX = 0
        for  stateWithDur_ in self.statesNetwork:
            if stateWithDur_.getMaxRefDur() > self.R_MAX:
                self.R_MAX  = stateWithDur_.getMaxRefDur()
        self.R_MAX = int(self.R_MAX)
        self.logger.info("R_MAX={}".format(self.R_MAX))
            
#         self.R_MAX = int( self.durationPdf.getMaxRefDur(numpy.amax(self.durationMap) ) )
    
   
    def getWaitLogLikOneDur(self, d, whichState):
        '''
        return waiting pdf. cases for distribution
        '''  
        stateWithDuration = self.statesNetwork[whichState]
        
        # expo distrib
        if stateWithDuration.distributionType=='exponential':
            return stateWithDuration.durationDistribution.getWaitLogLik(d)
        
        # normal distrib
        scoreDurCurrState = self.durationMap[whichState]
        return stateWithDuration.durationDistribution.getWaitLogLik(d+1, scoreDurCurrState)
     

            
            
            
    
    def _viterbiForcedDur(self):
        # sanity check. make sure durations are init from score
      
        lenObs = numpy.shape(self.B_map)[1]
        print "decoding..."
        for t in range(self.R_MAX,lenObs):                          
            for currState in xrange(1, self.n):
                maxPhi, fromState, maxDurIndex = self._calcCurrStatePhi(t, currState) # get max duration quantities
                self.phi[t][currState] = maxPhi
        
                self.psi[t][currState] = fromState
        
                self.chi[t][currState] = maxDurIndex
        
        
        numpy.savetxt(PATH_LOGS + '/phi', self.phi)
           
        numpy.savetxt(PATH_LOGS + '/chi', self.chi)
        numpy.savetxt(PATH_LOGS + '/psi', self.psi)

        # return for backtracking
        return  self.chi, self.psi
    
    
    

    
    def initDecodingParameters(self,  observationsORLyricsWithModels,  onsetTimestamps, fromTs, toTs):
        '''
        helper method to init all params
        '''    
        
        lenObservations = super(_DurationHMM,self).initDecodingParameters( observationsORLyricsWithModels,  onsetTimestamps, fromTs, toTs)
        
        # backpointer: how much duration waited in curr state
        self.chi = numpy.empty((lenObservations, self.n), dtype=self.precision)
        self.chi.fill(-1)
        
        # init. t< R_MAX
        if (self.R_MAX >= lenObservations):
            sys.exit("MAX_Dur {} of a state is more than total number of observations {}. Unable to decode".format(self.R_MAX, lenObservations))
        self._initBeginingPhis(lenObservations)
    
    
    def _calcCurrStatePhi(self,  t, currState):
        '''
        calc. quantities in recursion  equation
        '''
        self.logger.debug("at time t={}".format(t) )          
        
        stateWithDuration = self.statesNetwork[currState]
        minDur = stateWithDuration.getMinRefDur()
        endDur = stateWithDuration.getMaxRefDur()
        

        if t <= minDur: # min duration is before beginning of audio. used in init         # never happens for t>self.R_MAX
            return -Infinity, -1, -1
        
        endDur = min(t, endDur)         # reducedMaxDur. never happens for t>self.R_MAX

        
#         maxPhi, fromState,  maxDurIndexSlow =  self.getMaxPhi_slow(t, currState, minDur, endDur)
        
        maxPhi, fromState,  maxDurIndex =  self.getPhiOptimal(t, currState, minDur, endDur)
        
#         if not maxDurIndex == maxDurIndexSlow:
#             print "{} and {} not SAME".format(maxDurIndex, maxDurIndexSlow)
#                
                
        return maxPhi, fromState, maxDurIndex 
                
           
    def computePhiStar(self, t, currState):
        '''
        boundaries check for minDur and endDur makes PhiStar different from phi 
        '''
        
        fromState =-1
        maxDurIndex = -1
        
        currStateWithDur = self.statesNetwork[currState]
        ####### boundaries check
        minDur = currStateWithDur.getMinRefDur()
        if t <= minDur: # min duration is before beginning of audio 
            phiStar = -Infinity
        else:
            currReducedMaxDur = min(t, currStateWithDur.getMaxRefDur())
#             phiStar, fromState, maxDurIndex = self.getMaxPhi_slow(t, currState, minDur, currReducedMaxDur)
            phiStar, fromState,  maxDurIndex =  self.getPhiOptimal(t, currState, minDur, currReducedMaxDur)

        return phiStar, fromState, maxDurIndex
        
 
    
    def getPhiOptimal(self,t,currState,minDur,maxDur):
        '''
        with numpy vector computation
        '''
        
        fromState = currState - 1
        maxPhi = -1 * numpy.Infinity 
        maxDurIndex = -1
         
         # 1) add +1 to make it start from t-minDur 
        phisFrom = self.phi[t-maxDur+1:t-minDur+1,fromState]
        reducedLengthDurationInterval =  len(phisFrom) # lets decode for this range of duration 
        
        # 2) wait logs
        stateWithDuration = self.statesNetwork[currState]
        
        
        if stateWithDuration.distributionType=='exponential':
             waitLogLiks = numpy.zeros(phisFrom.shape)
             for d in range (minDur, maxDur):
                 # TODO: write a function that pre-computes the list of probs p_i(d). instead of redundantly computing it for each p_i(d)    
                 waitLogLiks[d-minDur] = stateWithDuration.durationDistribution.getWaitLogLik(d)
                 
        else: # normal distribution
            offset =  len(stateWithDuration.durationDistribution.liks) - reducedLengthDurationInterval
            waitLogLiks = stateWithDuration.durationDistribution.liks[offset:,0]
            waitLogLiks = waitLogLiks.T
        
        waitLogLiks  = waitLogLiks[::-1]
        
#         3) sumObsProb 
        b_map_slice = self.B_map[currState, t-maxDur+2:t-minDur+2] # first slice
        b_map_slice = b_map_slice[::-1] # get initial slice
        sumObsProb = numpy.zeros(b_map_slice.shape)
        
        #### add incrementally obs probs to initial slice
        tmp = 0
        for i in range(reducedLengthDurationInterval):
            tmp += b_map_slice[i]  
            sumObsProb[i]=tmp
        sumObsProb = sumObsProb[::-1]
        
        # sum and get max
        phis = phisFrom + self.ALPHA * waitLogLiks + (1-self.ALPHA) * sumObsProb 

        self.logger.debug("  VECTRO: state = {}, time = {}".format( currState, t )) 
        
        
#         print  "\t\t phis= {}".format (phis)  
#         print  "\t\t waitLogLik= {}".format (waitLogLiks) 
#         print "\t\t sumObsProb= {}".format( sumObsProb) 

        
        maxPhi = numpy.max(phis)
        maxDurIndex = maxDur - numpy.argmax(phis) - 1
        
        # add remaining part from sum ObsProb form d = 1:minDur
        b_map_slice = self.B_map[currState, t-minDur+2:t+1]
        maxPhi += (1-self.ALPHA) * numpy.sum(b_map_slice)
        
        return maxPhi, fromState,  maxDurIndex  

  
        
        
    def getMaxPhi_slow(self, t, currState, minDur, endDur):
        '''
        @deprecated
        recursive rule. Find duration that maximizes current phi
        @return: maxPhi - pprob
        @return: fromState - from which state we come (hard coded to prev. state in forced alignment) 
        @return: maxDurIndex - index Duration with max prob. INdex for t begins at 0
        
        used in _initBeginingPhis
        used in _calcCurrStatePhi
        '''
        sumObsProb = 0
         # (hard coded to prev. state in forced alignment)
        fromState = currState - 1
        maxPhi = -1 * numpy.Infinity 
        maxDurIndex = -1
        
#         print "in getMaxPhi_slow: maxDuration =",  currRefDur
    
        for d in range(int(minDur), int(endDur)):

            currPhi = self.phi[t-d][fromState]
            whichTime =  t-d+1
            updateQuantity, sumObsProb = self._calcUpdateQuantity(whichTime, d, currState, currPhi, sumObsProb)

            #sanity check. The '=' sign is when both are infty, take d as index
            if updateQuantity >= maxPhi:
                maxPhi = updateQuantity
                maxDurIndex = d
        
        if maxDurIndex == -1:
            sys.exit(" no max duration at time {} and state {}".format(t, currState))
        
        # add remaining part from sum ObsProb form d = 1:minDur
        b_map_slice = self.B_map[currState, t-minDur+2:t+1]
        maxPhi += (1-self.ALPHA) * numpy.sum(b_map_slice)
        
        return maxPhi, fromState, maxDurIndex    
    
    
    def _calcUpdateQuantity(self, whichTime, whichDuration, currState, currPhi, sumObsProb):
        '''
        @param whichTime: needed to take the corresponding b_i(O_t)
        calc update quantity.
        used in getMaxPhi_slow
        used in init kappas
        '''
        
        self.logger.debug( " d= {} time = {}, state = {}".format(whichDuration, whichTime, currState ) )

#             print "\t\t prevPhi= {}".format(currPhi)  
        
        old_settings = numpy.seterr( under='raise')
        
        waitLogLik = self.getWaitLogLikOneDur(whichDuration, currState)
#         print  "\t\t waitLogLik= {}".format (waitLogLik) 
            
        sumObsProb += self.B_map[currState, whichTime]
#         print "\t\t sumObsProb= {}".format( sumObsProb)      
        
        updateQuantity = currPhi + self.ALPHA * waitLogLik + (1-self.ALPHA)*sumObsProb
#         updateQuantity = currPhi +  waitLogLik + sumObsProb
        self.logger.debug( "\t UPDATE QUANT= {}".format(updateQuantity)  )


        return updateQuantity, sumObsProb

 
 

    

    def _initBeginingPhis(self, lenObservations):
        '''
        init phis when t < self.R_MAX
        '''
        
        self._initKappas(lenObservations)
        
        print "init beginning phis"
         # for convenience put as class vars
#         self.phi = numpy.empty((lenObservations,self.n),dtype=self.precision)
#         self.phi.fill(-Infinity)
        
        
        # init t=0
#         for currState in range(self.n): self.phi[0,currState] = self.kappas[currState,0]
        self.phi[0,:] = self.kappas[0,:]
        
        # init first state = kappa (done to allow self.getMaxPhi_slow  to access prev. currState)
        self.phi[:len(self.kappas[:,0]),0] = self.kappas[:,0]        
        
      
        # select bigger (kappa and phi_star)
        for currState in range(1, self.n): 
            # phi star makes sence only from second state 
            for t in  range(1,int(self.R_MAX)):
                
#                 phiStar, fromState, maxDurIndex = self._calcCurrStatePhi(t, currState)
                phiStar, fromState, maxDurIndex = self.computePhiStar(t, currState)

                currKappa = self.kappas[t,currState]
                
               
#                 if phiStar == -Infinity and currKappa == -Infinity and currState != 1 and currState != 2 and currState != 3:  # sanity check
#                     # kappas are -inf for t > currState.maxRefDur. phis is -inf only at state=1, becuase currState-1 is initialized with kappas, which can be -inf 
#                     self.logger.warning("both phiStar and kappa are infinity for time {} and state {}".format( t, currState))
#                     sys.exit()
                    
                # take bigger : eq:deltaStarOrKappa
                if  phiStar >= currKappa:
                    self.phi[t,currState] = phiStar
                    self.psi[t,currState] = fromState 
                    self.chi[t,currState] = maxDurIndex
#                     self.debug.info("time = {} currState = {}".format(t, currState) )  
                else: # kappa is bigger
                    
                    maxRefDur = self.statesNetwork[currState].getMaxRefDur()
                    self.logger.debug( " kappa {} more than phi {} at time {} and state {}\n maxRefDur is {}".format(currKappa, phiStar, t, currState, maxRefDur))                        
                    
                    if t > maxRefDur:  # sanity check
                        self.logger.warning(" non-real kappa at time {} and state {}".format( t, currState))
                        sys.exit()
                    self.phi[t, currState] = currKappa
                    # kappas mean still at beginning state
                    self.psi[t,currState] = currState
                    self.chi[t,currState] = t
                    
        
        writeListOfListToTextFile(self.phi, None , PATH_LOGS + '/phi_init_1') 
    

        
    def _initKappas(self, lenObservations):
        '''
        kappas[t][s] - starting and staying at time t in same currState s.
        WITH LogLik 
        '''
        if lenObservations <= self.R_MAX:
            sys.exit("observations are only {}, R_max = {}. not able to run initialization. Increase size of observations".format(lenObservations,self.R_MAX)) 
        
        print 'init kappas...'
        self.kappas = numpy.empty((self.R_MAX,self.n), dtype=self.precision)
        # kappa[t, state] = -INFINITY allows phi to be selcted instead of kappa. we forbid this kappa. 
        self.kappas.fill(-numpy.Infinity)
        
        for currState in range(self.n):
            sumObsProb = 0
            currStateWithDur  = self.statesNetwork[currState]
            currRefMax = currStateWithDur.getMaxRefDur()
            currLogPi = numpy.log(self.pi[currState])
            
            # start from 1 because t is in the role of duration
            for t in range(1, int(currRefMax)+1):
                whichtime = t-1
                whichDuration = t
                updateQuantity, sumObsProb = self._calcUpdateQuantity(whichtime, whichDuration, currState, 0, sumObsProb)
                
                self.kappas[whichtime,currState] = currLogPi + updateQuantity
                
                
                
        writeListOfListToTextFile(self.kappas, None , PATH_LOGS + '/kappas') 
       
