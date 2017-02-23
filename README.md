Copyright � 2015,2016  Music Technology Group - Universitat Pompeu Fabra

NAME: AlignmentDuration

DESCRIPTION 
 tool for Aligning lyrics to audio automatically using Hidden Markov Models with Explicit Duration

LICENSE:
AlignmentDuration is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation (FSF), either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more details.

You should have received a copy of the GNU General Public License along with this program.  If not, see http://www.gnu.org/licenses/



BUILD INSTRUCTIONS: 

git clone https://github.com/georgid/AlignmentDuration.git
cd AlignmentDuration
git checkout for_pycompmusic

sudo apt-get install python-dev python-setuptools python-numpy

pip install -r requirements
python setup.py install


* htkModelParser 
git clone https://github.com/georgid/htkModelParser.git
cd htkModelParser
sudo pip install -r requirements
python setup.py install


* sci-kit-learn (branch with fixed underflow issues)
git clone https://github.com/georgid/scikit-learn 
cd scikit-learn
sudo apt-get install python-scipy
python setup.py install



How to Run on KORA
-------------------------------

ssh georgid@kora.s.upf.edu

cd /homedtic/georgid/test2/AlignmentDuration
source /homedtic/georgid/env/bin/activate 
python setup.py install
(dependencies already installed in this python virtual env)

to test:
make sure to adjust path to HCopy
https://github.com/MTG/pycompmusic/blob/master/compmusic/extractors/makam/lyricsalign.py#L61

python /homedtic/georgid/test2/AlignmentDuration/test/testLyricsAlign.py



How to run on on server
-------------------------------

git pull https://github.com/MTG/pycompmusic
/srv/dunya/env/src/pycompmusic/compmusic/extractors/makam/lyricsalign.py
with recording MB-ID: 727cff89-392f-4d15-926d-63b2697d7f3f 



 


-----
* Evaluation (optional if model evaluation step needed, see Doit.py ) 
<put in parent direcoty of AlignmentDuration>
cd ..
git clone https://github.com/georgid/AlignmentEvaluation.git


* HMM (optional if approach with no-duration modeling needed)
https://github.com/MTG/HMM.git


-------------------------------------------------------
USAGE (jingju):
python AlignmentDuration/jingju/runWithParamsAll.py 2 0   /JingjuSingingAnnotation-master/lyrics2audio/results/3folds/ 3 0


USAGE (makam):
pycompmusic/compmusic/extractors/makam/lyricsalign.py

to test without pycommusic: 
python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/test/testLyricsAlign.py


------------------------------------------

all from here is DEPRACATED: 
EXAMPLE: doitOneChunk()
python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/doitOneChunk.py /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin/ /Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/idil/05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var_0_zemin_from_69_5205_to_84_2 True False 0.97 False 2

# with re-synthesized audio
python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/doitOneChunk.py /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses/  /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses/06_Semahat_Ozdenses_-_Aksam_Oldu_Huzunlendim/06_Semahat_Ozdenses_-_Aksam_Oldu_Huzunlendim_1_zemin_from_62_393939_to_77_827796 False 0.97 False 2

python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/doitOneChunk.py /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik_short/  /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik_short/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde_2_zemin_from_16_459_to_38_756510 True 0.97 False 2

EXAMPLE: doitOneRecording() 
# with re-synthesized audio
python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/doitOneRecording.py  /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses/ /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis//ussak--sarki--duyek--aksam_oldu_huzunlendim--semahat_ozdenses/06_Semahat_Ozdenses_-_Aksam_Oldu_Huzunlendim/ 06_Semahat_Ozdenses_-_Aksam_Oldu_Huzunlendim_ True True 0.97 False 2 True

EXAMPLE: doitAllRecordings()
python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/doitAllRecordings.py /Users/joro/Documents/Phd/UPF/  False False 0.97 False 2
python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/doitAllRecordings.py /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/   /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/ False True 0.97 False 2

# with synthesized audio
python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/doitAllRecordings.py /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/   /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/ False True 0.97 False 2

(on hpc)
see runAllRecordings.sh


EXAMPLE: doitAllRecParams()
python /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/doitAllRecParams.py /Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data/  /Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/

(on hpc)
python AlignmentDuration/doitAllRecParams.py /homedtic/georgid/turkish-makam-lyrics-2-audio-test-data/  /homedtic/georgid/ISTANBUL/


loading persistent files: 
extension to load observation probabilities for all states and all observations for a given file is in 
Decoder.Decoder.decodeAudio
