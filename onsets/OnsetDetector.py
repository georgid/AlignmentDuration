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
import sys
import csv

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.path.pardir)) 

pathPycomp = os.path.join(parentDir, 'pycompmusic')
if pathPycomp not in sys.path:
    sys.path.append(pathPycomp)


def writeCsv(fileURI, list_, withListOfRows=1):
    from csv import writer
    fout = open(fileURI, 'wb')
    w = writer(fout)
    print 'writing to csv file {}...'.format(fileURI)
    for row in list_:
        if withListOfRows:
            w.writerow(row)
        else:
            tuple_note = [row.onsetTime, row.noteDuration]
            w.writerow(tuple_note)
    
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


class VocalNote(object):
    def __init__(self,onsetTime, noteDuration):
        self.onsetTime = onsetTime
        self.noteDuration = noteDuration

class OnsetDetector(object):
    '''
    extract note onsets for one chunk
    '''

    def __init__(self, sectionLink):
        self.vocalNotes = []
        self.sectionLink = sectionLink

    def parseNoteOnsetsGrTruth(self, groundTruthNotesURI):
        
        '''
        from annotated notes for score-following for a segment from given 
        @param starttime to
        @param  endtime 
        '''
        startTime = self.sectionLink.beginTs
        endTime = self.sectionLink.endTs
        
        wholeRecordingVocalNotes = []
        from csv import reader
        with open(groundTruthNotesURI) as f:
            r = reader(f, delimiter='\t')
            for row in r:
                wholeRecordingVocalNotes.append(  VocalNote(float(row[0]), row[2] ) )
    
        
        ######## select part of onset times corresponding to segment
        i = 0
        while startTime > wholeRecordingVocalNotes[i].onsetTime:
            i+=1
            
        while i< len(wholeRecordingVocalNotes) and endTime >= wholeRecordingVocalNotes[i].onsetTime :
            self.vocalNotes.append(  VocalNote( wholeRecordingVocalNotes[i].onsetTime - startTime, wholeRecordingVocalNotes[i].noteDuration )  )
            i+=1
        
        if len(self.vocalNotes) == 0:
            sys.exit("in section from {} to {} there are no annotated onsets. No implemented".format(startTime, endTime))
        
        
        outFileURI = self.sectionLink.URIRecordingChunk + '.gr_truth.csv'
        writeCsv(outFileURI, self.vocalNotes, 0)
        return outFileURI
    
    def extractNoteOnsets(self, audioFileURI):
        '''
        with cante. 
        extract note onsets for whole audio
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
                durationDummy = 1
                self.vocalNotes.append(VocalNote(currTs, durationDummy))
        return onsetsURI
    
                
    def onsetTsToOnsetFrames(self,  lenObservations):
        
        noteOnsets = numpy.zeros((lenObservations,)) # init note onsets as all zeros: e.g. with normal transMatrices
        if self.vocalNotes != None:
        
            
            for vocalNote in self.vocalNotes:
                frameNum = tsToFrameNumber(vocalNote.onsetTime)
                if frameNum >= lenObservations or frameNum < 0:
                    logging.warning("onset has ts {} < first frame or > totalnumFrames {}".format(vocalNote.onsetTime, lenObservations))
                    continue
                onsetTolInFrames = ParametersAlgo.NUMFRAMESPERSECOND * ParametersAlgo.ONSET_TOLERANCE_WINDOW
                fromFrame = max(0, frameNum - onsetTolInFrames)
                toFrame = min(lenObservations, frameNum + onsetTolInFrames)
                noteOnsets[fromFrame:toFrame + 1] = 1  
        
        return noteOnsets  
    

def getDistFromOnset(noteOnsets, t):
        '''
        get distance in frames from time t to closest onset 
        '''
#        ##### DEBUG: 
#         for idx, onset in  enumerate(noteOnsets):
#             print idx, ": ", onset
        
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
  

def remove4thRow(annotationFileURI):
    '''
    convert from 4 rows annotation to 3 rows (without last textual one)
    used for annotations in turkish_makam_audio_score_alignment_dataset to prepare them for matlab evaluation script of Nadine
    '''

#     annotationFileURI = '/Users/joro/Documents/Phd/UPF/turkish_makam_audio_score_alignment_dataset/data/nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi/567b6a3c-0f08-42f8-b844-e9affdc9d215/alignedNotes.txt'
    with open(annotationFileURI, 'rb') as csvfile:
            score = csv.reader(csvfile, delimiter='\t')
            for idx, row in enumerate(score):
                
                print row[0] + '\t' + row[1] + '\t' + row[2] 

    
if __name__ == '__main__':
    
#     audioFileURI = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/HMMDuration/hmm/examples/KiseyeZeminPhoneLevel_2_zemin.wav'
    audioFileURI = '/Users/joro/Downloads/ISTANBULSymbTr2/567b6a3c-0f08-42f8-b844-e9affdc9d215/567b6a3c-0f08-42f8-b844-e9affdc9d215.wav'
    extractPitch(audioFileURI) 
     
    od = OnsetDetector() 
    od.extractNoteOnsets(audioFileURI)
    
#     noteOnsets = numpy.zeros((8,))
#     noteOnsets[2] = 1
#     noteOnsets[7] = 1
#     n = getDistFromOnset(noteOnsets, 7)
#     print n
