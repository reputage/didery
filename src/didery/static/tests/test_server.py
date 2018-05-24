# ================================================== #
#                    TEST SERVER                     #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/21/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

__pragma__ ('alias', 'Global', 'global')


import didery.static.transcrypt.server as server
from tester import test

o = require("mithril/ospec/ospec")
sinon = require("sinon")

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

@test
class Server:
    """
    Class for testing server.
    """
    def beforeEach(self):
        """
        Sets up fake server and window.
        """
        self.testServer = sinon.createFakeServer()
        self.manager = server.Manager()
        window.XMLHttpRequest = Global.XMLHttpRequest

    # ============================================== #

    def afterEach(self):
        """
        Resets fake server.
        """
        self.testServer.restore()

    # ============================================== #

    def _respond(self, request, response):
        """
        Gives response to request.

            Parameters:
            request - HTTP request
            response - HTTP response
        """
        request.respond(200, {"Content-Type": "application/json"}, JSON.stringify(response))

    # ============================================== #

    def _respondTo(self, endpoint, data):
        """
        Gives response for specific endpoint.

            Parameters:
            endpoint - URL of API endpoint
            data - Data to be returned
        """
        self.testServer.respondWith(endpoint, lambda request: self._respond(request, data))

    # ============================================== #

    def basicRequest(self):
        """
        Tests basic server request.
        """
        endpoint = "/foo"

        def verify(request):
            o(request.method).equals("GET")("Checking basic request method.")
            o(request.url).equals(endpoint)("Checking basic request url.")
            request.respond(200)
        self.testServer.respondWith(verify)

        server.request(endpoint)
        self.testServer.respond()

    # ============================================== #

    def queryRequest(self):
        """
        Tests server request with query.
        """
        endpoint = "/foo"
        full_path = "/foo?one=1&two=2"

        def verify(request):
            o(request.method).equals("GET")("Checking query request method.")
            o(request.url).equals(full_path)("Checking basic request url.")
            request.respond(200)
        self.testServer.respondWith(verify)

        server.request(endpoint, one=1, two=2)
        self.testServer.respond()

    # ============================================== #

    def asyncErrors(self, done):
        """
        Tests errors request.

            Parameters:
            done - Automatically included promise done function
        """
        o(len(self.manager.errors.errors)).equals(0)("Checking initial errors list.")

        self._respondTo("/errors", {
            "data": [{
                    "title": "Invalid Signature.",
                    "msg": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= had an invalid rotation signature.",
                    "time": "2000-01-01T00:00:00+00:00"
                },
                {
                    "title": "Relay Unreachable.",
                    "msg": "Could not establish a connection with relay servers.",
                    "time": "2000-01-01T11:00:00+00:00"
                }]
            })

        def f1():
            o(len(self.manager.errors.errors)).equals(2)("Checking errors list after promise.")
            o(self.manager.errors.errors[0]).deepEquals({
                    "title": "Invalid Signature.",
                    "msg": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= had an invalid rotation signature.",
                    "time": "2000-01-01T00:00:00+00:00"
                })("Checking first error entry.")
            o(self.manager.errors.errors[1]).deepEquals({
                    "title": "Relay Unreachable.",
                    "msg": "Could not establish a connection with relay servers.",
                    "time": "2000-01-01T11:00:00+00:00"
                })("Checking second error entry.")
            done()

        self.testServer.autoRespond = True
        self.manager.errors.refreshErrors().then(f1)

    # ============================================== #

    def asyncHistory(self, done):
        """
        Tests history request.

            Parameters:
            done - Automatically included promise done function
        """
        o(len(self.manager.history.history)).equals(0)("Checking initial history list.")

        self._respondTo("/history", {
            "data": [{
                "history":
                {
                    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                    "changed" : "2000-01-01T00:00:00+00:00",
                    "signer": 2,
                    "signers":
                    [
                        "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                        "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
                    ]
                },
                "signatures":
                [
                    "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
                ]
            }, {
                "history":
                {
                    "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                    "changed" : "2000-01-01T00:00:00+00:00",
                    "signer": 1,
                    "signers":
                    [
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
                    ]
                },
                "signatures":
                [
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw==",
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
                ]
            }]
        })

        def f1():
            o(len(self.manager.history.history)).equals(2)("Checking history list after promise.")
            o(self.manager.history.history[0]).deepEquals({
                "history":
                {
                    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                    "changed" : "2000-01-01T00:00:00+00:00",
                    "signer": 2,
                    "signers":
                    [
                        "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                        "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
                    ]
                },
                "signatures":
                [
                    "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
                ]
            })("Checking first history entry.")
            o(self.manager.history.history[1]).deepEquals({
                "history":
                {
                    "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                    "changed" : "2000-01-01T00:00:00+00:00",
                    "signer": 1,
                    "signers":
                    [
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
                    ]
                },
                "signatures":
                [
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw==",
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
                ]
            })("Checking second history entry.")
            done()

        self.testServer.autoRespond = True
        self.manager.history.refreshHistory().then(f1)

    # ============================================== #

    def asyncOTPBlobs(self, done):
        """
        Tests blobs request.

            Parameters:
            done - Automatically included promise done function
        """
        o(len(self.manager.otpBlobs.blobs)).equals(0)("Checking initial blobs list.")

        self._respondTo("/blob", {
            "data": [{
                "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
            },
            {
                "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
            }]
        })

        def f1():
            o(len(self.manager.otpBlobs.blobs)).equals(2)("Checking blobs list after promise.")
            o(self.manager.otpBlobs.blobs[0]).deepEquals({
                "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
            })("Checking first blob entry.")
            o(self.manager.otpBlobs.blobs[1]).deepEquals({
                "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
            })("Checking second blob entry.")
            done()

        self.testServer.autoRespond = True
        self.manager.otpBlobs.refreshBlobs().then(f1)

    # ============================================== #

    def asyncRelays(self, done):
        """
        Tests relays request.

            Parameters:
            done - Automatically included promise done function
        """
        o(len(self.manager.relays.relays)).equals(0)("Checking initial relay list.")

        self._respondTo("/relay", {
            "1": {
                "host address": "127.0.0.1",
                "port": 7541,
                "name": "alpha",
                "main": True,
                "uid": "1",
                "status": "connected"
            },
            "2": {
                "host address": "127.0.0.1",
                "port": 7542,
                "name": "beta",
                "main": False,
                "uid": "2",
                "status": "connected"
            }
        })

        def f1():
            o(len(self.manager.relays.relays)).equals(2)("Checking relays list after promise.")
            o(self.manager.relays.relays[0]).deepEquals({
                "host address": "127.0.0.1",
                "port": 7541,
                "name": "alpha",
                "main": True,
                "uid": "1",
                "status": "connected"
            })("Checking first relay entry.")
            o(self.manager.relays.relays[1]).deepEquals({
                "host address": "127.0.0.1",
                "port": 7542,
                "name": "beta",
                "main": False,
                "uid": "2",
                "status": "connected"
            })("Checking second relay entry.")
            done()

        self.testServer.autoRespond = True
        self.manager.relays.refreshRelays().then(f1)

# ================================================== #
#                        EOF                         #
# ================================================== #