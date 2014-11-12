'''
Created on Oct 27, 2014

@author: joro
'''
import os
import sys
from Utilz import writeListOfListToTextFile, writeListToTextFile
from hmm.Path import Path
from Syllable import MINIMAL_DURATION_UNIT
from hmm.continuous.DurationPdf import MINIMAL_PROB


parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir)) 

pathUtils = os.path.join(parentDir, 'utilsLyrics')
sys.path.append(pathUtils )

htkModelParser = os.path.join(parentDir, 'htk2s3')
sys.path.append(htkModelParser)

# pathHMM = os.path.join(parentDir, 'HMM')
pathHMM = os.path.join(parentDir, 'HMMDuration')
sys.path.append(pathHMM)



from hmm.continuous.GMHMM  import GMHMM

import numpy

# TODO: read from models
numMixtures = 9
numDimensions = 25

# TODO: read from feat extraction parameters
NUM_FRAMES_PERSECOND = 100.0

#DEBUG: 
PATH_CHI = '/Users/joro/Downloads/chi'
PATH_PSI = '/Users/joro/Downloads/psi'

class Decoder(object):
    '''
    holds structures used in decoding and decoding result
    '''


    def __init__(self, lyricsWithModels, numStates=None, withModels=True):
        '''
        Constructor
        '''
        self.lyricsWithModels = lyricsWithModels
        
        '''
        of class HMM
        '''
        self.hmmNetwork = []
                

        self._constructHmmNetwork(numStates, withModels)
        
        # Path class object
        self.path = None
        
    def _constructHmmNetwork(self,  numStates, withModels ):
        '''
        Tests the guyz hmm viterbi with one word. 
        '''
        
    #     sequencePhonemes = sequencePhonemes[0:4]
        
        
        ######## construct transition matrix
        #######
        
#         transMAtrix = self._constructTransMatrixHMMNetwork(self.lyricsWithModels.phonemesNetwork)
#        DEBUG
#  writeListOfListToTextFile(transMAtrix, None , '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentStep/transMatrix')
        
        # construct means, covars, and all the rest params
        #########
       
        if numStates == None:
            numStates = len(self.lyricsWithModels.statesNetwork) 
        
        means, covars, weights, pi = self._constructHMMNetworkParameters(numStates,  withModels)
        
        self.hmmNetwork = GMHMM(numStates,numMixtures,numDimensions,None,means,covars,weights,pi,init_type='user',verbose=True)
        

        
    def  _constructTransMatrixHMMNetwork(self, sequencePhonemes):
        
        # just for initialization totalNumPhonemes
        totalNumStates = 0
        for phoneme in sequencePhonemes:
            currNumStates = phoneme.htkModel.tmat.numStates - 2
            totalNumStates += currNumStates
            
        transMAtrix = numpy.zeros((totalNumStates, totalNumStates), dtype=numpy.double)
        
        
        counterOverallStateNum = 0 
        
        for phoneme in sequencePhonemes:
            currNumStates =   phoneme.htkModel.tmat.numStates - 2
            
            vector_ = phoneme.htkModel.tmat.vector
            currTransMat = numpy.reshape(vector_ ,(len(vector_ )**0.5, len(vector_ )**0.5))
            
    #         disregard 1st and last states from transMat because they are the non-emitting states
       
            transMAtrix[counterOverallStateNum : counterOverallStateNum + currNumStates, counterOverallStateNum : counterOverallStateNum + currNumStates ] = currTransMat[1:-1,1:-1]
           
            # transition probability to next state
            #         TODO: here multiply by [0,1] matrix next state. check if it exists
            nextStateTransition = 1
            
            if (counterOverallStateNum + currNumStates) < transMAtrix.shape[1]:
                val = currTransMat[-2,-1] * nextStateTransition
                transMAtrix[counterOverallStateNum + currNumStates -1, counterOverallStateNum + currNumStates] =  val
    
    
            # increment in final trans matrix  
            counterOverallStateNum +=currNumStates
            
            
        return transMAtrix
    
    def _constructHMMNetworkParameters(self,  numStates,  withModels=True, sequenceStates=None):
        '''
        tranform h2s hmm model to  format of gyuz's hmm class
        '''
        
       
        
        means = numpy.empty((numStates, numMixtures, numDimensions))
        
        # init covars
        covars = [[ numpy.matrix(numpy.eye(numDimensions,numDimensions)) for j in xrange(numMixtures)] for i in xrange(numStates)]
        
        weights = numpy.ones((numStates,numMixtures),dtype=numpy.double)
        
        # start probs : allow to start only at first state
        pi = numpy.zeros((numStates), dtype=numpy.double)
        # avoid log(0) 
        pi.fill(MINIMAL_PROB)
        pi[0] = 1
        
