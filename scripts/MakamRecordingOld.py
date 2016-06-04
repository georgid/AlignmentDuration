# -*- coding: utf-8 -*-
'''
contains a Class 
Created on Mar 3, 2014

@author: joro
'''
from MakamScoreOld import MakamScoreOld
import subprocess
import os
from genericpath import isfile
import sys
from utilsLyrics.Utilz import loadTextFile, matchSections
import json
# from align.LyricsAligner import loadsectionTimeStampsLinksNew

pathToSox = "/usr/local/bin/sox"
    
class MakamRecordingOld:

    '''
    Logic to handle reading of audio section annotations, dividing into sections
    '''
    '''
    The size of self.sectionNames, self.beginTs, self.endTs, self.sectionIndices should be same
    
    '''

        
    def __init__(self, makamScore, pathToAudioFile, pathToLinkedSectionsFile):
       
       # the score of the piece
        self.makamScore = makamScore
        
        # wav file
        self.pathToAudiofile = pathToAudioFile
        self.pathToDividedAudioFiles= []
        
        
        # section timestamps,
        self.beginTs=[]
        self.endTs = []  
        
        # section names ordered as played in a recording
        self.sectionNamesSequence = []
        
        # indices to section numbers as in makamScore from sections.tsv file
        self.sectionIndices = []
        
        self._loadsectionTimeStamps( pathToLinkedSectionsFile)
#         self.sections = loadsectionTimeStampsLinksNew( pathToLinkedSectionsFile)  
        
        self.isChunkUsed  = []
        
        '''
        assigns a pointer (number) to each section Name from score
        '''
        
    
        return
    


        
        
       ##################################################################################
      
    ## loads timestamps from file .sectionAnno
    def _loadsectionTimeStamps(self, URISectionsAnnotationsFile):
        
        if not os.path.isfile(URISectionsAnnotationsFile):
                sys.exit("no file {}".format(URISectionsAnnotationsFile))
        
        ext = os.path.splitext(os.path.basename(URISectionsAnnotationsFile))[1] 
        if ext == '.txt' or ext=='.tsv':
            lines = loadTextFile(URISectionsAnnotationsFile)
            
            for line in lines:
                tokens =  line.split()
        
                         
                self.beginTs.append(float(tokens[0]))
                self.endTs.append(float(tokens[1]))
                self.sectionNamesSequence.append(tokens[2])
                
                # WORKAROUND for section mapping. read mapping index from 4th field in .annotations file
                # sanity check: 
