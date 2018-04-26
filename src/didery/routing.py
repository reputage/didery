from didery.controllers import history as rhistory


HISTORY_BASE_PATH = "/history"


def loadEndPoints(app, store):
    """
    Add Rest endpoints to a falcon.API object by mapping the API's routes.
    :param app: falcon.API object
    :param store: Store
        ioflo datastore
    """
    history = rhistory.History(store)
    app.add_route('{}/{{did}}'.format(HISTORY_BASE_PATH), history)
    app.add_route('{}'.format(HISTORY_BASE_PATH), history)

