'''
Created on Mar 17, 2015
 see V. Rao and P. Rao - Vocal melody extraction in the presence of pitched accompaniment in polyphonic music, II.B

@author: joro
'''

from scipy.signal import get_window
import os
import sys
import math
import numpy as np
sys.path.append(os.path.join(os.path.dirname(os.path.realpath(__file__)), '../software/models/'))
import utilFunctions as UF
import sineModel as SM
import harmonicModel as HM
import dftModel as DFT
import matplotlib.pyplot as plt

parentParentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0]) ), os.path.pardir,  os.path.pardir)) 
pathUtils = os.path.join(parentParentDir, 'utilsLyrics')
if pathUtils not in sys.path:
    sys.path.append(pathUtils )

inputFile = '../sounds/vignesh.wav'
melodiaInput = '../sounds/vignesh.melodia'

from Utilz import readListOfListTextFile_gen


def doit():
    M=2047
    N=2048
     
    # read input sound
    (fs, x) = UF.wavread(inputFile)
    # correponds to db = -70
    t = 0.0003162
    
    #correponds to db = -90
    t = 0.00003162

#     readf0 from Melodia 
    f0FreqsRaw = readListOfListTextFile_gen(melodiaInput)
    hopSizeMelodia = int( round( (float(f0FreqsRaw[1][0])  - float(f0FreqsRaw[0][0]) ) * fs ) )
    
    firstTs = float(f0FreqsRaw[0][0])
    pinFirst  = round (firstTs * fs)
    
    # discard ts-s
    f0Series = []
    for foFreqRaw in f0FreqsRaw:
        f0Series.append(float(foFreqRaw[1])) 
    

    window='blackmanharris'
    # compute analysis window
    w = get_window(window, M)
    
    # 2freq domain 
    mX, iploc, ipmag, ipphase = time2Freq(x, fs, w, N, pinFirst,hopSizeMelodia, t)
    
    calcPeakSimilarityAll(mX, N, fs, iploc, ipmag, ipphase)
    
 
    

def time2Freq(x, fs, w, N, pinFirst, hopSizeMelodia, t):
    '''
    makes fourier transform, peak thresholding and interpolation  for one window
    return interpolated 
    iploc, ipmag, ipphase
    '''
    
    ###################
    ## prepare params    
    hM1 = int(math.floor((w.size+1)/2))                     # half analysis window size by rounding
    hM2 = int(math.floor(w.size/2))                         # half analysis window size by floor
    x = np.append(np.zeros(hM2),x)                          # add zeros at beginning to center first window at sample 0
    x = np.append(x,np.zeros(hM2))                          # add zeros at the end to analyze last sample
    #     pin = hM1                                               # init sound pointer in middle of anal window          
    pin = pinFirst + 300 * hopSizeMelodia
    pend = x.size - hM1                                     # last sample to start a frame
    
    ########################
    # process one window     
    print "at time {}".format(pin/fs)

    x1 = x[pin-hM1:pin+hM2]                               # select frame
    mX, pX = DFT.dftAnal(x1, w, N)                        # compute dft   
    
    ploc = UF.peakDetection(mX, t)                        # detect peak locations   
    
    iploc, ipmag, ipphase = UF.peakInterp(mX, pX, ploc)   # refine peak values
    
    # optional
    visualize(N, mX, pin, fs, ploc, iploc, ipmag, ipphase )
    
    return mX, iploc, ipmag, ipphase
    
def calcPeakSimilarityAll(mX, N, fs, iploc, ipmag, ipphase ):
    for (currIploc, currIpmag, currIpphase) in  zip(iploc, ipmag, ipphase):
        currPeakSim = calcPeakSimilarity(currIploc, currIpmag, currIpphase, mX, N, fs)
        print currPeakSim
        
def visualize(N, mX, pin, fs, ploc, iploc, ipmag, ipphase ):
    '''
    visuaizes 
    '''   
    ipfreq = fs * iploc/N
    
    # generate total spectrum by main lobe
    X = UF.genSpecSines_p(ipfreq, ipmag, ipphase, N, fs)     # generate spec sines
    
    hN = N/2 + 1                                               # size of positive spectrum
    absX = abs(X[:hN])                                      # compute ansolute value of positive side
    absX[absX<np.finfo(float).eps] = np.finfo(float).eps    # if zeros add epsilon to handle log
    generatedX = absX
#     generatedX = 20 * np.log10(absX) 
    
    ########################
    visualizeSpectum(mX,pin/fs, ploc, iploc, ipmag, generatedX)
        

def visualizeSpectum(spectrum, timestamp, ploc,  iploc, ipmag, generatedX):
    # create figure to show plots
    plt.figure(figsize=(12, 9))
    freqBinNums = np.arange(len(spectrum))
    # plot

#     plot original spectrum
    plt.vlines(freqBinNums, [0], spectrum,  linewidth=1)
    

    # plot picked peaks
    plt.vlines(ploc, [0], spectrum[ploc], linewidth=2, color='b')
    
    # plot peak interp peaks
    plt.vlines(iploc, [0], ipmag, linewidth=2, color='r')
    
    # plot main-lobes
    
    plt.vlines(freqBinNums, [0], generatedX, linewidth=2, color='g')
    
    plt.title('at time ' + str(timestamp) )
    plt.show()
    
def calcPeakSimilarity(ipfreq, ipmag, ipphase, spectrum, N, fs): 
    '''
    for spectrum @param spectrum calculates the similarity for one peak.
    Peak centered at interpolated 
    @param: ipfreq with @param: ipmag and phrase @param ipphase
    Generates blackman harris window in spectral domain 
    Uses metric descibed in Rao: section II.B
    '''
    
    epsilonM = 0
    
    nominatorA = 0
    denominatorA = 0
    
    denominatorS  = 0
    
    mainLobeSpec,bins = UF.genSpecSines_p_onePeak(ipfreq, ipmag, ipphase, N, fs)     # generate spec sines
    
    hN = N/2 + 1                                               # size of positive spectrum
    absMainLobeSpec = abs(mainLobeSpec[:hN])                                      # compute ansolute value of positive side
    absMainLobeSpec[absMainLobeSpec<np.finfo(float).eps] = np.finfo(float).eps    # if zeros add epsilon to handle log


    # epsion. no norm term A needed because genSpecSines_p_onePeak uses magnitude ipmag from original spectrum
    for i, b_i in enumerate(bins):
        # negative freq values are replaced with  mirror-freq (hack: analogous to UF.genSpecSines_p_onePeak) 
        if b_i < 0 or b_i >= hN:
            continue
        
        nominatorA += (absMainLobeSpec[b_i] * spectrum[b_i])
        denominatorA += math.pow( absMainLobeSpec[b_i] , 2)

        denominatorS += math.pow( spectrum[b_i] , 2)
    if denominatorA == 0: sys.exit("denominator A = 0")
    
    A = nominatorA / denominatorA
    
    # epsion. no norm term A needed because genSpecSines_p_onePeak uses magnitude ipmag from original spectrum
    for i, b_i in enumerate(bins):
        # negative freq values are replaced with  mirror-freq (hack: analogous to UF.genSpecSines_p_onePeak) 
        if b_i < 0 or b_i >= hN:
            continue
        diff = math.pow( ( spectrum[b_i] - A * absMainLobeSpec[b_i] ) , 2)
        epsilonM += diff
        
         
    # normalize over overall magnitude of peak. 2*Pi cancels, so not needed
    if denominatorS == 0: sys.exit("denominator S = 0")
 
    S = 1 - (epsilonM / denominatorS)
    return S
      
    
if __name__ == "__main__":
    doit()