#         pi = numpy.ones( (numStates)) *(1.0/numStates)
        
        if not withModels:
            return None, None, None, pi

        
        sequenceStates = self.lyricsWithModels.statesNetwork
         
        if sequenceStates==None:
            sys.exit('no state sequence')
               
        for i in range(len(sequenceStates) ):
            state  = sequenceStates[i] 
            
            for (numMixture, weight, mixture) in state.mixtures:
                
                weights[i,numMixture-1] = weight
                
                means[i,numMixture-1,:] = mixture.mean.vector
                
                variance_ = mixture.var.vector
                for k in  range(len( variance_) ):
                    covars[i][numMixture-1][k,k] = variance_[k]
        return means, covars, weights, pi
    
            
      
        
        
    def duration2numFrameDuration(self, observationFeatures):
        '''
        helper method. 
        setDuration HowManyFrames for each state in hmm
        '''
        # TODO: read from score
#         self.bpm = 60
#         durationMinUnit = (1. / (self.bpm/60) ) * (1. / MINIMAL_DURATION_UNIT) 
#         numFramesPerMinUnit = NUM_FRAMES_PERSECOND * durationMinUnit
        totalDur = self.lyricsWithModels.getTotalDuration()
        numFramesPerMinUnit   = float(len(observationFeatures)) / float(totalDur)
        numFramesDurationsList = []
        
        for  i, stateWithDur_ in enumerate (self.lyricsWithModels.statesNetwork):
            # numFrames per phoneme
            numFramesPerState = round(float(stateWithDur_.duration) * numFramesPerMinUnit)
            numFramesDurationsList.append(numFramesPerState)
            stateWithDur_.setDurationInFrames(numFramesPerState)
            
        return numFramesDurationsList
        
        


        
    
    def decodeAudio( self, observationFeatures):
        ''' decode path for given exatrcted features for audio
        '''
        # TODO: double check that features are in same dimension as model
#         observationFeatures = observationFeatures[0:100,:]
        
        listDurations = self.duration2numFrameDuration(observationFeatures)
        
        self.hmmNetwork.setDurForStates(listDurations) 
        
#         self.path, psi, delta = self.hmmNetwork._viterbiForced(observationFeatures)
#         if os.path.exists(PATH_CHI) and os.path.exists(PATH_PSI): 
#             chiBackPointer = numpy.loadtxt(PATH_CHI)
#             psiBackPointer = numpy.loadtxt(PATH_PSI)
#                
#         else:
        chiBackPointer, psiBackPointer = self.hmmNetwork._viterbiForcedDur(observationFeatures)
    
        writeListOfListToTextFile(chiBackPointer, None , PATH_CHI)
        writeListOfListToTextFile(psiBackPointer, None , PATH_PSI)
            
        
        self.path =  Path(chiBackPointer, psiBackPointer)
        
         # DEBUG
#         self.path.printDurations()
        writeListToTextFile(self.path.pathRaw, None , '/tmp/path')
        
    
  
    

    def path2ResultWordList(self):
        '''
        makes sense of path indices : maps numbers to states and phonemes, uses self.lyricsWithModels.statesNetwork and lyricsWithModels.listWords) 
        to be called after decoding
        '''
        # indices in pathRaw
        self.path._path2stateIndices()
        
        #sanity check
        numStates = len(self.lyricsWithModels.statesNetwork)
        numdecodedStates = len(self.path.indicesStateStarts)
        
        if numStates != numdecodedStates:
            sys.exit("detected path has {} states, but stateNetwork transcript has {} states".format( numdecodedStates, numStates ) )
        
        detectedWordList = []
        
        for word_ in self.lyricsWithModels.listWords:
            countFirstState = word_.syllables[0].phonemes[0].numFirstState

            lastPhoneme = word_.syllables[-1].phonemes[-1]
            if lastPhoneme.ID != 'sp':
                sys.exit('In Decode. \n last state for word {} is not sp. Sorry - not implemented.'.format(word_.text))
            
            countLastState = lastPhoneme.numFirstState

            detectedWord = self._constructTimeStampsForWord( word_, countFirstState, countLastState)
           
            detectedWordList.append( detectedWord)
        return detectedWordList
    
    
    def _constructTimeStampsForWord(self,  word_, countFirstState, countLastState):
        currWordBeginFrame = self.path.indicesStateStarts[countFirstState]
        currWordEndFrame = self.path.indicesStateStarts[countLastState]
    #             # debug:
    #             print self.pathRaw[currWordBeginFrame]
    # timestamp:
        startTs = float(currWordBeginFrame) / NUM_FRAMES_PERSECOND
        endTs = float(currWordEndFrame) / NUM_FRAMES_PERSECOND
        
        detectedWord = startTs, endTs, word_.text
        print detectedWord
        
        return detectedWord
    
             
        