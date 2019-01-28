import pytest
import os
import shutil

from didery.db import dbing


DB_DIR_PATH = "/tmp/db_setup_test"


def cleanupBaseDir(baseDirPath):
    """
    Remove baseDirPath
    """
    if os.path.exists(baseDirPath):
        shutil.rmtree(baseDirPath)


@pytest.fixture(autouse=True)
def setupTeardown():
    """

    Pytest runs this function before every test when autouse=True
    Without autouse=True you would have to add a setupTeardown parameter
    to each test function

    """

    yield DB_DIR_PATH  # this allows the test to run

    # teardown
    cleanupBaseDir(DB_DIR_PATH)
    assert not os.path.exists(DB_DIR_PATH)


@pytest.fixture
def historyDB():
    dbing.setupDbEnv(DB_DIR_PATH)
    return dbing.historyDB


@pytest.fixture
def otpDB():
    dbing.setupDbEnv(DB_DIR_PATH)
    return dbing.otpDB


@pytest.fixture
def eventsDB():
    dbing.setupDbEnv(DB_DIR_PATH)
    return dbing.eventsDB


@pytest.fixture
def promiscuousEventsDB():
    dbing.setupDbEnv(DB_DIR_PATH, mode="promiscuous")
    return dbing.eventsDB


@pytest.fixture
def raceEventsDB():
    dbing.setupDbEnv(DB_DIR_PATH, mode="race")
    return dbing.eventsDB
