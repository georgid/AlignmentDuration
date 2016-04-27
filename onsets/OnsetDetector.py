'''
Created on Mar 4, 2016

@author: joro
'''
import os
import subprocess
import numpy
from align.ParametersAlgo import ParametersAlgo
import math
import logging




def writeCsv(fileURI, list_):
    from csv import writer
    fout = open(fileURI, 'wb')
    w = writer(fout)
    for row in list_:
        w.writerow(row)
    
    fout.close()

def extractPitch(audioFileURI):
    '''
    extract pitch using local version of pycompmusic and save as csv as input for Nadines algo
    '''
    
    print 'extracting pitch for {}...'.format(audioFileURI)
    from compmusic.extractors.makam import pitch
    extractor = pitch.PitchExtractMakam()
    results = extractor.run(audioFileURI)
    extractedPitchList = results['pitch']
    for i, row in enumerate(extractedPitchList):
        row = row[:-1]
        extractedPitchList[i]=row
    
    outFileURI = os.path.splitext(audioFileURI)[0] + '.pitch.csv'
    writeCsv(outFileURI, extractedPitchList)

class OnsetDetector(object):
    '''
    extract note onsets for one chunk
    '''

    def __init__(self):
        self. onsetTimestamps = []

    def parserNoteOnsetsGrTruth(self, groundTruthNotesURI, startTime, endTime):
        
        '''
        from annotated notes for score-following from  
        '''
        allRecordingOnsetTimestamps = []
        from csv import reader
        with open(groundTruthNotesURI) as f:
            r = reader(f, delimiter=' ')
            for row in r:
                allRecordingOnsetTimestamps.append(float(row[0]) )
    
        self.onsetTimestamps
        
        ######## select part of onset times corresponding to segment
        i = 0
        while startTime > allRecordingOnsetTimestamps[i]:
            i+=1
            
        while i< len(allRecordingOnsetTimestamps) and endTime >= allRecordingOnsetTimestamps[i] :
            self.onsetTimestamps.append(allRecordingOnsetTimestamps[i] - startTime) 
            i+=1
        
    
    
    def parserNoteOnsets(self, audioFileURI):
        '''
        with cante
        '''
        
        onsetsURI = os.path.splitext(audioFileURI)[0] + '.notes.csv'
        pitchURI = os.path.splitext(audioFileURI)[0] + '.pitch.csv'
        if not os.path.isfile(onsetsURI):
            if not os.path.isfile(pitchURI):
                extractPitch(audioFileURI)
            
            print 'extracting note onsets for {}...'.format(audioFileURI)
            cante = '/Users/joro/Downloads/cante-beta-csv/DerivedData/cante-static/Build/Products/Debug/cante-static'
            canteCommand = [cante, pitchURI, audioFileURI ]
            pipe= subprocess.Popen(canteCommand)
            pipe.wait()
            
            
        from csv import reader
        
        with open(onsetsURI) as f:
            r = reader(f)
            for row in r:
                currTs = float( "{0:.2f}".format(float(row[0].strip())) )
    #             currTs = round(float(row[0][0]),2)
                self.onsetTimestamps.append(currTs)
                
    def onsetTsToOnsetFrames(self,  lenObservations):
        
        noteOnsets = numpy.zeros((lenObservations,)) # init note onsets as all zeros: e.g. with normal transMatrices
        if self.onsetTimestamps != None:
        
            
            for onsetTimestamp in self.onsetTimestamps:
                frameNum = tsToFrameNumber(onsetTimestamp)
                if frameNum >= lenObservations or frameNum < 0:
                    logging.warning("onset has ts {} < first frame or > totalnumFrames {}".format(onsetTimestamp, lenObservations))
                    continue
                onsetTolInFrames = ParametersAlgo.NUMFRAMESPERSECOND * ParametersAlgo.ONSET_TOLERANCE_WINDOW
                fromFrame = max(0, frameNum - onsetTolInFrames)
                toFrame = min(lenObservations, frameNum + onsetTolInFrames)
                noteOnsets[fromFrame:toFrame + 1] = 1  
        
        return noteOnsets  
    

def getDistFromOnset(noteOnsets, t):
        '''
        get distance in frames from time to closest onset 
        '''
        
        #### find closest onset 
        n = 0
        rightIdx = t
        leftIdx = t
        while  noteOnsets[rightIdx] == 0 and  noteOnsets[leftIdx] == 0:
            n += 1
            rightIdx =  min(t + n, noteOnsets.shape[0]-1)
            leftIdx = max(t - n, 0) 
        
        return n

def tsToFrameNumber(ts):
    '''
    get which frame is for a given ts, according to htk's feature extraction  
    '''
    return   int(math.floor( (ts - ParametersAlgo.WINDOW_SIZE/2.0) * ParametersAlgo.NUMFRAMESPERSECOND))
 
 
def frameNumberToTs(frameNum):
    '''
    get which ts is for a given frame, according to htk's feature extraction  
    '''
    return float(frameNum) /    float(ParametersAlgo.NUMFRAMESPERSECOND) + ParametersAlgo.WINDOW_SIZE/2.0
  

    
if __name__ == '__main__':
    
#     audioFileURI = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/HMMDuration/hmm/examples/KiseyeZeminPhoneLevel_2_zemin.wav'
#     extractPitch(audioFileURI) 
#     
#     od = OnsetDetector() 
#     od.parserNoteOnsets(audioFileURI)
    
    noteOnsets = numpy.zeros((8,))
    noteOnsets[2] = 1
    noteOnsets[7] = 1
    n = getDistFromOnset(noteOnsets, 7)
    print n
