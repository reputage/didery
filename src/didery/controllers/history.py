import falcon
import arrow
import time

try:
    import simplejson as json
except ImportError:
    import json

from ..help import helping
from ..did.didering import Did, getDIDModel
from ..db import dbing as db
from ..controllers.validation import factory
from ..models.models import BasicHistoryModel


def validate(req, resp, resource, params):
    """
    Validate incoming requests and prepare
    body of request for processing.

    :param req: falcon.Request object
    :param resp: falcon.Response object
    :param resource: History controller object
    :param params: (dict) URI Template field names
    """
    validator = factory.historyFactory(resource.mode, req, params) 
    validator.validate()


class History:
    def __init__(self, store=None, mode=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store
        self.mode = mode

    @falcon.before(helping.parseQString)
    def on_get(self, req, resp, did=None):
        """
        Handle and respond to incoming GET request.
        :param req: Request object
        :param resp: Response object
        :param did: string
            URL parameter specifying a rotation history
        """
        offset = req.offset
        limit = req.limit

        count = db.historyDB.historyCount()

        if did is not None:
            body = db.historyDB.getHistory(did)
            if body is None:
                raise falcon.HTTPError(falcon.HTTP_404)
            body = body.data
        else:
            if offset >= count:
                resp.body = json.dumps({}, ensure_ascii=False)
                return

            body = db.historyDB.getAllHistories(offset, limit)

            resp.append_header('X-Total-Count', count)

        resp.body = json.dumps(body, ensure_ascii=False)

    @falcon.before(validate)
    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        request_json = BasicHistoryModel(req.body)
        sigs = req.signatures
        did = request_json.id

        # TODO: review signature validation for any holes
        response_json = db.historyDB.saveHistory(did, request_json.data, sigs)
        db.eventsDB.saveEvent(did, request_json.data, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)
        resp.status = falcon.HTTP_201

    @falcon.before(validate)
    def on_put(self, req, resp, did):
        """
            Handle and respond to incoming PUT request.
            :param req: Request object
            :param resp: Response object
            :param did: decentralized identifier
        """
        request_data = BasicHistoryModel(req.body)
        sigs = req.signatures

        # TODO: review signature validation for any holes
        response_json = db.historyDB.saveHistory(did, request_data.data, sigs)
        db.eventsDB.saveEvent(did, request_data.data, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)

    @falcon.before(validate)
    def on_delete(self, req, resp, did):
        """
            Handle and respond to incoming PUT request.
            :param req: Request object
            :param resp: Response object
            :param did: decentralized identifier
        """
        vk = req.body["vk"]

        if self.mode == "method":
            did_class = getDIDModel(did)
            if did_class is not None:  # Test id-string Resolver exists
                did_obj = did_class(did)

                if did_obj.match_vk(vk):
                    vk = None  # Delete all data

        success = db.historyDB.deleteHistory(did, vk)
        db.eventsDB.deleteEvent(did, vk)

        if success is None:
            raise falcon.HTTPError(falcon.HTTP_409,
                                   'Deletion Error',
                                   'Error while attempting to delete the resource.')

        success = success if isinstance(success, list) else [success]

        resp.body = json.dumps({"deleted": success}, ensure_ascii=False)


class HistoryStream:
    def __init__(self, store=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store
        self.id = 0
        self.history = None

    def historyGenerator(self, did=None):
        if did is None:
            count = db.historyDB.historyCount()
            if self.history == count:
                time.sleep(2)
            else:
                self.history = count
                history = db.historyDB.getAllHistories(limit=self.history)
                temp = []
                for entry in history['data']:
                    temp.append(json.loads(entry.decode('utf-8')))

                history = {"data": temp}
                yield bytes("\nid:" + str(self.id) + "\nevent:message\ndata:" + str(history) + "\n\n", "ascii")
                self.id += 1
                time.sleep(2)

        else:
            value = db.historyDB.getHistory(did)
            if value is None:
                raise falcon.HTTPError(falcon.HTTP_404)

            if self.history == value:
                time.sleep(2)
            else:
                self.history = value
                print(self.history)
                yield bytes("\nid:" + str(self.id) + "\nevent:message\ndata:" + str(self.history) + "\n\n", "ascii")
                self.id += 1
                time.sleep(2)

    def on_get(self, req, resp, did=None):
        resp.status = falcon.HTTP_200
        resp.content_type = "text/event-stream"
        resp.stream = self.historyGenerator(did)
