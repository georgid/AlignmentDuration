'''
Created on Jan 15, 2016

@author: joro
'''

#!/usr/bin/env python

from setuptools import setup, find_packages

setup(name='lyrics-align',
      version='0.1',
      description='alignment of lyrics using duration modeling',
      author='Georgi Dzhambazov',
      url='',
      # packages=['align', 'align.model' ,'hmm', 'hmm.continuous',  'test']
    packages=find_packages(),
    package_data={'align': ['model/hmmdefs9gmm9iter']},
    include_package_data=False,
    install_requires=['setuptools-git']

)