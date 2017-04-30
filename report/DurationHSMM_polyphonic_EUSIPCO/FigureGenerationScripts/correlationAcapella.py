
scoreDev  = [0.35, 
0.45, 
0.56, 
0.63, 
0.65, 
0.83, 
0.91, 
1.01, 
1.33]

noDurationError = [

0.64,
0.41,
0.93,
1.83,
0.94,
2.17,
1.09,
0.78,
1.49


]

durationError =  [
0.26,
0.47,
0.63,
0.45,
0.78,
0.92,
0.81,
1.1,
1.9
]

import scipy.stats
correlationA = scipy.stats.spearmanr(durationErrorAcapella, durationError)

