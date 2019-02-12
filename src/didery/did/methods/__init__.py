"""
DID package

DID helpers

"""

import importlib

_modules = ['dad']

for m in _modules:
    importlib.import_module(".{0}".format(m), package='didery.did.methods')
