"""

conftest.py allows you to define fixtures on a package level
The fixtures below will be available to all tests within the
controllers directory.

"""

import shutil
import pytest
import falcon
from falcon import testing

from ioflo.base import storing

from didery.routing import *
from didery.db import dbing
from didery.help import helping


@pytest.fixture(scope="module")
def testApp():
    """

    setup falcon and load REST endpoints

    """
    def app(mode="method"):
        store = storing.Store(stamp=0.0)
        testApp = falcon.API()
        loadEndPoints(testApp, store=store, mode=mode)
        return testApp

    return app


@pytest.fixture(scope="module")
def client(testApp):
    """

    This function utilizes the testApp() fixture above

    Pytest runs this function once per module

    testing.TestClient() is optional
    It allows you to avoid passing your app object into every
    simulate_xxx() function call

    """

    return testing.TestClient(testApp("method"))


@pytest.fixture(scope="module")
def promiscuous_client(testApp):
    """

    This function utilizes the testApp() fixture above

    Pytest runs this function once per module

    testing.TestClient() is optional
    It allows you to avoid passing your app object into every
    simulate_xxx() function call

    """

    return testing.TestClient(testApp("promiscuous"))


@pytest.fixture(scope="module")
def race_client(testApp):
    """

    This function utilizes the testApp() fixture above

    Pytest runs this function once per module

    testing.TestClient() is optional
    It allows you to avoid passing your app object into every
    simulate_xxx() function call

    """

    return testing.TestClient(testApp("race"))


@pytest.fixture(autouse=True)
def setupTeardown():
    """

    Pytest runs this function before every test when autouse=True
    Without autouse=True you would have to add a setupTeardown parameter
    to each test function

    """
    # setup
    dbPath = helping.setupTmpBaseDir()
    dbing.setupDbEnv(dbPath)

    yield dbPath  # this allows the test to run

    # teardown
    helping.cleanupTmpBaseDir(dbPath)
