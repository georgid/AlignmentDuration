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

