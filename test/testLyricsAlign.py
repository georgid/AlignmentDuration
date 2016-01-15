'''
Created on Jan 13, 2016

@author: joro
'''
import os
from align.LyricsAlign import alignRecording

def testLyricsAlign():
    
    
    symbtrtxtURI = '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci.txt'
    sectionMetadataURI = '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci.sectionsMetadata.json'
    sectionLinksURI = '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya.sectionLinks.json'
    audioFileURI = '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya.wav'
    outputDir = '../example/output/'
    
    totalDetectedTokenList = alignRecording(symbtrtxtURI, sectionMetadataURI, sectionLinksURI, audioFileURI, outputDir)
    ret = {'alignedLyricsSyllables':{} }
    ret['alignedLyricsSyllables'] =   totalDetectedTokenList
    print ret


if __name__ == '__main__':
    testLyricsAlign()