

#!/bin/bash
#$ -q default.q
#$ -pe smp 8
#$ -l s_vmem=8G
#$ -l h_vmem=10G
#$ -m bea
#$ -M georgi.dzhambazov@upf.edu
#$ -e allRecordingsParamsError.out
#$ -o allRecordingsParamsOutput.out
#$ -cwd
#$ -N allRecordingsParams

# A SCRIPT THAT RUNS on HPC
# Copyright (C) 2014-2018  Music Technology Group - Universitat Pompeu Fabra
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


module load python/2.7.5
echo "python after loading module: "
which python
source /homedtic/georgid/env/bin/activate
echo "python after loading vrit env: "
which python


HOME_DTIC=/homedtic/georgid/

$HOME_DTIC/env/bin/python AlignmentDuration/doitAllRecParams.py /homedtic/georgid/turkish-makam-lyrics-2-audio-test-data/  /homedtic/georgid/ISTANBUL/ False True


# $HOME_DTIC/env/bin/python AlignmentDuration/doitOneRecording.py   $HOME_DTIC/turkish-makam-lyrics-2-audio-test-data/nihavent--sarki--aksak--gel_guzelim--faiz_kapanci/ $HOME_DTIC/ISTANBUL/barbaros/ 02_Gel True
