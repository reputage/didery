# ================================================== #
#                      SERVER                        #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/03/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

# ================================================== #
#                 CONSTANTS & GLOBALS                #
# ================================================== #

DEFAULT_INTERVAL = 1000

# ================================================== #
#                     FUNCTIONS                      #
# ================================================== #

__pragma__("kwargs")


def request(path, **kwargs):
    """
    Performs a mithril GET request.

        Parameters:
        path - Endpoint string
        kwargs - Dictionary of path query arguments

        Returns:
        Promise from m.request
    """
    path += "?"
    for key, value in kwargs.items():
        path += key + "=" + str(value) + "&"
    path = path[:-1]
    return m.request(path)

# ================================================== #


def onlyOne(func, interval=1000):
    """
    Enforces the promise function. Never called more than once
    per interval.

        Parameters:
        func - Executor function
        interval - Promise interval in milliseconds
    """
    scope = {"promise": None, "lastCalled": 0}

    def wrap():
        now = __new__(Date())
        if scope.promise != None and now - scope.lastCalled < interval:
            return scope.promise

        scope.lastCalled = now

        def f(resolve, reject):
            p = func()
            p.then(resolve)
            p.catch(reject)
        scope.promise = __new__(Promise(f))
        return scope.promise
    return wrap
__pragma__("nokwargs")

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #


def clearArray(a):
    """
    Clears an array/list.

        Parameters:
        a - Array/List to be cleared
    """
    while len(a):
        a.pop()

# ================================================== #


class Manager:
    """
    Class for managing server calls.
    """
    def __init__(self):
        """
        Initialize Manager object. Loads all server calls.
        """
        self.errors = Errors()
        self.history = History()
        self.otpBlobs = OTPBlobs()
        self.relays = Relays()

# ================================================== #


class Errors:
    """
    Class for error server call.
    """
    Refresh_Interval = DEFAULT_INTERVAL
    # Refresh rates should never exceed the default interval rate.

    def __init__(self):
        """
        Initialize Errors object.
        """
        self.errors = []
        self.refreshErrors = onlyOne(self._refreshErrors, interval=self.Refresh_Interval)

    # ============================================== #

    def _refreshErrors(self):
        """
        Clears error array and retrieves fresh error data.
        """

        clearArray(self.errors)
        return request("/errors").then(self._parseAll)

    # ============================================== #

    def _parseAll(self, data):
        """
        Parses returned error data.

            Parameters:
            data - Returned error data

            Example:
            {
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
            }
        """
        if 'data' in data:
            for error in data['data']:
                self.errors.append(error)

# ================================================== #


class History:
    """
    Class for history server call.
    """
    Refresh_Interval = DEFAULT_INTERVAL
    # Refresh rates should never exceed the default interval rate.

    def __init__(self):
        """
        Initialize History object.
        """
        self.history = []
        self.refreshHistory = onlyOne(self._refreshHistory, interval=self.Refresh_Interval)

    # ============================================== #

    def _refreshHistory(self):
        """
        Clears history array and retrieves fresh history data.
        """

        clearArray(self.history)
        return request("/history").then(self._parseAll)

    # ============================================== #

    def _parseAll(self, data):
        """
        Parses returned history data.

            Parameters:
            data - Returned history data

            Example:
            {
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
            }

        """
        if 'data' in data:
            for key, history in enumerate(data['data']):
                self.history.append(history)

# ================================================== #


class OTPBlobs:
    """
    Class for otp blob server call.
    """
    Refresh_Interval = DEFAULT_INTERVAL

    # Refresh rates should never exceed the default interval rate.

    def __init__(self):
        """
        Initialize OTPBlob object.
        """
        self.blobs = []
        self.refreshBlobs = onlyOne(self._refreshBlobs, interval=self.Refresh_Interval)

    # ============================================== #

    def _refreshBlobs(self):
        """
        Clears blob array and retrieves fresh blob data.
        """

        clearArray(self.blobs)
        return request("/blob").then(self._parseAll)

    # ============================================== #

    def _parseAll(self, data):
        """
        Parses returned blob data.

            Parameters:
            data - Returned blob data

            Example:
            {
                "data": [{
                    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
                },
                {
                    "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
                }]
            }
        """

        if 'data' in data:
            for blob in data['data']:
                self.blobs.append(blob)

# ================================================== #


class Relays:
    """
    Class for relays server call.
    """
    Refresh_Interval = DEFAULT_INTERVAL
    # Refresh rates should never exceed the default interval rate.

    def __init__(self):
        """
        Initialize Relays object.
        """
        self.relays = []
        self.refreshRelays = onlyOne(self._refreshRelays, interval=self.Refresh_Interval)

    # ============================================== #

    def _refreshRelays(self):
        """
        Clears relay array and retrieves fresh relay data.
        """

        clearArray(self.relays)
        return request("/relay").then(self._parseAll)

    # ============================================== #

    def _parseAll(self, data):
        """
        Parses returned relay data.

            Parameters:
            data - Returned relay data

            Example:
            {
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
            }
        """

        for relay in dict(data).items():
            self.relays.append(relay[1])

# ================================================== #
#                       MAIN                         #
# ================================================== #

manager = Manager()

# ================================================== #
#                        EOF                         #
# ================================================== #
