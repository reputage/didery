import falcon
import arrow
import time

try:
    import simplejson as json
except ImportError:
    import json

from ..help import helping
from ..db import dbing as db
from ..controllers.validation import factory


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

    """
    For manual testing of the endpoint:
        http localhost:8000/history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=
        http localhost:8000/history
    """
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

        count = db.historyCount()

        if did is not None:
            body = db.getHistory(did)
            if body is None:
                raise falcon.HTTPError(falcon.HTTP_404)
        else:
            if offset >= count:
                resp.body = json.dumps({}, ensure_ascii=False)
                return

            body = db.getAllHistories(offset, limit)

            resp.append_header('X-Total-Count', count)

        resp.body = json.dumps(body, ensure_ascii=False)


    """
    For manual testing of the endpoint:
        http POST localhost:8000/history id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" changed="2000-01-01T00:00:00+00:00" signer=2 signers="['Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=', 'Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=', 'dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=', '3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=']"
    """
    @falcon.before(validate)
    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        result_json = req.body
        sigs = req.signatures
        did = result_json['id']

        # TODO: review signature validation for any holes
        response_json = db.saveHistory(did, result_json, sigs)
        db.saveEvent(did, result_json, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)
        resp.status = falcon.HTTP_201

    """
    For manual testing of the endpoint:
        http PUT localhost:8000/history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" changed="2000-01-01T00:00:00+00:00" signer=2 signers="['Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=', 'Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=', 'dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=', '3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=']"
    """
    @falcon.before(validate)
    def on_put(self, req, resp, did):
        """
            Handle and respond to incoming PUT request.
            :param req: Request object
            :param resp: Response object
            :param did: decentralized identifier
        """
        result_json = req.body
        sigs = req.signatures

        resource = db.getHistory(did)

        if resource is None:
            raise falcon.HTTPError(falcon.HTTP_404)

        # make sure time in changed field is greater than existing changed field
        last_changed = arrow.get(resource['history']['changed'])
        new_change = arrow.get(result_json['changed'])

        if last_changed >= new_change:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   '"changed" field not later than previous update.')

        # validate that previously rotated keys are not changed with this request
        current = resource['history']['signers']
        update = result_json['signers']

        if len(update) <= len(current):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers field is missing keys.')

        for key, val in enumerate(current):
            if update[key] != val:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers field missing previously verified keys.')

        # without these checks a hacker can skip past the validated signatures and insert their own keys
        if resource['history']['signer'] + 1 != result_json['signer']:
            if result_json['signers'][result_json['signer']] is not None:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signer field must be one greater than previous.')

        # TODO: review signature validation for any holes
        response_json = db.saveHistory(did, result_json, sigs)
        db.saveEvent(did, result_json, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)

    @falcon.before(validate)
    def on_delete(self, req, resp, did):
        """
            Handle and respond to incoming PUT request.
            :param req: Request object
            :param resp: Response object
            :param did: decentralized identifier
        """
        resource = req.history

        success = db.deleteHistory(did)
        db.deleteEvent(did)

        if not success:
            raise falcon.HTTPError(falcon.HTTP_500,
                                   'Deletion Error',
                                   'Error while attempting to delete the resource.')

        resp.body = json.dumps({"deleted": resource}, ensure_ascii=False)


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
            count = db.historyCount()
            if self.history == count:
                time.sleep(2)
            else:
                self.history = count
                history = db.getAllHistories(limit=self.history)
                temp = []
                for entry in history['data']:
                    temp.append(json.loads(entry.decode('utf-8')))

                history = {"data": temp}
                yield bytes("\nid:" + str(self.id) + "\nevent:message\ndata:" + str(history) + "\n\n", "ascii")
                self.id += 1
                time.sleep(2)

        else:
            value = db.getHistory(did)
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
