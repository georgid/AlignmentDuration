'''
Created on Feb 3, 2016

@author: joro
'''

import sys
import os
import urllib2
import json
import logging
import subprocess

### include src folder
parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir, os.pardir))
if parentDir not in sys.path:
    sys.path.append(parentDir)

# if '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/pycompmusic/' not in sys.path:
#     sys.path.append('/Users/joro/Documents/Phd/UPF/voxforge/myScripts/pycompmusic/')

# make sure pycompmusic is installed with setup.py install
    
import compmusic.extractors
# from docserver import util
from compmusic import dunya
from compmusic.dunya import makam
import tempfile


from compmusic.extractors.makam.fetch_tools import getWork, fetchNoteOnsetFile,\
    get_section_annotaions_dict, downloadSymbTr, fetch_audio_wav

from src.align.LyricsAligner  import LyricsAligner, stereoToMono, loadMakamRecording
from src.align.ParametersAlgo import ParametersAlgo

# if on server:
# ParametersAlgo.FOR_MAKAM = 1
# ParametersAlgo.POLYPHONIC = 1
# ParametersAlgo.WITH_DURATIONS = 1
# ParametersAlgo.DETECTION_TOKEN_LEVEL= 'syllables'

# if for ISMIR 2016 paper note onsets:
ParametersAlgo.WITH_DURATIONS = 0
ParametersAlgo.FOR_MAKAM = 1
ParametersAlgo.POLYPHONIC = 0
ParametersAlgo.DETECTION_TOKEN_LEVEL= 'words'
# ParametersAlgo.DETECTION_TOKEN_LEVEL= 'syllables'
# ParametersAlgo.DETECTION_TOKEN_LEVEL= 'phonemes' 

ParametersAlgo.WITH_ORACLE_ONSETS = -1

if ParametersAlgo.POLYPHONIC:
    dataDir = '/Users/joro/Documents/lyrics-2-audio-test-data/'
#     sys.exit('path to audio not given')
else:
#     dataDir = '/home/georgid/Documents/makam_acapella/'
    dataDir = '/Users/joro/Documents/ISTANBULSymbTr2'

# triple: (acappella name, hasSecondVerse, hasSectionNumberDiscrepancy)

# these 6 have annotation on R2
recMBIDs = {}
# recMBIDs['727cff89-392f-4d15-926d-63b2697d7f3f'] = ('18_Munir_Nurettin_Selcuk_-_Gel_Guzelim_Camlicaya',0,0)             # done
# recMBIDs['feda89e3-a50d-4ff8-87d4-c1e531cc1233'] = ('Melihat_Gulses',0,0) # done.
# recMBIDs['f5a89c06-d9bc-4425-a8e6-0f44f7c108ef'] = ('04_Hamiyet_Yuceses_-_Bakmiyor_Cesm-i_Siyah_Feryade',0, 0) # done
# recMBIDs['b49c633c-5059-4658-a6e0-9f84a1ffb08b'] = ('2-15_Nihavend_Aksak_Sarki',0,0)  # done.
recMBIDs['567b6a3c-0f08-42f8-b844-e9affdc9d215'] = ('03_Bekir_Unluataer_-_Kimseye_Etmem_Sikayet_Aglarim_Ben_Halime',0,0)  # done
# recMBIDs['2ec806b4-7df2-4fd4-9752-140a0bcc9730'] = ('21_Recep_Birgit_-_Olmaz_Ilac_Sine-i_Sad_Pareme',0, 0) #  


# following 6 do not have annotation on Rules
# recMBIDs['9c26ff74-8541-4282-8a6e-5ba9aa5cc8a1'] =  ('Sakin--Gec--Kalma', 1,1) # done.
# recMBIDs['43745ff1-0848-4592-b1ad-9e7b172b0ebd'] =  ('06_Semahat_Ozdenses_-_Aksam_Oldu_Huzunlendim',0, 0) # done. no notes annoations

######### these have problems with section numbers
# recMBIDs['dd536d18-aa84-451c-b7e5-d97271300b8c'] =  ('05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var',0,0) # no notes annotation. TODO. annotation https://raw.githubusercontent.com/georgid/turkish_makam_section_dataset/master/audio_metadata/dd536d18-aa84-451c-b7e5-d97271300b8c.json with new sectios as in  https://raw.githubusercontent.com/sertansenturk/turkish_makam_corpus_stats/master/data/SymbTrData/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin.json
#### recMBIDs['338e24ba-1f19-49a1-ad6a-2b89e0e09c38'] =  ('Semahat_Ozdenses',0,1) # not present in sertans section-link annotations. text score sections are 14 and sectionsMetadata with new labels are 32. TODO: redo section Anno with 32 sections ( maybe use annotation from TextGrid)
#### recMBIDs['8c7eccf5-0d9e-4f33-89f0-87e95b7da970'] =   ('Eda_Simsek',1,1) # no second verse.  no notes anno. not present in sertans section-link annotations. has 36 score sections in new metadata (12 old). TODO: redo section Anno with 36 sections ( maybe use annotation from TextGrid)
#### recMBIDs['1701ceba-bd5a-477e-b883-5dacac67da43'] = ('Nurten_Demirkol',1,1) #  not present in sertans section-link annotations. has 10 score sections in new metadata (20 old). TODO: redo section Anno with 36 sections ( maybe use annotation from TextGrid)

