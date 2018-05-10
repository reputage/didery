"""
controllers package

rest endpoints

"""
from __future__ import generator_stop

import importlib

_modules = ['errors', 'history', 'otp_blob', 'relays']

for m in _modules:
    importlib.import_module(".{0}".format(m), package='didery.controllers')
