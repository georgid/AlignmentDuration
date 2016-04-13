'''
Created on Oct 1, 2015

@author: joro


'''
import os
import sys
from lyricsParser import divideIntoSentencesFromAnnoWithSil

parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

if parentDir not in sys.path:
    sys.path.append(parentDir)

dirUtilsLyrics = parentDir + 'utilsLyrics'
if dirUtilsLyrics not in sys.path:
    sys.path.append(dirUtilsLyrics)

AlignmentDurURI = parentDir + 'AlignmentDuration'
if AlignmentDurURI not in sys.path:
    sys.path.append(AlignmentDurURI)    
    
from PhonetizerDict import tokenizePhonemes, createDictSyll2XSAMPA
from ParsePhonemeAnnotation import     validatePhonemesOneSyll,  validatePhonemesWholeAria


def validatePhonemesOneSyllTest():
    '''
    test parsing of one syll by its syl idx
    '''
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/arias_dev_01_t_70/dan-xipi_02'
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/fold1/xixiangji_biyuntian'
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/fold1/shiwenhui_tingxiongyan'
    
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'

    listSentences = divideIntoSentencesFromAnnoWithSil(lyricsTextGrid, False) #uses TextGrid annotation to derive structure. 
    # TextGrid-1
    syllableIdx = 273
    currSyllable = listSentences[5].listWords[15].syllables[0]
    dictSyll2XSAMPA = createDictSyll2XSAMPA()
    validatePhonemesOneSyll(lyricsTextGrid, syllableIdx, dictSyll2XSAMPA, currSyllable)
    
    
def validatePhonemesWholeAriaTest():

    
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/wangjiangting_dushoukong'
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/shiwenhui_tingxiongyan'
    
    URIrecordingNoExt = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/fold1/xixiangji_biyuntian'
    lyricsTextGrid = URIrecordingNoExt + '.TextGrid'
    
    
    validatePhonemesWholeAria(lyricsTextGrid)
    

def vaidatePhonemesAllArias():
##### automatic dir parsing:    
    path = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/'
    from Utilz import findFilesByExtension
    
    folds = ['fold1/', 'fold2/', 'fold3/']            
    for fold_ in folds:
    
            URiREcordings = findFilesByExtension(path + fold_, 'wav')
            if len(URiREcordings) == 0:
                sys.exit("path {} has no wav recordings".format(path))
            for URiREcording in URiREcordings:
                URIrecordingNoExt = os.path.splitext(URiREcording)[0] 
                lyricsTextGrid = URIrecordingNoExt + '.TextGrid'
                validatePhonemesWholeAria(lyricsTextGrid)
        
      
     
     
      
#     if len(argv) != 2:
#             print ("Tool to check consistency of timestamps among annotation layers  ")
#             print ("usage: {}   <URI_textGrid> ".format(argv[0]) )
#             sys.exit()
#          
#     lyricsTextGrid = argv[1]
      

    
    
def tokenizePhonemesTest():
    phonemesSAMPA = [ u"r\\'i"]
    phonemesSAMPA = [ u'j',u"iu"]
    phonemesSAMPA = [ u"@r\\'"]
    
    phonemesSAMPAQueue = tokenizePhonemes(phonemesSAMPA)
    print phonemesSAMPAQueue
    
    
def  createDictSyll2XSAMPATest():
    dictSyll2XSAMPA = createDictSyll2XSAMPA()
    import json
    json.dump(dictSyll2XSAMPA, open("DictSyll2XSAMPA.txt",'w'), indent=4, sort_keys=True)
    syllableText = 'shang'
    phonemesDictSAMPA = dictSyll2XSAMPA[syllableText]
    print phonemesDictSAMPA
    
    
if __name__ == '__main__':
    
#     validatePhonemesOneSyllTest() 
    vaidatePhonemesAllArias()        
#     validatePhonemesWholeAriaTest()

  
#     createDictSyll2XSAMPATest()
#     tokenizePhonemesTest()

    