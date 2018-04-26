import falcon
try:
    import simplejson as json
except ImportError:
    import json


class Error:
    def __init__(self, store=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store

    """
    For manual testing of the endpoint:
        http localhost:8000/errors
    """
    def on_get(self, req, resp):
        """
        Handle and respond to incoming GET request.
        :param req: Request object
        :param resp: Response object
        """
        body = {
            "data": [
                {
                    "title": "Invalid Signature.",
                    "msg": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= had an invalid rotation signature.",
                    "time": "2000-01-01T00:00:00+00:00"
                },
                {
                    "title": "Relay Unreachable.",
                    "msg": "Could not establish a connection with relay servers.",
                    "time": "2000-01-01T11:00:00+00:00"
                }
            ]
        }

        resp.body = json.dumps(body, ensure_ascii=False)
