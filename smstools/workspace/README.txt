workspace/harmonicModel_function has the main logic

-extractHarmSpec()
sets params for extarction and loads pitchSeries
for now it is hard coded to work with one particular audio.
TODO: load stereo as mono with MonoLoader
	
-resynthesize()


software.models.harmonicModel.harmonicModelAnal_2()
extracts harm elements from the spectrum (based on main melody provided)

software.models.harmonicModel.harmonicDetection()
 	when f0 detected but no peaks above threshold => return zero harmonics
 	
 -------------------------------------------------------
 mainLobeMatcher
 
  implements a technique of compariong shape of peaks to mainLobe of a window:
  	NOTE: works only with blackman-harris window; size of window hardcoded
 
 see V. Rao and P. Rao - Vocal melody extraction in the presence of pitched accompaniment in polyphonic music, II.B
 
 code in workspace/mainLobeMatcher
 
 !!!!! we changed from db to absolute loudness scale: 
 mX = 20 * np.log10(absX) in /software/models/dftModel.py in function dftAnal()
 make sure it is db. otherwise synthesis does not work well.