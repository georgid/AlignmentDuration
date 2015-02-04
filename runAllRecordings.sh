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

module load python/2.7.5
echo "python after loading module: "
which python
source /homedtic/georgid/env/bin/activate
echo "python after loading vrit env: "
which python


HOME_DTIC=/homedtic/georgid/


$HOME_DTIC/env/bin/python AlignmentDuration/doitAllRecordings.py /homedtic/georgid/turkish-makam-lyrics-2-audio-test-data-synthesis/  /homedtic/georgid/ISTANBUL/ True 0.97 False 1 False
#$HOME_DTIC/env/bin/python AlignmentDuration/doitAllRecordings.py $HOME_DTIC//turkish-makam-lyrics-2-audio-test-data-synthesis/ $HOME_DTIC//turkish-makam-lyrics-2-audio-test-data-synthesis/ True 0.97 False 1 True
