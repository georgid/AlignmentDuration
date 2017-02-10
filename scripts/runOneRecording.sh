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
COMPOSITION=muhayyerkurdi--sarki--duyek--ruzgar_soyluyor--sekip_ayhan_ozisik/
TEST_DATA_SYNTH=$HOME_DTIC/turkish-makam-lyrics-2-audio-test-data-synthesis

#no synthesis
# $HOME_DTIC/env/bin/python AlignmentDuration/doitOneRecording.py $HOME_DTIC/turkish-makam-lyrics-2-audio-test-data/segah--sarki--curcuna--olmaz_ilac--haci_arif_bey/  $HOME_DTIC/ISTANBUL/guelen/ 01_Olmaz_
/Users/joro/Documents/Phd/UPF/turkish-makam-lyrics-2-audio-test-data-synthesis/nihavent--sarki--duyek--bir_ihtimal--osman_nihat_akin/  /Users/joro/Documents/Phd/UPF/adaptation_data_soloVoice/ISTANBUL/idil/ 05_Semahat_Ozdenses_-_Bir_Ihtimal_Daha_Var_ True False 0.97 False 2

# with Synthesis
$HOME_DTIC/env/bin/python AlignmentDuration/doitOneRecording.py $TEST_DATA_SYNTH/$COMPOSITION $TEST_DATA_SYNTH/$COMPOSITION/1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde 1-05_Ruzgar_Soyluyor_Simdi_O_Yerlerde_ True 0.97 True 2