### these are needed for extend sectionMetadata script:
# recordingDirs =  [

dunya.set_token("69ed3d824c4c41f59f0bc853f696a7dd80707779")

WITH_SECTION_ANNOTATIONS = 1
PATH_TO_HCOPY= '/usr/local/bin/HCopy'
# ANDRES. On kora.s.upf.edu
# PATH_TO_HCOPY= '/srv/htkBuilt/bin/HCopy'


############# keep this class and use it as a local test version of  pycompmusic/compmusic/extractros/makam/lyricsalign. 
class LyricsAlign(object):
    _version = "0.1"
    _sourcetype = "mp3"
    _slug = "lyrics-align"
    _output = {
            "alignedLyricsSyllables": {"extension": "json", "mimetype": "application/json"},
            "sectionlinks": {"extension": "json", "mimetype": "application/json"}, # refined section links
            }
   




    def __init__(self, dataDir, hasSecondVerse, hasSectionNumberDiscrepancy ):
        self.dataDir = dataDir
        self.hasSecondVerse = hasSecondVerse
        self.hasSectionNumberDiscrepancy = hasSectionNumberDiscrepancy

 

    def run(self, musicbrainzid, fname):
       
        citation = u"""
            Dzhambazov, G., & Serra X. (2015).  Modeling of Phoneme Durations for Alignment between Polyphonic Audio and Lyrics.
            Sound and Music Computing Conference 2015.
            """
       
        #### output
        ret = {'alignedLyricsSyllables':{}, 'sectionlinks':{} }
           
       
        recIDoutputDir = os.path.join(self.dataDir, musicbrainzid)        
        if not os.path.isdir(recIDoutputDir):
                os.mkdir(recIDoutputDir)

        outputDir = tempfile.mkdtemp()
        outputDir = recIDoutputDir

        w = getWork(musicbrainzid)

       
# get symbTr local
        symbtrtxtURI = downloadSymbTr(w['mbid'], recIDoutputDir, self.hasSecondVerse)
       
        if not symbtrtxtURI:
                sys.exit("no symbTr found for work {}".format(w['mbid']) )
       
       
        ############ score section metadata
#         if WITH_SECTION_ANNOTATIONS:            #  because complying with  number of score sections in metadata for symbTr1, on which annotations are done
#             dir_ = 'scores/metadata/'
#             sectionMetadataDict = get_section_metadata_dict(w['mbid'], dir_, recIDoutputDir, self.hasSectionNumberDiscrepancy)
#         else:
            
        sectionMetadataDict = dunya.docserver.get_document_as_json(w['mbid'], "scoreanalysis", "metadata", 1, version="0.1") # NOTE: this is default for note onsets
                     
        
        ##################### audio section annotation  or result from section linking
        if WITH_SECTION_ANNOTATIONS:    #  because complying with section annotations
            try:
                dir_ = 'audio_metadata/'
                sectionLinksDict = get_section_annotaions_dict(musicbrainzid, dir_, outputDir, self.hasSectionNumberDiscrepancy)
            except Exception,e:
                sys.exit("no section annotations found for audio {} ".format(musicbrainzid))
                
        else:
            try:
                sectionLinksDict = dunya.docserver.get_document_as_json(musicbrainzid, "scorealign", "sectionlinks", 1, version="0.2")
            except dunya.conn.HTTPError:
                  logging.error("section link {} missing".format(musicbrainzid))
                  return ret
            if not sectionLinksDict:
                  logging.error("section link {} missing".format(musicbrainzid))
                  return ret
       
        try:   
            extractedPitch = dunya.docserver.get_document_as_json(musicbrainzid, "jointanalysis", "pitch", 1, version="0.1")
        except Exception,e:
            sys.exit("no initialmakampitch series could be downloaded.  ")
       
#  on dunya server      
#         wavFileURI, created = util.docserver_get_wav_filename(musicbrainzid)

