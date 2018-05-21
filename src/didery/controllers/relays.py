import falcon
try:
    import simplejson as json
except ImportError:
    import json

from ..help import helping


tempDB = []


def basicValidation(req, resp, resource, params):
    """
    Validate incoming POST request and prepare
    body of request for processing.
    :param req: Request object
    """

    helping.parseReqBody(req)
    body = req.body

    required = ["host_address", "port", "name", "changed"]
    helping.validateRequiredFields(required, body)

    if body['host_address'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'host_address field cannot be empty.')

    if body['port'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'port field cannot be empty.')

    if body['name'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'name field cannot be empty.')

    if body['changed'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'changed field cannot be empty.')

    if 'main' in body:
        if body['main'] == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'main field cannot be empty.')

        if type(body['main']) != bool:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'main field must be a boolean value.')

    try:
        body['port'] = int(body['port'])
    except ValueError:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'port field must be a number.')

    if body['port'] < 1 or body['port'] > 65535:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'port field must be a number between 1 and 65535.')


def validatePost(req, resp, resource, params):
    basicValidation(req, resp, resource, params)

    if 'uid' in req.body:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'If uid is known use PUT.')


def validatePut(req, resp, resource, params):
    basicValidation(req, resp, resource, params)

    if "uid" not in params:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'uid required in url.')

    try:
        params['uid'] = int(params['uid'])
    except ValueError:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'uid in url must be a number.')

    if "uid" not in req.body or req.body['uid'] == "":
        req.body['uid'] = params['uid']
    else:
        try:
            req.body['uid'] = int(req.body['uid'])
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'uid field must be a number.')

    if params['uid'] != req.body['uid']:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'uid in url must match uid in body.')


def validateDelete(req, resp, resource, params):
    if "uid" not in params:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'uid required in url.')


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
                "status": "connected",
                "changed" : "2000-01-01T00:00:00+00:00"
            },
            "2": {
                "host address": "127.0.0.1",
                "port": 7542,
                "name": "beta",
                "main": False,
                "uid": "2",
                "status": "connected",
                "changed": "2000-01-01T00:00:00+00:00"
            }
        }

        resp.body = json.dumps(body, ensure_ascii=False)

    """
    For manual testing of the endpoint:
        http POST localhost:8000/relay host_address="127.0.0.1" port=7541 name="alpha" main=true
    """
    @falcon.before(basicValidation)
    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        result_json = req.body

        result_json["uid"] = len(tempDB)
        result_json["status"] = "connected"

        tempDB.append(result_json)

        resp.body = json.dumps(result_json, ensure_ascii=False)
        resp.status = falcon.HTTP_201

    """
    For manual testing of the endpoint:
        http PUT localhost:8000/relay/1 host_address="127.0.0.1" port=7541 name="alpha" main=true
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
            "status": "disconnected",
            "changed": "2000-01-01T00:00:00+00:00"
        }

        resp.body = json.dumps(body, ensure_ascii=False)
