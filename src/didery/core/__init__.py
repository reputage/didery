"""
core package

flo behaviors

"""
from __future__ import generator_stop

import importlib

_modules = ['resting', ]

for m in _modules:
    importlib.import_module(".{0}".format(m), package='didery.core')