# on other computer
       
        wavFileURI =  fetch_audio_wav(self.dataDir, musicbrainzid, ParametersAlgo.POLYPHONIC)
                

       

        wavFileURIMono = stereoToMono(wavFileURI)
        if ParametersAlgo.WITH_ORACLE_ONSETS == 1:
            fetchNoteOnsetFile(musicbrainzid, recIDoutputDir)
       
       
        recording = loadMakamRecording(musicbrainzid, wavFileURIMono, symbtrtxtURI, sectionMetadataDict, sectionLinksDict,  WITH_SECTION_ANNOTATIONS)
        recording.score.printSectionsAndLyrics()
       
        lyricsAligner = LyricsAligner(recording, WITH_SECTION_ANNOTATIONS, PATH_TO_HCOPY)
   
        fullRecordingDetectedTokenList, sectionLinksDict =  lyricsAligner.alignRecording( extractedPitch, outputDir)
        lyricsAligner.store_as_textGrid(fullRecordingDetectedTokenList)
        
        
        if ParametersAlgo.DETECTION_TOKEN_LEVEL != 'phonemes': # phoneme level eval not implemented
            totalCorrectDurations, totalDurations = lyricsAligner.evalAccuracy(ParametersAlgo.EVAL_LEVEL)
       
        ret['alignedLyricsSyllables'] = fullRecordingDetectedTokenList
        ret['sectionlinks'] = sectionLinksDict
#         print ret
        return ret, totalCorrectDurations, totalDurations

