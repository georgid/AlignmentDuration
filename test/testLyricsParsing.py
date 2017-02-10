'''
Created on Mar 21, 2016

@author: joro
'''
from hmm.Path import Path
from docutils.parsers.rst.directives import path
from align.LyricsParsing import getBoundaryFrames


def getBoundaryFramesTest():
    
    path = Path(None, None, 'dummy', 'dummy')
    path.setPathRaw([0,0,1,1,1,3,3,5])
    path.path2stateIndices()
    countFirstState = 3
    countLastState = 4
    currWordBeginFrame, currWordEndFrame  = getBoundaryFrames(countFirstState, countLastState, path)
    
    # shoudl be 5 and 7
    print currWordBeginFrame
    print currWordEndFrame

if __name__ == '__main__':
    getBoundaryFramesTest()