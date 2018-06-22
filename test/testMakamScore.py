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
Created on Jan 13, 2016

@author: joro
'''
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../for_makam'))
from MakamScore import printMakamScore

from compmusic import dunya
        
dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")        
      

      
      
          
     

          
if __name__ == '__main__':
    
    if len(sys.argv) < 3:
      sys.exit('usage: {} <score_URI> <workMBID>'.format(sys.argv[0]))
    URI_dataset  = sys.argv[1]
    workMBID =  sys.argv[2]
    sectionMetadataDict = dunya.docserver.get_document_as_json(workMBID, "metadata", "metadata", 1, version="0.1")
    printMakamScore(URI_dataset, workMBID)  



          # compositionNames = [
          # 'nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi', 
          # 'nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin', 
          # 'ussak--sarki--aksak--bu_aksam_gun--tatyos_efendi', 
          # 'segah--sarki--curcuna--olmaz_ilac--haci_arif_bey', 
          # 'ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses', 
          # 'nihavent--sarki--aksak--gel_guzelim--faiz_kapanci', 
          # 'nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey', 
          # 'nihavent--sarki--aksak--koklasam_saclarini--artaki_candan', 
          # 'nihavent--sarki--kapali_curcuna--kimseye_etmem--kemani_sarkis_efendi', 
          # 'rast--turku--semai--gul_agaci--necip_mirkelamoglu', 
          # 'rast--sarki--sofyan--gelmez_oldu--dramali_hasan_hasguler', 
          # 'rast--sarki--curcuna--nihansin_dideden--haci_faik_bey']

