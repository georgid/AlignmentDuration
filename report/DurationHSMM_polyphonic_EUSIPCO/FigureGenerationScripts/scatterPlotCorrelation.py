import matplotlib.pyplot as pyplot


# core dev read form here: with-SAZ
# /Users/joro/Documents/Phd/UPF/withSAZ/turkish-makam-lyrics-2-audio-test-data-synthesis/rast--sarki--curcuna--nihansin_dideden--haci_faik_bey/alignError_2015-03-07--15-36-53.out
scoreDev  = [0.86, 
0.84, 
0.90, 
 0.80, 
0.69, 
 0.94, 
 0.88 - 0.002,
0.88, 
 0.91,
 0.92 - 0.002, 
  0.87, 
  0.92]



noDurationError = [

0.516490829974,
0.634393584405,
0.782236363131,
0.787080869236,
0.699770531142,
0.72872955498,
0.767838644833 - 0.005,
0.557009046317,
0.683730223343,
0.799722142547,
0.740651630304,
0.576972387971

]

durationError =  [
0.869704801244,
0.796500513883,
0.76067062319,
0.804287127171,
0.834204657829,
0.837431094783,
0.767743686088,
0.825394723462,
0.745095767979,
0.924637494555,
0.676065307666,
0.54919312463
]

# with-SAZ from /mnt/compmusic/users/georgid/dataset12sarki/turkish-makam-lyrics-2-audio-test-data-synthesis/rast--sarki--curcuna--nihansin_dideden--haci_faik_bey/alignError_2015-03-07--15-54-33.out
durationErrorAcapella =  [
0.9170,
0.8825,
0.9172,
0.9099,
0.8764,
0.9298,
0.7716,
0.9389,
0.9161,
0.9261,
0.8451,
0.9229
]

import numpy as np
scoreDev = 100*np.array(scoreDev) 
noDurationError = 100*np.array(noDurationError)
durationError = 100*np.array( durationError)
durationErrorAcapella = 100*np.array( durationErrorAcapella)

 
# markers = ['d','v','8','H','s','h','D','^','p','H','v','<']

fig1 = pyplot.figure(figsize=(20,7.5))    

for i in range(len(scoreDev)):
    pyplot.scatter(scoreDev[i], noDurationError[i], marker='D', color='cyan', facecolors='none', s=100)
    pyplot.scatter(scoreDev[i], durationError[i], marker='D', color='red',  s=50)
    pyplot.scatter(scoreDev[i], durationErrorAcapella[i], marker='p', color='green',  s=110, facecolors='none')

    pyplot.plot([scoreDev[i], scoreDev[i]], [noDurationError[i], durationError[i]],  linestyle='dotted', color='black'  )
    pyplot.plot([scoreDev[i], scoreDev[i]], [noDurationError[i], durationErrorAcapella[i]],  linestyle='dotted', color='black'  )


#because of labeling
pyplot.scatter(scoreDev[i], noDurationError[i], marker='D', color='cyan', facecolors='none', s=100, label='baseline polyphonic')
pyplot.scatter(scoreDev[i], durationError[i], marker='D', color='red', s=50, label='proposed polyphonic')
pyplot.scatter(scoreDev[i], durationErrorAcapella[i], marker='p', color='green', s=110, facecolors='none', label='proposed acapella')

pyplot.xlabel('musical score in-sync accuracy (%)', fontsize=28)
pyplot.ylabel('alignment accuracy (%)', fontsize=28)

pyplot.xlim([78,96])
# pyplot.ylim([50,100])

ax = pyplot.gca()
ax.yaxis.grid(True)

ax.legend(loc=3, fontsize=25)
fig1.savefig('/Users/joro/Documents/Phd/UPF/papers/DurationHSMM_polyphonic_poster/scatterCorrelation.svg')

