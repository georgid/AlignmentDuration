# Copyright (C) 2014-2018  Music Technology Group - Universitat Pompeu Fabra
#
# This file is part of AlignmentDuration:  tool for Lyrics-to-audio alignment with syllable duration modeling
# and is modified from https://github.com/MTG/sms-tools

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


'''
Created on Nov 27, 2016

@author: georgid
'''
__all__ = []

import pkgutil
import inspect

# for loader, name, is_pkg in pkgutil.walk_packages(__path__):
#     if name.startswith( 'for_jingju') or  name.startswith( 'hmm.examples.tests'):
#         continue
#     module = loader.find_module(name).load_module(name)
# 
#     for name, value in inspect.getmembers(module):
#         if name.startswith('__'):
#             continue
# 
#         globals()[name] = value
#         __all__.append(name)