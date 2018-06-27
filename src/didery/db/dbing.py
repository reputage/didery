import lmdb
import os
try:
    import simplejson as json
except ImportError:
    import json


MAX_DB_COUNT = 8

DATABASE_DIR_PATH = "/var/reputation/db"
ALT_DATABASE_DIR_PATH = os.path.join('~', '.xaltry/reputation/db')

DB_KEY_HISTORY_NAME = b'key_history'
DB_OTP_BLOB_NAME = b'otp_blob'

gDbDirPath = None   # database directory location has not been set up yet
dideryDB = None    # database environment has not been set up yet


def setupDbEnv(baseDirPath=None):
    """
    Setup the module globals gDbDirPath, and dideryDB using baseDirPath
    if provided otherwise use DATABASE_DIR_PATH
    :param baseDirPath: string
        directory where the database is located
    """
    global gDbDirPath
    global dideryDB

    if not baseDirPath:
        baseDirPath = DATABASE_DIR_PATH

    baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
    if not os.path.exists(baseDirPath):
        try:
            os.makedirs(baseDirPath)
        except OSError as ex:
            baseDirPath = ALT_DATABASE_DIR_PATH
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)
    else:
        if not os.access(baseDirPath, os.R_OK | os.W_OK):
            baseDirPath = ALT_DATABASE_DIR_PATH
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)

    gDbDirPath = baseDirPath  # set global

    dideryDB = lmdb.open(gDbDirPath, max_dbs=MAX_DB_COUNT)
    dideryDB.open_db(DB_KEY_HISTORY_NAME)
    dideryDB.open_db(DB_OTP_BLOB_NAME)

    return dideryDB


def historyCount():
    subDb = dideryDB.open_db(DB_KEY_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=True) as txn:
        return txn.stat(subDb)['entries']


def saveHistory(did, data):
    """
        Takes a raw reputee dict and places it into the raw table as well
        as place an entry in the unprocessed table to signal the processor
        to calculate the reputee's reputation

        :param did: string
            W3C did string
        :param data: dict
            A dict containing the rotation history and signatures

    """
    subDb = dideryDB.open_db(DB_KEY_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=True) as txn:
        txn.put(
            did.encode(),
            json.dumps(data).encode()
        )


def getHistory(did):
    """
        Find and return a key rotation history matching the supplied did.
        :param did: string
            W3C did identifier for history object
        :return: dict
    """
    subDb = dideryDB.open_db(DB_KEY_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=False) as txn:
        raw_data = txn.get(did.encode())

        if raw_data is None:
            return None

        return json.loads(raw_data)


def getAllHistories(offset=0, limit=10):
    subDb = dideryDB.open_db(DB_KEY_HISTORY_NAME)
    values = {"data": []}

    with dideryDB.begin(db=subDb, write=False) as txn:
        cursor = txn.cursor()

        count = 0
        for key, value in cursor:
            if count >= limit+offset:
                break

            if offset < count+1:
                values["data"].append(value)

            count += 1

    return values


def otpBlobCount():
    subDb = dideryDB.open_db(DB_OTP_BLOB_NAME)

    with dideryDB.begin(db=subDb, write=True) as txn:
        return txn.stat(subDb)['entries']


def saveOtpBlob(did, data):
    pass


def getOtpBlob(did):
    pass


def loadTestData(name, data):
    pass
