import falcon
try:
    import simplejson as json
except ImportError:
    import json


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
    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   'Error reading request body.')

        try:
            result_json = json.loads(raw_json, encoding='utf-8')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect.')

        result_json["uid"] = "1"
        result_json["status"] = "connected"

        resp.body = json.dumps(result_json, ensure_ascii=False)

    """
    For manual testing of the endpoint:
        http PUT localhost:8000/relay/1 host_address="127.0.0.1" port=7541 name="alpha" main=true auto=true
    """
    def on_put(self, req, resp, uid):
        """
        Handle and respond to incoming PUT request.
        :param req: Request object
        :param resp: Response object
        """
        try:
            raw_json = req.stream.read()
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Error',
                                   'Error reading request body.')

        try:
            result_json = json.loads(raw_json, encoding='utf-8')
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Malformed JSON',
                                   'Could not decode the request body. The '
                                   'JSON was incorrect.')

        result_json["uid"] = uid
        result_json["status"] = "connected"

        resp.body = json.dumps(result_json, ensure_ascii=False)

    """
    For manual testing of the endpoint:
        http DELETE localhost:8000/relay/10
    """
    def on_delete(self, req, resp, uid):
        """
        Handle and respond to incoming DELETE request.
        :param req: Request object
        :param resp: Response object
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
