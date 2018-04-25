import falcon

try:
    import simplejson as json
except ImportError:
    import json

from ioflo.aid import getConsole
from ioflo.aid import odict
from ioflo.aio.http import Valet
from ioflo.base import doify