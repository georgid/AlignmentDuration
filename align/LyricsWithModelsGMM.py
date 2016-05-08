'''
Created on May 7, 2016

@author: joro
'''
import sys
from align.ParametersAlgo import ParametersAlgo
from hmm.Parameters import MAX_SILENCE_DURATION
from align.Constants import NUM_FRAMES_PERSECOND
from align._LyricsWithModelsBase import _LyricsWithModelsBase
from jingju.sciKitGMM import SciKitGMM
import os
from utilsLyrics.Utilz import loadDictFromTabFile


currDir = os.path.abspath( os.path.join( os.path.dirname(os.path.realpath(__file__)) , os.path.pardir ) )
MODELS_SCRIPTS = currDir + '/models_jingju/'

class LyricsWithModelsGMM(_LyricsWithModelsBase):
    '''
    classdocs
    '''


    
    def _linkToModels(self, URIrecordingNoExt):
            '''
            load  trained models and link phoneme list to them    
            '''
                 
                #link each phoneme from transcript to a model
                # FIXME: DO A MORE OPTIMAL WAY like ismember()
            for phonemeFromTranscript in    self.phonemesNetwork:
                    self._renamePhonemeNames(phonemeFromTranscript)
                    
                    model, modelName = self._loadGMMModel(phonemeFromTranscript.ID, URIrecordingNoExt)
    #                 if model == None:
    
                    
                    sciKitGMM = SciKitGMM(model, modelName)
                    phonemeFromTranscript.setGMM(sciKitGMM)
                    phonemeFromTranscript.setNumStates(1)
                    
    
    
    def _loadGMMModel(self, modelName, URIRecordingNoExt ):
        ''' load model'''
        
#         thisDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__) ) )
        
        
        dictURI =  os.path.join(MODELS_SCRIPTS, 'modelName2FileNameDict') 
        modelName2FileNameDict = loadDictFromTabFile(dictURI)
        
        # table convert model names
        if modelName in modelName2FileNameDict:
            modelName = modelName2FileNameDict[modelName]
        
        path, fileName = os.path.split(URIRecordingNoExt)
        path, fold = os.path.split(path) # which Fold
#         fold = 'fold1'
        modelsURI =  os.path.join( ParametersAlgo.MODELS_DIR + fold + '/GMM/',  str(modelName) + '.pkl' )
        import pickle
        try:
            model = pickle.load(file(modelsURI))
        except BaseException:
            sys.exit("no model with URI {}. Make sure the correct fold is given".format(modelsURI))
            model = None
        return model, modelName
    
    
    
    def _renamePhonemeNames(self, phonemeFromTranscript):
            '''
            workaround. In trained models these models are missing so replace them with approximately closest ones 
            '''
            if phonemeFromTranscript.ID == 'N':
                phonemeFromTranscript.ID = 'n'
            if phonemeFromTranscript.ID == 'A':
                phonemeFromTranscript.ID = 'a'
            if phonemeFromTranscript.ID == 'U':
                phonemeFromTranscript.ID = 'u'
            if phonemeFromTranscript.ID == 'o':
                phonemeFromTranscript.ID = 'O'
            if phonemeFromTranscript.ID == 'U^':
                phonemeFromTranscript.ID = 'u'
            if phonemeFromTranscript.ID == '@':
                phonemeFromTranscript.ID = 'e'
            if phonemeFromTranscript.ID == '9':
                phonemeFromTranscript.ID = 'O'
       
    
    
    
    def _phonemes2stateNetwork(self):
        '''
        expand to self.statesNetwork . TAKE ONLY middle state for now
        @deprecated
        '''
        
        self.statesNetwork = []
        stateCount = 0
        
        for phoneme in self.phonemesNetwork:
            
            phoneme.setNumFirstState(stateCount)
            
            
             # update state counter
            if not hasattr(phoneme, 'sciKitGMM'):
                sys.exit("phoneme {} has no gmm assigned".format(phoneme.ID))
            stateCount += 1
            gmm = phoneme.sciKitGMM.gmm   
            idxMiddleState = 0
            
            
            if phoneme.ID != 'REST':
   
            
                if not phoneme.isVowelJingju(): # consonant
                    self.deviation = ParametersAlgo.CONSONANT_DURATION_DEVIATION
            
           
                currStateWithDur = self._createStateWithDur(phoneme, 1, idxMiddleState, None, 'normal', gmm)
                
                currStateWithDur.setDurationInFrames(phoneme.durationInNumFrames)
            
            else:
                
                currStateWithDur = self._createStateWithDur(phoneme, 1, idxMiddleState, None, 'exponential', gmm)
    
                currStateWithDur.setDurationInFrames( MAX_SILENCE_DURATION  * NUM_FRAMES_PERSECOND)
            
            self.statesNetwork.append(currStateWithDur)
        