'''
Created on Jan 13, 2016

@author: joro
'''
import os
from align.LyricsAlign import alignRecording

def testLyricsAlign():
    
    currDir = os.path.abspath(os.path.dirname(os.path.realpath(__file__)) )

    symbtrtxtURI = os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci.txt')
    sectionMetadataURI =  os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci.sectionsMetadata.json' )
    sectionLinksURI =   os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya.sectionLinks.json' )
    audioFileURI =  os.path.join( currDir, '../example/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya/18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya.wav')
    outputDir =  os.path.join( currDir, '../example/output/' )
    
    totalDetectedTokenList = alignRecording(symbtrtxtURI, sectionMetadataURI, sectionLinksURI, audioFileURI, outputDir)
    ret = {'alignedLyricsSyllables':{} }
    ret['alignedLyricsSyllables'] =   totalDetectedTokenList
    print ret


if __name__ == '__main__':
    testLyricsAlign()