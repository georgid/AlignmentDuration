'''
Created on May 22, 2015

@author: joro
'''
import numpy

def areArraysEqual(B_map, B_mapSciKit):
    print "abs diff"
    arr = abs(B_map  - B_mapSciKit)
    print numpy.max(abs(B_map  - B_mapSciKit))
    
    # print vallues of top 10 most different values 

    indices = arr.ravel().argsort()[-10:]
    indices = (numpy.unravel_index(i, arr.shape) for i in indices)
    print [(B_map[i], B_mapSciKit[i], i) for i in indices]
    
    # compare with assertion exception
    try:
        res = numpy.testing.assert_array_almost_equal_nulp(B_map, B_mapSciKit, 10)
        
    except Exception:
        print res