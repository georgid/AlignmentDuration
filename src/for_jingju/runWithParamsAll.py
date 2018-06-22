# Copyright (C) 2014-2017  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling

#
# AlignmentDuration is free software: you can redistribute it and/or modify it under
# the terms of the GNU Affero General Public License as published by the Free
# Software Foundation (FSF), either version 3 of the License, or (at your
# option) any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
# details.
#
# You should have received a copy of the Affero GNU General Public License
# version 3 along with this program. If not, see http://www.gnu.org/licenses/


'''
Created on Dec 3, 2015

@author: joro
'''
import sys
import os
from runWithParams import runWithParameters
from align.ParametersAlgo import ParametersAlgo

def runWithParametersAll(argv):
    
    if len(argv) != 6:
            print ("Tool to get alignment accuracy of of one for_jingju aria with different parameters ")
            print ("usage: {}    <deviation_INSeconds> <withVocalPrediciton> <pathToData> <numFolds> <withRefSyllDurations=0/1>".format(argv[0]) )
            sys.exit()

    pathAudio = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat/'
    pathAudio = '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/'
    pathAudio = argv[3]
    
    numFolds = argv[4]
    if int(numFolds) != 15 and int(numFolds) != 3:
        sys.exit(" number of folds specified is {} . implemented only 3 and 15 folds.".format(numFolds )) 
    
    parentDir = os.path.abspath(os.path.join(os.path.dirname(os.path.realpath(__file__) ), os.path.pardir)) 

    ParametersAlgo.MODELS_DIR = os.path.join(parentDir, 'models_jingju/' + numFolds + 'folds/')
    from utilsLyrics.Utilz import findFilesByExtension
    ParametersAlgo.POLYPHONIC = 0
    
    withRefSyllDurations = argv[5]
    
    
    correctDurationHTK = 0
    totalDurationHTK = 0
    
    correctDurationOracle = 0
    totalDurationOracle = 0
    
    correctDuration = 0
    totalDuration = 0
    
    
    for currFold in range(int(numFolds)):
        pathFold = os.path.join(pathAudio,'fold' + str(currFold + 1) + '/' )
        URiREcordings = findFilesByExtension(pathFold, 'wav')
        if len(URiREcordings) == 0:
            sys.exit("pathAudio {} has no wav recordings".format(pathFold))
        for URiREcording in URiREcordings:
            URiREcording = os.path.splitext(URiREcording)[0] 
            print "working on " + URiREcording
             
            a, b, c, d, e, f = runWithParameters( ["dummy", URiREcording,  argv[1], withRefSyllDurations] )
             
            correctDurationHTK += a 
            totalDurationHTK += b
             
            correctDurationOracle += c
            totalDurationOracle += d
             
            correctDuration += e
            totalDuration += f
#     URiREcordings = [
#                     '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/fold2/zhuangyuanmei_daocishi.TextGrid', 
#                     '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/fold1/xixiangji_biyuntian.TextGrid',
#                     '/Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/fold1/zhuangyuanmei_tianbofu.TextGrid'
#                     ]    

            
                
    # end of loop
    print "final HTK: {:.2f}".format(correctDurationHTK / totalDurationHTK * 100)
    print "final Oracle: {:.2f}".format( correctDurationOracle / totalDurationOracle * 100) 
    print "final xampa: {:.2f}".format( correctDuration / totalDuration * 100) 


if __name__ == '__main__':
    runWithParametersAll(sys.argv)
    
#     python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/for_jingju/runWithParamsAll.py  2 0  /Users/joro/Documents/Phd/UPF/JingjuSingingAnnotation/lyrics2audio/praat_rules/3folds/ 3

#  python ~/workspace/AlignmentDuration/for_jingju/runWithParamsAll.py  2 0  ~/Documents/Jingju/JingjuSingingAnnotation-master/lyrics2audio/praat_rules/3folds/ 3
