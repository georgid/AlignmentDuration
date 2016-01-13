'''
Created on Jan 13, 2016

@author: joro
'''
import sys
from MakamScore import loadMakamScore

def runMakamScore(argv):
        if len(argv) != 2:
            print ("usage: {} <path to symbtTr.txt and symbTr.sections.tsv>".format(argv[0]) )
            sys.exit();
        pathToComposition = argv[1]
        
        makamScore = loadMakamScore(pathToComposition)
        makamScore.printSectionsAndLyrics()
#         lyrics = loadLyrics(pathToComposition, whichSection=0)
     
      

def testMakamScore():
      a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/ussak--sarki--aksak--bu_aksam_gun--tatyos_efendi/']
      a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/rast--turku--semai--gul_agaci--necip_mirkelamoglu/']
      a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin/']
      a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/']
      a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/rast--sarki--curcuna--nihansin_dideden--haci_faik_bey/']
      a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/rast--sarki--sofyan--gelmez_oldu--dramali_hasan/']
    #         a = ['dummy', '/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/rast--turku--semai--gul_agaci--necip_mirkelamoglu/']
      a = ['dummy', '/Users/joro/Downloads/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/']
      
      compositionNames = [
          'nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi', 
          'nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin', 
          'ussak--sarki--aksak--bu_aksam_gun--tatyos_efendi', 
          'segah--sarki--curcuna--olmaz_ilac--haci_arif_bey', 
          'ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses', 
          'nihavent--sarki--aksak--gel_guzelim--faiz_kapanci', 
          'nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey', 
          'nihavent--sarki--aksak--koklasam_saclarini--artaki_candan', 
          'nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi', 
          'rast--turku--semai--gul_agaci--necip_mirkelamoglu', 
          'rast--sarki--sofyan--gelmez_oldu--dramali_hasan_hasguler', 
          'rast--sarki--curcuna--nihansin_dideden--haci_faik_bey']
      
      for compositionName in compositionNames:
          dirScoreURI = '/Users/joro/Downloads/turkish-makam-lyrics-2-audio-test-data-synthesis/' + compositionName + '/'
          a = ['dummy', dirScoreURI]
          runMakamScore(a)
          
if __name__ == '__main__':
    testMakamScore()  
