
import sys
from doitOneRecording import doitOneRecording

def doit(argv):
	
	if len(argv) != 3 and len(argv) != 4  :
            print ("usage: {}  <pathToCompositions>  <pathToRecordings> <usePersistentFiles=False>".format(argv[0]) )
            sys.exit();
	
	# todo: adjust these params
# 	pathToScores = 'turkish-makam-lyrics-2-audio-test-data/'
	pathToScores = argv[1]
	
# 	path_testFile = pathToScores
	path_testFile  = argv[2]
	
	usePersistentFiles = False
	if len(argv) == 4:
		usePersistentFiles = argv[3]
	
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
	
	outputFileHandle = open('alignError.out', 'w', 'utf-8')

	
	totalMean  = 0
	for i in range(len(scores)):
		URI_score = pathToScores + scores[i]
		URI_testFile = path_testFile + subpaths[i]
		pattern  = patterns[i]
		
		print "doing command ...\n doitOneRecording  " + URI_score + " " +  URI_testFile  + " " + pattern
		mean, stDev  = doitOneRecording([ 'dummy', URI_score, URI_testFile, pattern, usePersistentFiles])
		listLine = URI_score + " " + pattern + " " + str(mean) + '\n'
        outputFileHandle.write(listLine)
        totalMean  += mean 
	
	result = 'total mean: ' + str(totalMean/len(scores))
	print result
	
	outputFileHandle.write(result)
	outputFileHandle.close()

if __name__ == '__main__':
	doit(sys.argv)
