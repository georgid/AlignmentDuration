# function to call the extractHarmSpec analysis/synthesis functions in software/models/harmonicModel.py

import numpy as np
import matplotlib.pyplot as plt
import os, sys
from scipy.signal import get_window
import logging

sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../software/models/'))
import utilFunctions as UF
import sineModel as SM
import harmonicModel as HM

# import software.models.utilFunctions as UF
# import software.models.sineModel as SM
# import software.models.harmonicModel as HM


# inputFile = '../sounds/vignesh.wav'

# def extractHarmSpec(inputFile='../sounds/vignesh.wav', window='blackman', M=1201, N=2048, t=-90, 
# 	minSineDur=0.1, nH=100, minf0=130, maxf0=300, f0et=7, harmDevSlope=0.01):

# increasing the threshold means discarding more  peaks and selecting less 	
def extractHarmSpec( inputFile, f0FreqsRaw, fromTs, toTs, t=-70, window='blackman',  M=2047, N=2048 , 
	minSineDur=0.0, nH=30, harmDevSlope=0.02):
	"""
	Analysis and synthesis using the harmonic model
	inputFile: input sound file (monophonic with sampling rate of 44100)
	window: analysis window type (rectangular, hanning, hamming, blackman, blackmanharris)	
	M: analysis window size; N: fft size (power of two, bigger or equal than M)
	t: magnitude threshold of spectral peaks; minSineDur: minimum duration of sinusoidal tracks
	nH: maximum number of harmonics; minf0: minimum fundamental frequency in sound
	maxf0: maximum fundamental frequency in sound; f0et: maximum error accepted in f0 detection algorithm                                                                                            
	harmDevSlope: allowed deviation of harmonic tracks, higher harmonics could have higher allowed deviation
	"""
	
	# read input sound
	(fs, x) = UF.wavread(inputFile)
	

# 	hopsize
	hopSizeMelodia = int( round( (float(f0FreqsRaw[1][0])  - float(f0FreqsRaw[0][0]) ) * fs ) )

	### get indices in melodia
	toTs = float(toTs)
 	if fromTs==-1 and toTs==-1:
 		logging.debug("fromTs and toTs not defined. extracting whole recording")
 		fromTs=0; toTs=f0FreqsRaw[-1][0]
    		
	
	idx = 0
	while fromTs > float(f0FreqsRaw[idx][0]):
		idx += 1
	
	firstTs = float(f0FreqsRaw[idx][0])
	pinFirst  = round (firstTs * fs)
		
	f0Series = []
	while  idx < len(f0FreqsRaw) and float(f0FreqsRaw[idx][0]) <= toTs:
		f0Series.append(float(f0FreqsRaw[idx][1])) 
		idx += 1
	lastTs = float(f0FreqsRaw[idx-1][0])
	pinLast = round (lastTs * fs)
	

	
	# discard ts-s
# 	for foFreqRaw in range() f0FreqsRaw:
# 		f0Series.append(float(foFreqRaw[1])) 
	
	# size of fft used in synthesis

	
	# hop size (has to be 1/4 of Ns)
# 	H = 128


	# compute analysis window
	w = get_window(window, M)

	# detect harmonics of input sound
	hfreq, hmag, hphase = HM.harmonicModelAnal_2(x, fs, w, N, hopSizeMelodia, pinFirst, pinLast, t, nH, f0Series, harmDevSlope, minSineDur)

# w/o melodia and with resynthesis 
# 	minf0=130
# 	maxf0=300
# 	f0et=7
# 	HM.harmonicModel(x, fs, w, N, t, nH, minf0, maxf0, f0et)


	
	return hfreq, hmag, hphase, fs, hopSizeMelodia, x[pinFirst:pinLast]
	
def resynthesize(hfreq, hmag, hphase, fs, hopSizeMelodia, URIOutputFile):
	''' synthesize the harmonics
	'''
# 	Ns = 512
	Ns = 4 * hopSizeMelodia

	y = SM.sineModelSynth(hfreq, hmag, hphase, Ns, hopSizeMelodia, fs)  

	# output sound file (monophonic with sampling rate of 44100)
# 	URIOutputFile = 'output_sounds/' + os.path.basename(inputFile)[:-4] + '_harmonicModel.wav'
	
	
	# write the sound resulting from harmonic analysis
	UF.wavwrite(y, fs, URIOutputFile)
	
	return y
	
	
# 	##########################
# 	## plotting of harmonic spectrum
# 	
def visualizeHarmSp(x, y, hopSizeMelodia ):
	# create figure to show plots
	plt.figure(figsize=(12, 9))
 
	# frequency range to plot
	maxplotfreq = 10000.0
 
	# plot the input sound
	plt.subplot(3,1,1)
	plt.plot(np.arange(x.size)/float(fs), x)
	plt.axis([0, x.size/float(fs), min(x), max(x)])
	plt.ylabel('amplitude')
	plt.xlabel('time (sec)')
	plt.title('input sound: x')
 
	# plot the harmonic frequencies
	plt.subplot(3,1,2)
	if (hfreq.shape[1] > 0):
		numFrames = hfreq.shape[0]
		frmTime = hopSizeMelodia * np.arange(numFrames)/float(fs)
		hfreq[hfreq<=0] = np.nan
		plt.plot(frmTime, hfreq)
		plt.axis([0, x.size/float(fs), 0, maxplotfreq])
		plt.title('frequencies of harmonic tracks')
 
	# plot the output sound
	plt.subplot(3,1,3)
	plt.plot(np.arange(y.size)/float(fs), y)
	plt.axis([0, y.size/float(fs), min(y), max(y)])
	plt.ylabel('amplitude')
	plt.xlabel('time (sec)')
	plt.title('output sound: y')
 
	plt.tight_layout()
	plt.show()

if __name__ == "__main__":
	
# 	inputFile = 'example_data/dan-erhuang_01_1.wav'
# 	melodiaInput = 'example_data/dan-erhuang_01.txt'

	inputFile = '/Users/joro/Documents/Phd/UPF/arias/laosheng-erhuang_04.wav'
	melodiaInput = '/Users/joro/Documents/Phd/UPF/arias/laosheng-erhuang_04.melodia'
	fromTs = 49.85
	toTs = 55.00
	
	fromTs = 0
	toTs = 858
		
# 	inputFile = '../sounds/vignesh.wav'
# 	melodiaInput = '../sounds/vignesh.melodia'
# 	fromTs = 0
# 	toTs = 2
	

	# exatract spectrum
	hfreq, hmag, hphase, fs, hopSizeMelodia, inputAudioFromTsToTs = extractHarmSpec(inputFile, melodiaInput, fromTs, toTs)
	np.savetxt('hfreq_2', hfreq)
	np.savetxt('hmag_2', hmag)
	np.savetxt('hphase_2', hphase)
	
	hfreq = np.loadtxt('hfreq_2')
	hmag = np.loadtxt('hmag_2')
	hphase = np.loadtxt('hphase_2')
	
	# resynthesize
	URIOutputFile = 'output_sounds/' + os.path.basename(inputFile)[:-4] + '_harmonicModel.wav'
	y = resynthesize(hfreq, hmag, hphase, fs, hopSizeMelodia, URIOutputFile)
	
	visualizeHarmSp(inputAudioFromTsToTs, y, hopSizeMelodia )
	
