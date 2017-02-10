import matplotlib.pyplot as pyplot


# core dev read form here: with-SAZ
# /Users/joro/Documents/Phd/UPF/withSAZ/turkish-makam-lyrics-2-audio-test-data-synthesis/rast--sarki--curcuna--nihansin_dideden--haci_faik_bey/alignError_2015-03-07--15-36-53.out
# scoreDev  = [0.86, 
# 0.84, 
# 0.90, 
#  0.80, 
# 0.69, 
#  0.94, 
#  0.88 - 0.002,
# 0.88, 
#  0.91,
#  0.92 - 0.002, 
#   0.87, 
#   0.92]



acapellaHMM = [

0.756490829974,
0.704393584405,
0.752236363131,
0.787080869236,
0.77770531142,
0.72872955498,
0.627838644833 - 0.005,
0.657009046317,
0.653730223343,
0.729722142547,
0.720651630304,
0.776972387971

]

acapellaVTHMM =  [
0.869704801244,
0.796500513883,
0.82067062319,
0.894287127171,
0.834204657829,
0.837431094783,
0.767743686088,
0.825394723462,
0.745095767979,
0.824637494555,
0.816065307666,
0.89919312463
]



import numpy as np
# scoreDev = 100*np.array(scoreDev) 

acapellaHMM = 100*(np.array(acapellaHMM) - 0.03)
acapellaVTHMM = 100*(np.array( acapellaVTHMM) -  0.09)
#acapellaVTHMMAcapella = 100*np.array( acapellaVTHMMAcapella)

 
# markers = ['d','v','8','H','s','h','D','^','p','H','v','<']

fig1 = pyplot.figure(figsize=(20,7.5))    

for i in range(len(acapellaHMM)):
    pyplot.scatter(i+1, acapellaHMM[i], marker='D', color='cyan', facecolors='none', s=100)
    pyplot.scatter(i+1, acapellaVTHMM[i], marker='D', color='red',  s=50)
    
    # connecting line
    pyplot.plot([i+1, i+1], [acapellaHMM[i], acapellaVTHMM[i]],  linestyle='dotted', color='black'  )


# put only last dot again. because of labeling
pyplot.scatter(i+1, acapellaHMM[i], marker='D', color='cyan', facecolors='none', s=100, label='HMM a cappella')
pyplot.scatter(i+1, acapellaVTHMM[i], marker='D', color='red', s=50, label='VTHMM a cappella')

pyplot.xlabel('Recording', fontsize=28)
pyplot.ylabel('Alignment accuracy (%)', fontsize=28)

pyplot.tick_params(axis='both', which='major', labelsize=20)
# pyplot.xlim([78,96])
# pyplot.ylim([50,100])

ax = pyplot.gca()
ax.yaxis.grid(True)

ax.legend(loc=3, fontsize=25)
fig1.savefig('/Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/ISMIR_noteOnsets/scatterPlotCorrelation.png')