# 
# def getWork( musicbrainzid):
#         try:
#             rec_data = dunya.makam.get_recording(musicbrainzid)
#             if len(rec_data['works']) == 0:
#                 raise Exception('No work on recording %s' % musicbrainzid)
#             if len(rec_data['works']) > 1:
#                 raise Exception('More than one work for recording %s Not implemented!' % musicbrainzid)
#             w = rec_data['works'][0]
#         except Exception:
#             sys.exit('no recording with this UUID found or no works related')
#             w = {}
#             w['mbid'] = ''
#         return w
# 
# def get_audio(dataDir, musicbrainzid):
#         recIDoutputDir = os.path.join(dataDir, musicbrainzid)        
#         if not os.path.isdir(recIDoutputDir):
#             os.mkdir(recIDoutputDir)
#        
#         wavFileURI = os.path.join(recIDoutputDir, musicbrainzid + '.wav' )
#        
#         if ParametersAlgo.POLYPHONIC:
#             wavFileURI_as_fetched = download_wav(musicbrainzid, recIDoutputDir)
# #             wavFileURI = wavFileURI_as_fetched
#             os.rename(wavFileURI_as_fetched, wavFileURI)
#         else: # acapella expect file to be already provided in dir
#            
#             if not os.path.isfile(wavFileURI): 
#                 sys.exit("acapella file {} not found".format(wavFileURI))
#         return wavFileURI
# 
# 
# def download_wav(musicbrainzid, outputDir):
#         '''
#         download wav for MB recording id from makam collection
#         '''
#         mp3FileURI = dunya.makam.download_mp3(musicbrainzid, outputDir)
#     ###### mp3 to Wav: way 1
#     #         newName = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'test.mp3')
#     #         os.rename(mp3FileURI, newName )
#     #         mp3ToWav = Mp3ToWav()
#     #         wavFileURI = mp3ToWav.run('dummyMBID', newName)
#        
#         ###### mp3 to Wav: way 2
#         wavFileURI = os.path.splitext(mp3FileURI)[0] + '.wav'
#         if os.path.isfile(wavFileURI):
#             return wavFileURI
#            
#         pipe = subprocess.Popen(['/usr/local/bin/ffmpeg', '-i', mp3FileURI, wavFileURI])
#         pipe.wait()
#    
#         return wavFileURI
# 
# 
# def get_section_annotaions_dict( musicbrainzid, dir_, outputDir, hasSectionNumberDiscrepancy):
#         URL = 'https://raw.githubusercontent.com/georgid/turkish_makam_section_dataset/master/' + dir_ + musicbrainzid + '.json'
#         sectionAnnosURI = os.path.join(outputDir, musicbrainzid + '.json')
#         fetchFileFromURL(URL, sectionAnnosURI)
#        
# #         if not hasSectionNumberDiscrepancy: # because score section metadata taken from sertan's github but section anno from georgis
# #             raw_input("make sure you audio section Annotation... has same section letters as score section Metadata ")
# 
#        
#         with open(sectionAnnosURI) as f3:
#             sectionAnnosDict = json.load(f3) # use annotations instead of links
#         return sectionAnnosDict
# 
# 
# def get_section_metadata_dict( workmbid, dir_, outputDir, hasSectionNumberDiscrepancy):
#        
#         symbtr = dunya.makam.get_symbtr(workmbid)
#         symbTrCompositionName = symbtr['name']
# #         symbTrCompositionName  = 'ussak--sarki--aksak--bu_aksam--tatyos_efendi'
#        
#         if hasSectionNumberDiscrepancy:
#             raw_input("make sure you first run exendSectionLinks... then press key")
#             # my derived with extendsecitonLinksnewNames metadata
#             URL = 'https://raw.githubusercontent.com/georgid/turkish_makam_section_dataset/master/' + dir_ + workmbid + '.json'
#        
#         else:
#             #  use sertans derived metadata with symbTrdataExtractor
#             URL = 'https://raw.githubusercontent.com/sertansenturk/turkish_makam_corpus_stats/master/data/SymbTrData/' + symbTrCompositionName + '.json'
# 
#         sectionAnnosURI = os.path.join(outputDir, symbTrCompositionName + '.json')
#        
#         fetchFileFromURL(URL, sectionAnnosURI)
#        
#        
#         with open(sectionAnnosURI) as f3:
#             sectionAnnosDict = json.load(f3) # use annotations instead of links
#         return sectionAnnosDict
# 
# 
# def downloadSymbTr(workMBID, outputDirURI, hasSecondVerse):
#    
#     symbtr = compmusic.dunya.makam.get_symbtr(workMBID)
#     symbTrCompositionName = symbtr['name']
#    
#     if workMBID == '30cdf1c2-8dc3-4612-9513-a5d7f523a889': # because of problem in work
#         symbTrCompositionName = 'ussak--sarki--aksak--bu_aksam--tatyos_efendi'
#    
#     URL = 'https://raw.githubusercontent.com/MTG/SymbTr/master/txt/' + symbTrCompositionName + '.txt'
#     outputFileURI = os.path.join(outputDirURI, symbTrCompositionName + '.txt')
# 
#     if hasSecondVerse:
#         raw_input("composition has a second verse not in github. copy symbTr manually to {}.\n  when done press a key ".format(outputFileURI))
#     else:
#         fetchFileFromURL(URL, outputFileURI)
#         print "downloaded symbtr file  {}".format(outputFileURI) 
# 
#     return outputFileURI
# 
# 
# 
# def fetchNoteOnsetFile(musicbrainzid,  recIDoutputDir):
#     '''
#     fetch note onset annotations
#     '''
# 
#             
#     onsetPath = os.path.join(recIDoutputDir,  ParametersAlgo.ANNOTATION_RULES_ONSETS_EXT)
#     if not os.path.isfile(onsetPath):
#                 work = getWork(musicbrainzid)
#                 symbtr = dunya.makam.get_symbtr(work['mbid'])
#                 symbTrCompositionName = symbtr['name']
#                 URL = 'https://raw.githubusercontent.com/MTG/turkish_makam_audio_score_alignment_dataset/vocal-only-annotation//data/' + symbTrCompositionName + '/' + musicbrainzid + '/' + ParametersAlgo.ANNOTATION_RULES_ONSETS_EXT
#                
#                 # problem with symbTrComposition name
# #                 URL = 'https://raw.githubusercontent.com/MTG/turkish_makam_audio_score_alignment_dataset/master/data/nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi/feda89e3-a50d-4ff8-87d4-c1e531cc1233/' + ParametersAlgo.ANNOTATION_RULES_ONSETS_EXT
#                 fetchFileFromURL(URL, onsetPath )
#                
# 
# 
# 
# 
# 
# def fetchFileFromURL(URL, outputFileURI):
#         print "fetching file from URL {} ...  ".format(URL)
#         try:
#             response = urllib2.urlopen(URL)
#             a = response.read()
#         except Exception:
#             "...maybe symbTr name has changed"
#        
#         with open(outputFileURI,'w') as f:
#             f.write(a)


def doitAllRecs(la, recMBIDs):
    totalCorrectDurations_all=0; totalDurations_all = 0
    for recMBID in  recMBIDs:
        la = LyricsAlign(dataDir, recMBIDs[recMBID][1], recMBIDs[recMBID][2] ) 
        ret, totalCorrectDurations, totalDurations = la.run(recMBID, 'testName')
        
        totalCorrectDurations_all += totalCorrectDurations
        totalDurations_all += totalDurations
        
#         with open('/Users/joro/Downloads/bu_aksam_gun.json', 'w') as f:
#             json.dump( ret, f, indent=4 )
#         raw_input('press enter...')

    accuracy = totalCorrectDurations_all / totalDurations_all
    logging.warning("total  accuracy: {:.2f}".format( accuracy))
       


if __name__=='__main__':


   
#     if len(sys.argv) != 2:
#         sys.exit('usage: {} <localpath>')
#     la = LyricsAlign(sys.argv[1])
   



   
    doitAllRecs(dataDir, recMBIDs)
   
#     la.run('727cff89-392f-4d15-926d-63b2697d7f3f','b')
#     la.run('567b6a3c-0f08-42f8-b844-e9affdc9d215','b')
       