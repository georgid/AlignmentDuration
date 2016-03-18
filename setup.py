'''
Created on Jan 15, 2016

@author: joro
'''

#!/usr/bin/env python

from setuptools import setup, find_packages
from setuptools import Extension
import os
import numpy as np




try:
   from distutils.command.build_py import build_py_2to3 \
       as build_py
except ImportError:
   from distutils.command.build_py import build_py
   
from Cython.Distutils import build_ext
   

# py_inc = [get_python_inc()]
# 
# np_lib = os.path.dirname(numpy.__file__)
# np_inc = [os.path.join(np_lib, 'core/include')]
# ext_inc = os

pathSmsTools = 'smstools/software/models/utilFunctions_C/'
sourcefiles = [pathSmsTools + 'utilFunctions.c', pathSmsTools + 'cutilFunctions.pyx']
ext_modules = [Extension("smstools.software.models.utilFunctions_C",
            sourcefiles,
            libraries=['m'],
            include_dirs=[np.get_include()]
            )]

generalDependencies = ['setuptools-git', 'numpy', 'cython']
# dependencies of hmm package dir
hmmDependencies = ['scipy', 'matplotlib']
generalDependencies.extend(hmmDependencies)

setup(name='lyrics-align',
      version='0.1',
      description='alignment of lyrics using duration modeling',
      author='Georgi Dzhambazov',
      url='',
      # packages=['align', 'align.model' ,'hmm', 'hmm.continuous',  'test']
    packages=find_packages(),
    package_data={'align': ['model/hmmdefs9gmm9iter']},
    include_package_data=True,
    install_requires=generalDependencies,
    
    # cython dependencies
    cmdclass = {'build_ext': build_ext},
    ext_modules=ext_modules

)