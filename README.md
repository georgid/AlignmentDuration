[![Build Status](https://travis-ci.org/georgid/AlignmentDuration.svg?branch=noteOnsets)](https://travis-ci.org/georgid/AlignmentDuration)

AlignmentDuration
======

Tool for Aligning lyrics to audio automatically using a phonetic recognizer with Hidden Markov Models. The Viterbi Decoding with explicit durations of reference syllables can be toggled on with the parameter [WITH_DURATIONS](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L36)

Built from scratch. Alternatively one can use this tool as a wrapper around  [htk](http://htk.eng.cam.ac.uk/download.shtml) (may be faster) by setting the parameter [DECODE_WITH_HTK](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L47) 

If you are using this work please cite http://mtg.upf.edu/node/3751
  

NOTE: A version building upon this research is built by [Voice Magix](http://www.voicemagix.com). It features 
- latest deep-learning enabled acoustic model
- English language lyrics parser and normalizer
- runtime speed optimization 
- option to run on recordings with diverse types of background instruments
- reduced external package dependencies 

If interested in using it write to info at voicemagix dot com

### Folder Structure
- example: example/test sound and annotation files 
- scripts: help scripts for running the code (including on [hpc cluster](https://www.upf.edu/en/web/etic/hpc) )
- src: main source code
	- align: main alignment logic
	- hmm: hidden Markov model alignment
	- for_makam: Makam-specific logic (see music traditions below)
	- models_makam: acoustic model for Turkish
	- models_jingju: acoustic model for Jingju Mandarin
	- for_jingju: jingju-specific logic (see music traditions below)
	- onsets: logic for note-onset-aware alignment (ISMIR 2016)
	- parse: logic for parsing lyrics files
	- smstools: modifications to the https://github.com/MTG/sms-tools
	- utilsLyrics: any utility scripts
- test: test scripts (scould be used in CI)
- thrash: code that has to be reviewed and deleted, left for the sake of completeness  

### LICENSE
Copyright 2014-2017  Music Technology Group - Universitat Pompeu Fabra

AlignmentDuration is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation (FSF), either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see http://www.gnu.org/licenses/

For more details see COPYING.txt


BUILD INSTRUCTIONS
----------------------------------- 
NOTE: python3 is not supported and tested

`git clone https://github.com/georgid/AlignmentDuration.git;
sudo apt-get install python-dev python-setuptools python-numpy`

`pip install -r requirements;
python setup.py install`


* [essentia](http://essentia.upf.edu/). 


* [pdnn](https://www.cs.cmu.edu/~ymiao/pdnntk.html)
needed if [OBS_MODEL is MLP or MLP_fuzzy](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L26)

`cd ..;
git clone https://github.com/yajiemiao/pdnn`

install also [Theano](http://www.cs.cmu.edu/~ymiao/pdnntk.html)


* install [htk](http://htk.eng.cam.ac.uk/download.shtml)
needed if either [MFCC_HTK](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L49)
or [DECODE_WITH_HTK](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L47) is set to 1


* htkModelParser 
needed if [on Turkish makam](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L24) and
[OBS_MODEL is GMM](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L26)

`git clone https://github.com/georgid/htkModelParser.git;
cd htkModelParser;
sudo pip install -r requirements;
python setup.py install`



* sci-kit-learn (branch with fixed underflow issues)
needed if [on Turkish makam](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L24) and
[OBS_MODEL is GMM](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L26)

`git clone https://github.com/georgid/scikit-learn;
sudo apt-get install python-scipy;
python setup.py install`


* git clone https://github.com/georgid/makam_acapella
needed if using [MLP_fuzzy model](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L28) 


* Evaluation (optional if evaluation of accuracy needed) 
<put in parent directory of AlignmentDuration>

`cd ..;
git clone https://github.com/georgid/AlignmentEvaluation.git`


### Citation
Georgi Dzhambazov, Knowledge-based Probabilistic Modeling for Tracking Lyrics in Music Audio Signals, PhD thesis
[thesis materials companion page](compmusic.upf.edu/phd-thesis-georgi)


USAGE on different music traditions
-------------------------------------------------------

### jingju (Beijing Opera) : Chinese
`python AlignmentDuration/jingju/runWithParamsAll.py 2 0   /JingjuSingingAnnotation-master/lyrics2audio/results/3folds/ 3 0`

to test: 
`python AlignmentDuration/test/testLyricsAlign.py`

with method [testLyricsAlign_mandarin_pop](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/test/testLyricsAlign.py#L97)


### Turkish Makam music: Turkish
You need to provide the [musicbrainz ID](https://musicbrainz.org/) (MBID) of the recording. This requirement could be removed on demand...

#### call as a method from an aggregator API:
`install https://github.com/MTG/pycompmusic;
python pycompmusic/compmusic/extractors/makam/lyricsalign.py`

or locally:

`python https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/for_makam/lyricalign_local.py`

to test: 
`python AlignmentDuration/test/testLyricsAlign.py`

with method [testLyricsAlignMakam](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/test/testLyricsAlign.py#L51)


### English 

Write to georgi.dzhambazov at upf dot edu or info at voicemagix dot com if you would like to use the English 
language model. It is not included here for licensing issues. 

## Evaluation
Use [evalAccuracy](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/LyricsAligner.py#L195) script. 100 means perfect alignment. Usually values above 80% are acceptably well for human listeners.

The default evaluation level is set at [word boundaries](https://github.com/georgid/AlignmentDuration/blob/noteOnsets/src/align/ParametersAlgo.py#L30)




 
 
BUILD INSTRUCTIONS ON server kora.s.upf.edu
-------------------------------

git clone https://github.com/georgid/AlignmentDuration.git
git checkout for_pycompmusic

cd /homedtic/georgid/test2/AlignmentDuration
source /homedtic/georgid/env/bin/activate 
python setup.py install

to test:
python /homedtic/georgid/test2/AlignmentDuration/test/testLyricsAlign.py

on server:
git pull https://github.com/MTG/pycompmusic
/srv/dunya/env/src/pycompmusic/compmusic/extractors/makam/lyricsalign.py
with recording MB-ID: 727cff89-392f-4d15-926d-63b2697d7f3f 
