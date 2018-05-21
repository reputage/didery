import falcon
import uuid
import itertools
import arrow

try:
    import simplejson as json
except ImportError:
    import json

from ..help import helping


tempDB = {}


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

    if "uid" not in req.body or req.body['uid'] == "":
        req.body['uid'] = params['uid']

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
    @falcon.before(helping.parseQString)
    def on_get(self, req, resp):
        """
        Handle and respond to incoming GET request.
        :param req: Request object
        :param resp: Response object
        """
        offset = req.offset
        limit = req.limit

        if offset >= len(tempDB):
            resp.body = json.dumps({}, ensure_ascii=False)
            return

        body = dict(itertools.islice(tempDB.items(), offset, offset+limit))

        resp.append_header('X-Total-Count', len(tempDB))
        resp.body = json.dumps(body, ensure_ascii=False)

    """
    For manual testing of the endpoint:
        http POST localhost:8000/relay host_address="127.0.0.1" port=7541 name="alpha" main=true
    """
    @falcon.before(validatePost)
    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        uid = uuid.uuid4().hex
        result_json = req.body

        if 'main' not in result_json:
            result_json['main'] = False

        result_json["uid"] = uid
        result_json["status"] = "connected"

        tempDB[uid] = result_json

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

        if uid not in tempDB:
            raise falcon.HTTPError(falcon.HTTP_404)

        resource = tempDB[uid]

        cdt = arrow.get(resource['changed'])
        udt = arrow.get(result_json['changed'])

        if cdt >= udt:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   '"changed" field not later than previous update.')

        resource['host_address'] = result_json['host_address']
        resource['port'] = result_json['port']
        resource['name'] = result_json['name']
        resource['changed'] = result_json['changed']

        if 'main' in result_json:
            resource['main'] = result_json['main']

        tempDB[uid] = resource

        resp.body = json.dumps(resource, ensure_ascii=False)

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
        if uid not in tempDB:
            raise falcon.HTTPError(falcon.HTTP_404)

        del tempDB[uid]
