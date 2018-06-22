# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/



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