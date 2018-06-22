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
Created on Jan 13, 2016

@author: joro
'''
from FeatureExtractor import loadMFCCs

def test_loadMFCCs():
    URI_noExt =   '/Users/joro/Documents/Phd/UPF/arias/laosheng-erhuang_04'
    withSynthesis = True
    loadMFCCs(URI_noExt, withSynthesis, 55, 58)


def test_htkmfcRead():
    URI_file = '/Users/joro/Documents/Phd/UPF/arias/laosheng-erhuang_04_0_2.mfc'
    HTKFeat_reader =  open(URI_file, 'rb')
    features = HTKFeat_reader.getall()
    print features.shape
    
if __name__ == '__main__':
    test_loadMFCCs()