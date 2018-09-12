import falcon

try:
    import simplejson as json
except ImportError:
    import json

from didery.routing import *