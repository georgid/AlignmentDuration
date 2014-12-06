
import sys
from doitOneRecording import doitOneRecording
import logging
from datetime import datetime
import os


def doit(argv):
	
	if len(argv) != 4 and len(argv) != 5  :
            print ("usage: {}  <pathToCompositions>  <pathToRecordings> <ALPHA> <usePersistentFiles=False>".format(argv[0]) )
            sys.exit();
	
	# todo: adjust these params
# 	pathToScores = 'turkish-makam-lyrics-2-audio-test-data/'
	pathToScores = argv[1]
	
# 	path_testFile = pathToScores
	path_testFile  = argv[2]
	
	ALPHA = argv[3]
	usePersistentFiles = False
	if len(argv) == 5:
		usePersistentFiles = argv[4]
	
	scores = ['nihavent--sarki--curcuna--kimseye_etmem--kemani_sarkis_efendi', \
	'nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/', \
	'nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/', \
	'nihavent--sarki--aksak--koklasam_saclarini--artaki_candan/', \
	'ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses',\
	'nihavent--sarki--aksak--bakmiyor_cesm-i--haci_arif_bey',\
	'ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses', \
	'segah--sarki--curcuna--olmaz_ilac--haci_arif_bey'
	]
	subpaths = ['/goekhan/', '/goekhan/', '/barbaros/', '/barbaros/', '/safiye/', '/safiye/', '/guelen/', '/guelen/' ]
	patterns = ['02_Kimseye', '02_Gel', '02_Gel', '02_Koklasam',   '01_Aksam' ,    '01_Bakmiyor', '01_Aksam', '01_Olmaz' ]
	
	currTime = datetime.now().strftime('%Y-%m-%d--%H-%M-%S')	
	filename = os.path.join(os.getcwdu(),   'alignError_' + currTime + '.out') 
	outputFileHandle = open(filename, 'a')
	
	
	outputFileHandle.write('\n'  + str(ALPHA) )
	totalMean  = 0.0
	for i in range(len(scores)):

		URI_score = pathToScores + scores[i]
		URI_testFile = path_testFile + subpaths[i]
		pattern  = patterns[i]
		
		logging.info("doing command ...\n doitOneRecording  " + URI_score + " " +  URI_testFile  + " " + pattern)
# 		mean, stDev  = doitOneRecording([ 'dummy', URI_score, URI_testFile, pattern, ALPHA, usePersistentFiles])
		mean = 2
		stDev = 3
		listLine = '\n' + subpaths[i] + " " + pattern + " " + str(mean) +   " " + str(stDev) 
		
		if outputFileHandle.closed:
			outputFileHandle = open(filename, 'a')
		outputFileHandle.write(listLine)
		outputFileHandle.close()
		
		totalMean  += mean 
	
	result = '\n' + 'total mean: ' + str(totalMean/len(scores)) + '\n'
	print result
	
	if outputFileHandle.closed:
		outputFileHandle = open(filename, 'a')
	outputFileHandle.write(result)
	
	outputFileHandle.close()
	print 'written to file ' + filename 
	
	

	
if __name__ == '__main__':
	doit(sys.argv)
	
	
	
