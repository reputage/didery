import pytest
import os
import shutil


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
