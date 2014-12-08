#!/bin/bash
#$ -q default.q
#$ -pe smp 8
#$ -l s_vmem=8G
#$ -l h_vmem=10G
#$ -m bea
#$ -M georgi.dzhambazov@upf.edu
#$ -e OneRecParamsError.out
#$ -o OneRecParamsOutput.out
#$ -cwd
#$ -N doitOneRecParams

# A SCRIPT THAT RUNS on HPC

module load python/2.7.5
echo "python after loading module: "
which python
source /homedtic/georgid/env/bin/activate
echo "python after loading vrit env: "
which python


HOME_DTIC=/homedtic/georgid/

$HOME_DTIC/env/bin/python AlignmentDuration/doitOneRecordingParams.py $HOME_DTIC/turkish-makam-lyrics-2-audio-test-data/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/  $HOME_DTIC/ISTANBUL/guelen/ 01_Olmaz_
