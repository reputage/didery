from didery.controllers import history as histories
from didery.controllers import otp_blob as blobs
from didery.controllers import relays
from didery.controllers import errors
from didery.controllers import static
from didery.controllers import events

STATIC_BASE_PATH = "/static"
DEFAULT_STATIC_BASE_PATH = "/"
STREAM_BASE_PATH = "/stream"
HISTORY_BASE_PATH = "/history"
BLOB_BASE_PATH = "/blob"
RELAY_BASE_PATH = "/relay"
ERRORS_BASE_PATH = "/errors"
EVENTS_BASE_PATH = "/event"


class CORSMiddleware:
    def process_request(self, req, resp):
        resp.set_header('Access-Control-Max-Age:', '3600')
        resp.set_header('Access-Control-Allow-Origin', '*')
        resp.set_header('Access-Control-Allow-Methods',
                                   'PUT, GET, POST, DELETE, HEAD, OPTIONS')
        resp.set_header('Access-Control-Allow-Headers',
                                   'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token, X-Auth-Token, Signature')


def loadEndPoints(app, store):
    """
    Add Rest endpoints to a falcon.API object by mapping the API's routes.
    :param app: falcon.API object
    :param store: Store
        ioflo datastore
    """

    sink = static.StaticSink()
    app.add_sink(sink, prefix=DEFAULT_STATIC_BASE_PATH)

    history = histories.History(store)
    app.add_route('{}/{{did}}'.format(HISTORY_BASE_PATH), history)
    app.add_route('{}'.format(HISTORY_BASE_PATH), history)

    historyStream = histories.HistoryStream(store)
    app.add_route('{}{}/{{did}}'.format(STREAM_BASE_PATH, HISTORY_BASE_PATH), historyStream)
    app.add_route('{}{}'.format(STREAM_BASE_PATH, HISTORY_BASE_PATH), historyStream)

    blob = blobs.OtpBlob(store)
    app.add_route('{}/{{did}}'.format(BLOB_BASE_PATH), blob)
    app.add_route('{}'.format(BLOB_BASE_PATH), blob)

    relay = relays.Relay(store)
    app.add_route('{}/{{uid}}'.format(RELAY_BASE_PATH), relay)
    app.add_route('{}'.format(RELAY_BASE_PATH), relay)

    error = errors.Error(store)
    app.add_route('{}'.format(ERRORS_BASE_PATH), error)

    event = events.Event(store)
    app.add_route('{}/{{did}}'.format(EVENTS_BASE_PATH), event)
    app.add_route('{}'.format(EVENTS_BASE_PATH), event)
