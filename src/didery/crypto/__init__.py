"""
controllers package

rest endpoints

"""
from __future__ import generator_stop

import importlib

_modules = ['eddsa', 'ecdsa']

for m in _modules:
    importlib.import_module(".{0}".format(m), package='didery.crypto')
