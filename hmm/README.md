HMM
===

A numpy/python-only Hidden Markov Models framework. No other dependencies are required.

This implementation (like many others) is based on the paper:
"A Tutorial on Hidden Markov Models and Selected Applications in Speech Recognition, LR RABINER 1989"

Major supported features:

* Discrete HMMs
* Continuous HMMs - Gaussian Mixtures
* Supports a variable number of features
* Easily extendable with other types of probablistic models (simply override the PDF. Refer to 'GMHMM.py' for more information)
* Non-linear weighing functions - can be useful when working with a time-series

Open concerns:
* Examples are somewhat out-dated
* Convergence isn't guaranteed when using certain weighing functions
-----------------------------------


Duration-model extension : done by georgi.dzhambazov@upf.edu
=========================

* fixed underflow due to multiplication of probabilities ( handled by sum log(probs) )

* posteriors of GMM mixtures are computed using scikit learn 

* added oracle test: Oracle test allow to check if model is able to perform perfect alignment on ground truth timestamps of phonemes (e.g. replace observation posteriors with 1-s from ground truth) (described more here: http://www.terasoft.com.tw/conf/ismir2014/proceedings/T050_126_Paper.pdf ) 
hmm.examples.tests.test_oracle() - needs phoneme-level annotation

Algorithm parameters can be changed from class hmm.ParametersAlgo 

TODO: 
use _ContinuousHMM.usePersistentProbs to store persistently <fileName>.durationsMap to save time Now computed each time