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

    def on_put(self, req, resp, uid):
        """
        Handle and respond to incoming PUT request.
        :param req: Request object
        :param resp: Response object
        """
        result_json = req.body

        result_json["uid"] = uid
        result_json["status"] = "connected"

        resp.body = json.dumps(result_json, ensure_ascii=False)

    def on_delete(self, req, resp, uid):
        """
        Handle and respond to incoming DELETE request.
        :param req: Request object
        :param resp: Response object
        """
        result_json = req.body

        result_json["uid"] = uid
        result_json["status"] = "connected"

        resp.body = json.dumps(result_json, ensure_ascii=False)