#                 if len(tokens) == 4:
#                     self.sectionIndices.append(int(tokens[3]))
                    
                    #####################
        elif ext == '.json':
                
                b = open (URISectionsAnnotationsFile)
                sectionLinks = json.load(b)
                b.close()
                
                sectionAnnos = sectionLinks['annotations']
                for sectionAnno in sectionAnnos:
                    
                    beginTimeStr = str(sectionAnno['time'][0])
                    beginTimeStr = beginTimeStr.replace("[","")
                    beginTimeStr = beginTimeStr.replace("]","")
                    
                        
                    endTimeStr = str(sectionAnno['time'][1])
                    endTimeStr = endTimeStr.replace("[","")
                    endTimeStr = endTimeStr.replace("]","")
                    
                    
                    self.beginTs.append(float(beginTimeStr))
                    self.endTs.append(float(endTimeStr))
                    self.sectionNamesSequence.append( str(sectionAnno['name']) )
        else: 
            sys.exit("section annotation file {} has not know file extension.".format(URISectionsAnnotationsFile) )       
        
        # match automatically section names from sectionLinks to scoreSections 
        indices = []
        scoreSectionNamesSequence = []
        for s in self.makamScore.sectionToLyricsMap:
            scoreSectionNamesSequence.append(s[0])
        self.sectionIndices = matchSections(scoreSectionNamesSequence, self.sectionNamesSequence, indices) 
        
        if len(self.sectionIndices) != len(self.sectionNamesSequence):
            sys.exit("number of sections and number of matched sections not same!")
       

       ##################################################################################
  
        
        # for given audio and ts divide audio into audio segments
    def divideAudio(self):
            
            for i in range(len(self.sectionNamesSequence)):
                if self.sectionNamesSequence[i] == 'aranagme' or  self.sectionNamesSequence[i] == 'taksim' or \
                self.sectionNamesSequence[i] == 'gazel' or self.sectionNamesSequence[i] == 'unsure':
                    continue
                
                filePathAndExt = os.path.splitext(self.pathToAudiofile)
                currBeginTs = self.beginTs[i].replace(".",'_')
                
                
                currEndTs = currEndTs = self.endTs[i].replace(".",'_')
                filePathDividedAudio = filePathAndExt[0] + '_' + str(self.sectionIndices[i]) + '_' + self.sectionNamesSequence[i] + '_from_' + currBeginTs + '_to_' + currEndTs + filePathAndExt[1] 
                
                self.pathToDividedAudioFiles.append(filePathDividedAudio)
                # make sure  sox (sox.sourceforge.net) is installed and call it  here with subprocess
                sectionDuration = float(self.endTs[i])-float(self.beginTs[i])
                pipe = subprocess.Popen([pathToSox, self.pathToAudiofile, filePathDividedAudio, 'trim', self.beginTs[i], str(sectionDuration)   ])
                pipe.wait()
            return
        
        
    def divideAudioLinksNew(self):
            
            for section in self.sections:
                melStruct = section.melodicStructure.lower() 
                if melStruct == 'aranagme' or  section.melodicStructure == 'taksim' or \
                section.melodicStructure == 'gazel' or section.melodicStructure == 'unsure':
                    continue
                
                filePathAndExt = os.path.splitext(self.pathToAudiofile)
                currBeginTs = str(section.beginTs).replace(".",'_')
                    
                
                currEndTs = str(section.endTs).replace(".",'_')
                filePathDividedAudio = filePathAndExt[0] + '_' + section.melodicStructure + '_from_' + currBeginTs + '_to_' + currEndTs + filePathAndExt[1] 
                print "divided file " + filePathDividedAudio
                self.pathToDividedAudioFiles.append(filePathDividedAudio)
                # make sure  sox (sox.sourceforge.net) is installed and call it  here with subprocess
                sectionDuration = float(section.endTs)-float(section.beginTs)
                pipe = subprocess.Popen([pathToSox, self.pathToAudiofile, filePathDividedAudio, 'trim', str(section.beginTs), str(sectionDuration)   ])
                pipe.wait()
            return
        
        
    '''
    if given wav file does not exists, assumes same file with .mp3 ext exists and converts it to wav
    '''    
    def mp3ToWav(self):
           # todo: convert to mp3 if not with Essentia
        baseNameAudioFile = os.path.splitext(self.pathToAudiofile)[0]
        
        if not os.path.isfile(self.pathToAudiofile):
             pipe = subprocess.Popen(['/usr/local/bin/ffmpeg', '-i', baseNameAudioFile + '.mp3', self.pathToAudiofile])
             pipe.wait() 
    
    '''
    notUsed are chunks which will not be used in evaluation. 
    This used for now to exclude chunks where melodia has wrong pitch detection
    '''
    def markUsedChunks(self):
        
        self.isChunkUsed = [1] * len(self.pathToDividedAudioFiles)
        
        for index, pathToDividedAudioFile in enumerate(self.pathToDividedAudioFiles):
            if isfile( os.path.splitext(pathToDividedAudioFile)[0] +  ".notUsed"):
                self.isChunkUsed[index] = 0



      
def doit(argv):
        '''
        not finished. testing purpose 
        '''
        if len(argv) != 4  :
           sys.exit ("usage: {}  <recordingURI.wav> <sectionAnnoPath> <scorePath>".format(argv[0]) )
        recordingURI = argv[1]
        sectionAnnoPath = argv[2]
        scorePath = argv[3]
         
        makamRecording = MakamRecordingOld(makamScore, pathToAudioFile, pathToSectionAnnotations)

               
    
if __name__ == '__main__':
        # only for unit testing purposes
        print "in Makam Recording"
        doit(sys.argv)
 
        