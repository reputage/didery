from didery.controllers import history as histories
from didery.controllers import otp_blob as blobs
from didery.controllers import relays
from didery.controllers import errors
from didery.controllers import static

STATIC_BASE_PATH = "/static"
DEFAULT_STATIC_BASE_PATH = "/"
HISTORY_BASE_PATH = "/history"
BLOB_BASE_PATH = "/blob"
RELAY_BASE_PATH = "/relay"
ERRORS_BASE_PATH = "/errors"


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
    app.add_route('{}/{{did}}/{{offset:int(min=0)}}/{{limit:int(min=1, max=100)}}'.format(HISTORY_BASE_PATH), history)
    app.add_route('{}'.format(HISTORY_BASE_PATH), history)

    blob = blobs.OtpBlob(store)
    app.add_route('{}/{{did}}'.format(BLOB_BASE_PATH), blob)
    app.add_route('{}'.format(BLOB_BASE_PATH), blob)

    relay = relays.Relay(store)
    app.add_route('{}/{{uid}}'.format(RELAY_BASE_PATH), relay)
    app.add_route('{}'.format(RELAY_BASE_PATH), relay)

    error = errors.Error(store)
    app.add_route('{}'.format(ERRORS_BASE_PATH), error)
