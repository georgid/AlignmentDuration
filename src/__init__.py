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