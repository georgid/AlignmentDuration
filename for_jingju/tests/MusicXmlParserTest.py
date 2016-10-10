from MusicXmlParser import MusicXMLParser
import os
import sys

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

pathHMMDuration = os.path.join(parentDir, 'AlignmentDuration')
if pathHMMDuration not in sys.path:
    sys.path.append(pathHMMDuration)


from Phonetizer import Phonetizer


if __name__=='__main__':
    
    aria = 'dan-xipi_02' 
    aria = 'laosheng-xipi_02'
    aria = 'laosheng-erhuang_04'
    
    URI = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/' 
      
    MusicXmlURI = URI + aria + '_score.xml'
    lyricsTextGrid =  URI + aria + '.TextGrid'
    
#     MusicXmlURI = 'dan-xipi_01_score.xml'
#     lyricsTextGrid = 'dan-xipi_01.TextGrid'
    

    musicXMLParser = MusicXMLParser(MusicXmlURI, lyricsTextGrid)
    
    Phonetizer.initLookupTable(True,  'phonemeMandarin2METUphonemeLookupTableSYNTH')

    for i in range(len(musicXMLParser.listSentences)):
        print i, " ",  musicXMLParser.getLyricsForSection(i)
    
#     for syll in musicXMLParser.listSyllables:
#         print syll    
