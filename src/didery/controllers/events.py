import falcon
import arrow
import time
try:
    import simplejson as json
except ImportError:
    import json

from collections import OrderedDict
from ..help import helping
from .. import didering
from ..db import dbing as db

class Event:
    def __init__(self, store=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store

    #@falcon.before(helping.parseQString)
    def on_get(self, req, resp, did=None):
        """
        Handle and respond to incoming GET request.
        :param req: Request object
        :param resp: Response object
        :param did: string
            URL parameter specifying a rotation history
        """
        #offset = req.offset
        #limit = req.limit

        count = db.eventCount()

        if did is not None:
            body = db.getEvent(did)
            if body is None:
                raise falcon.HTTPError(falcon.HTTP_404)
        else:
            #if offset >= count:
                #resp.body = json.dumps({}, ensure_ascii=False)
                #return


            body = db.getAllEvents(limit=count)

            resp.append_header('X-Total-Count', count)

        resp.body = json.dumps(body, ensure_ascii=False)