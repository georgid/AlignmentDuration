#! /usr/bin/python
# -*- coding: utf-8 -*-
import textgrid as tgp
import sys, os
# from onsets.OnsetDetector import writeCsv


sys.path.append(os.path.realpath('../Batch_Processing/'))
# import Batch_Proc_Essentia as BP  # @UnresolvedImport


   # utility enumerate constants class 
class Enumerate(object):
  def __init__(self, names):
    for number, name in enumerate(names.split()):
      setattr(self, name, number)

# tierAliases = Enumerate("phonemeLevel wordLevel phraseLevel lyrics-syllables-pinyin sections")
tierAliases = Enumerate("phonemes words phrases pinyin sections line details xsampadetails xsampadetails_with_sp dian dianDuration isNonKeySyllLong isLastSyllLong")
tier_names = ["phonemes", "words", "phrases", "pinyin", "sections", "line", "details", "xsampadetails", "xsampadetails_with_sp" ,"dian", "dianDuration", "isNonKeySyllLong", "isLastSyllLong"];

# tierAliases = Enumerate("phonemes words phrases pinyin sections line detailsgeorgi")
# tier_names = ["phonemes", "words", "phrases", "pinyin", "sections", "line", "detailsgeorgi"];   



def readNonEmptyTokensTextGrid(annotationURI, whichLevel, startIdx, endIdx, initialTimeOffset=0):
    '''
    ######################
    # prepare list of phrases from ANNOTATION. remove empty annotation tokens
    @param endIdx: set endIdx to be -1 if all tokens wanted
    
    @return: annotationTokenListNoPauses - list of tuples (index from original list of tokens, token with lyrics)
    '''
    try:
        annotationTokenListAll = TextGrid2WordList(annotationURI, whichLevel)
    except Exception as errorMsg:
        sys.exit(str(errorMsg))
    
    if endIdx != -1:
        annotationTokenListAll = annotationTokenListAll[startIdx : endIdx+1]
    
    for currAnnoTsAndToken in annotationTokenListAll:
        currAnnoTsAndToken[0] = float(currAnnoTsAndToken[0])
        currAnnoTsAndToken[0] += initialTimeOffset
        currAnnoTsAndToken[1] = float(currAnnoTsAndToken[1])
        currAnnoTsAndToken[1] += initialTimeOffset

    
    # store to file .anno
    baseN = os.path.basename(annotationURI)
    dir = os.path.dirname(annotationURI)
    annotationURI_anno = os.path.join(dir,baseN+'.csv')
    
    
#     writeListOfListToTextFile(annotationTokenListAll, None,   annotationURI_anno )

    annotationTokenListNoPauses = []
    
    #########
    # remove empty phrases

    for idxListAll,currAnnoTsAndToken in enumerate(annotationTokenListAll):
        if currAnnoTsAndToken[2] != "" and not (currAnnoTsAndToken[2].isspace()): # skip empty phrases
            currAnnoTsAndToken.append(idxListAll) # add index to list of all tokens
            annotationTokenListNoPauses.append(currAnnoTsAndToken)

    return annotationTokenListAll, annotationTokenListNoPauses

'''
textGrid to dictionary column file 
'''
def TextGrid2Dict(textgrid_file, outputFileName):
	
	par_obj = tgp.TextGrid.load(textgrid_file)	#loading the object	
	tiers= tgp.TextGrid._find_tiers(par_obj)	#finding existing tiers
    
	outputFileHandle = open(outputFileName, 'w')
	
	
	for tier in tiers:
		
		if tier.tier_name() == tier_names[2]:	#iterating over tiers and selecting the one specified
			
			tier_details = tier.make_simple_transcript();		#this function parse the file nicely and return cool tuples
			
			for line in tier_details:
				
				outputFileHandle.write(line[0] + "\t" + line[2]+ "\n") 

	outputFileHandle.close()		


def TextGrid2WordList(textgrid_file, whichTier=2):
    '''
    parse textGrid into a python list of tokens 
    @param whichTier : 0 -  phonemes,    1- words, 2 - phrases  
    '''	
    if not os.path.isfile(textgrid_file): raise Exception("Annotation file {} not found".format(textgrid_file))
    beginTsAndWordList=[]
	
    par_obj = tgp.TextGrid.load(textgrid_file)	#loading the object	
    tiers= tgp.TextGrid._find_tiers(par_obj)	#finding existing tiers		
	
    isTierFound = 0
    for tier in tiers:
        tierName= tier.tier_name().replace('.','')
        if int(whichTier) >= len(tier_names):
            sys.exit("tiers are {} but requested tier {}".format(len(tier_names),int(whichTier) ))
        if tierName ==  tier_names[int(whichTier)]:	#iterating over tiers and selecting the one specified
			isTierFound = 1
			tier_details = tier.make_simple_transcript();		#this function parse the file nicely and return cool tuples
			
			for line in tier_details:
				beginTsAndWordList.append([float(line[0]), float(line[1]), line[2]])
    if not isTierFound:
		raise Exception('tier in file {0} might not be named correctly. Name it {1}' .format(textgrid_file,  tier_names[whichTier]))
    return beginTsAndWordList		


##################################################################################

def toChronTest(textgrid_file):
    par_obj = tgp.TextGrid.load(textgrid_file)    #loading the object    
    chronFile = tgp.TextGrid.to_chron(par_obj)
    print chronFile


def testreadNonEmptyTokensTextGrid():
    

    lowLevel = tierAliases.xsampadetails # read phonemesAnno
    lyricsTextGrid = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/fold1/xixiangji_biyuntian.TextGrid'
    lyricsTextGrid = '/Users/joro/Documents/Phd/UPF/voxforge/myScripts/HMMDuration/hmm/examples/KiseyeZeminPhoneLevel_2_zemin.TextGrid'
    initialOffset = 51.35
    
    lyricsTextGrid = '/Users/joro/Downloads/ISTANBULSymbTr2/567b6a3c-0f08-42f8-b844-e9affdc9d215/567b6a3c-0f08-42f8-b844-e9affdc9d215_51.35423_72.248897.TextGrid'
    phonemesAnnoList, phonemesAnnoListNoPauses = readNonEmptyTokensTextGrid(lyricsTextGrid, lowLevel, 0, -1, initialOffset)
    for phoneme in phonemesAnnoListNoPauses:
            phoneme[3] = 1
#     writeCsv(os.path.splitext(lyricsTextGrid)[0] + '.csv' , phonemesAnnoListNoPauses)

if __name__ == '__main__':
    testreadNonEmptyTokensTextGrid()