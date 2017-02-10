cd /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentDuration/
cd /Users/joro/Documents/Phd/UPF/voxforge/myScripts/AlignmentEvaluation/
cd /Users/joro/Documents/Phd/UPF/voxforge/myScripts/utilsLyrics
cd /Users/joro/Documents/Phd/UPF/voxforge/myScripts/HMMDuration/

# add files manually if there are deletions or additioons
git add Decoder.py;
git add hmm/continuous/_DurationHMM.py


git commit -a -m "mc"; git push -u origin master
git commit -m "mc"; git push -u origin master
