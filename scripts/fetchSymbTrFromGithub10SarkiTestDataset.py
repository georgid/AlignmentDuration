'''
Created on Jan 15, 2016

fetch symbTr and sectionsMaetadata for a given list of symbTrNames.

List of compositins taken from 
https://drive.google.com/file/d/0B4bIMgQlCAuqY3hKc25WTm9kTEk/view

'''


import urllib2
import urllib
    
def fetchFileFromURL(URL, outputFileURI):
        response = urllib2.urlopen(URL)
        a = response.read()
        with open(outputFileURI,'w') as f:
            f.write(a) 

def doit():    
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
                        'rast--sarki--curcuna--nihansin_dideden--haci_faik_bey'
                        
                    
                    ]
        
        for compositionName in compositionNames:
            webSiteSymbTr = 'https://raw.githubusercontent.com/MTG/SymbTr/master/txt/' + compositionName + '.txt'
            fileURISymbTr = '/Users/joro/Downloads/turkish-for_makam-lyrics-2-audio-test-data-synthesis/' + compositionName + '/' + compositionName + '.txt'
    
            print webSiteSymbTr
            
            webSiteSectionsMetadata = 'https://raw.githubusercontent.com/sertansenturk/turkish_makam_corpus_stats/master/data/SymbTrData/' + compositionName + '.json' 
            print webSiteSectionsMetadata
            fileURISectionsMetadata = '/Users/joro/Downloads/turkish-for_makam-lyrics-2-audio-test-data-synthesis/' + compositionName + '/' + compositionName + '.sectionsMetadata.json'
    
            
            try:
    #             fetchFileFromGithub(webSiteSymbTr, fileURISymbTr)
                fetchFileFromGithub(webSiteSectionsMetadata, fileURISectionsMetadata)
                
            except urllib2.URLError as e:
                print e.reason
                continue


if __name__ == '__main__':
    doit()