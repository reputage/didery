"""
DID package

DID helpers

"""
from __future__ import generator_stop

import importlib

_modules = ['didering']

for m in _modules:
    importlib.import_module(".{0}".format(m), package='didery.did')
