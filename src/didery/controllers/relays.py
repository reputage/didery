import falcon
try:
    import simplejson as json
except ImportError:
    import json

from ..help import helping


def validatePost(req, resp, resource, params):
    """
    Validate incoming POST request and prepare
    body of request for processing.
    :param req: Request object
    """

    helping.parseReqBody(req)
    body = req.body

    required = ["host_address", "port", "name"]
    helping.validateRequiredFields(required, body)

    if body['host_address'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'host_address field cannot be empty.')

    if body['port'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'port field cannot be empty.')

    if body['name'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'name field cannot be empty.')

    if 'main' in body:
        if body['main'] == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Malformed Field',
                                   'main field cannot be empty.')

        if type(body['main']) != bool:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Malformed Field',
                                   'main field must be a boolean value.')

    if 'auto' in body:
        if body['auto'] == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Malformed Field',
                                   'auto field cannot be empty.')

        if type(body['auto']) != bool:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Malformed Field',
                                   'auto field must be a boolean value.')

    try:
        int(body['port'])
    except ValueError:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'port field must be a number.')

    if int(body['port']) < 1 or int(body['port']) > 65535:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'port field must be a number between 1 and 65535.')


def validatePut(req, resp, resource, params):
    validatePost(req, resp, resource, params)

    if "uid" not in params:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Incomplete Request',
                               'uid required.')


def validateDelete(req, resp, resource, params):
    if "uid" not in params:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Incomplete Request',
                               'uid required.')


class Relay:
    def __init__(self, store=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store

    """
    For manual testing of the endpoint:
        http localhost:8000/relay
    """
    def on_get(self, req, resp):
        """
        Handle and respond to incoming GET request.
        :param req: Request object
        :param resp: Response object
        """
        body = {
            "1": {
                "host address": "127.0.0.1",
                "port": 7541,
                "name": "alpha",
                "main": True,
                "uid": "1",
                "auto": True,
                "status": "connected",
            },
            "2": {
                "host address": "127.0.0.1",
                "port": 7542,
                "name": "beta",
                "main": False,
                "uid": "2",
                "auto": True,
                "status": "connected",
            }
        }

        resp.body = json.dumps(body, ensure_ascii=False)

    """
    For manual testing of the endpoint:
        http POST localhost:8000/relay host_address="127.0.0.1" port=7541 name="alpha" main=true auto=true
    """
    @falcon.before(validatePost)
    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        result_json = req.body

        result_json["uid"] = "1"
        result_json["status"] = "connected"

        resp.body = json.dumps(result_json, ensure_ascii=False)

    """
    For manual testing of the endpoint:
        http PUT localhost:8000/relay/1 host_address="127.0.0.1" port=7541 name="alpha" main=true auto=true
    """
    @falcon.before(validatePut)
    def on_put(self, req, resp, uid):
        """
        Handle and respond to incoming PUT request.
        :param req: Request object
        :param resp: Response object
        :param uid: servers unique id
        """
        result_json = req.body

        result_json["uid"] = uid
        result_json["status"] = "connected"

        resp.body = json.dumps(result_json, ensure_ascii=False)

    """
    For manual testing of the endpoint:
        http DELETE localhost:8000/relay/10
    """
    @falcon.before(validateDelete)
    def on_delete(self, req, resp, uid):
        """
        Handle and respond to incoming DELETE request.
        :param req: Request object
        :param resp: Response object
        :param uid: servers unique id
        """
        body = {
            "host_address": "127.0.0.1",
            "port": 7541,
            "name": "alpha",
            "main": True,
            "uid": uid,
            "auto": True,
            "status": "disconnected",
        }

        resp.body = json.dumps(body, ensure_ascii=False)
