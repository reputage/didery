import lmdb
import os
try:
    import simplejson as json
except ImportError:
    import json


MAX_DB_COUNT = 8

DATABASE_DIR_PATH = "/var/didery/db"
ALT_DATABASE_DIR_PATH = os.path.join('~', '.consensys/didery/db')

DB_EVENT_HISTORY_NAME = b'event_history'
DB_KEY_HISTORY_NAME = b'key_history'
DB_OTP_BLOB_NAME = b'otp_blob'

gDbDirPath = None   # database directory location has not been set up yet
dideryDB = None    # database environment has not been set up yet


def setupDbEnv(baseDirPath=None, port=8080):
    """
    Setup the module globals gDbDirPath, and dideryDB using baseDirPath
    if provided otherwise use DATABASE_DIR_PATH
    :param port: int
        used to differentiate dbs for multiple didery servers running on the same computer
    :param baseDirPath: string
        directory where the database is located
    """
    global gDbDirPath, dideryDB

    if not baseDirPath:
        baseDirPath = "{}{}".format(DATABASE_DIR_PATH, port)

    baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
    if not os.path.exists(baseDirPath):
        try:
            os.makedirs(baseDirPath)
        except OSError as ex:
            baseDirPath = "{}{}".format(ALT_DATABASE_DIR_PATH, port)
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)
    else:
        if not os.access(baseDirPath, os.R_OK | os.W_OK):
            baseDirPath = "{}{}".format(ALT_DATABASE_DIR_PATH, port)
            baseDirPath = os.path.abspath(os.path.expanduser(baseDirPath))
            if not os.path.exists(baseDirPath):
                os.makedirs(baseDirPath)

    gDbDirPath = baseDirPath  # set global

    dideryDB = lmdb.open(gDbDirPath, max_dbs=MAX_DB_COUNT)
    dideryDB.open_db(DB_EVENT_HISTORY_NAME)
    dideryDB.open_db(DB_KEY_HISTORY_NAME)
    dideryDB.open_db(DB_OTP_BLOB_NAME)

    return dideryDB

def eventCount():
    """
        Gets a count of the number of entries in the table

        :return: int count
    """
    subDb = dideryDB.open_db(DB_EVENT_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=False) as txn:
        return txn.stat(subDb)['entries']

def getEvent(did):
    """
        Find and return an event history matching the supplied did.

        :param did: string
            W3C did identifier for history object
        :return: dict
    """
    subDb = dideryDB.open_db(DB_EVENT_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=False) as txn:
        raw_data = txn.get(did.encode())

        if raw_data is None:
            return None

        return json.loads(raw_data)


def saveEvent(did, data, sigs):
    """
        Store an event and signatures

        :param did: string
            W3C did string
        :param data: dict
            A dict containing the rotation history and signatures

    """
    db_entry = []
    certifiable_data = {
        "event": data,
        "signatures": sigs
    }
    db_entry.append(certifiable_data)

    old_data = getEvent(did)
    if old_data is not None:
        print(old_data)
        for entry in old_data:
            db_entry.append(entry)

    subDb = dideryDB.open_db(DB_EVENT_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=True) as txn:
        txn.put(
            did.encode(),
            json.dumps(db_entry).encode()
        )

    return certifiable_data

def getAllEvents(offset=0, limit=10):
    """
        Get all events in a range between the offset and offset+limit

        :param offset: int starting point of the range
        :param limit: int maximum number of entries to return
        :return: dict
    """
    subDb = dideryDB.open_db(DB_EVENT_HISTORY_NAME)
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


def deleteEvent(did):
    """
        Find and delete a key rotation history matching the supplied did.

    :param did: string
        W3C did identifier for history object
    :return: boolean
    """
    subDb = dideryDB.open_db(DB_EVENT_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=True) as txn:
        status = txn.delete(did.encode())

        return status

def historyCount():
    """
        Gets a count of the number of entries in the table

        :return: int count
    """
    subDb = dideryDB.open_db(DB_KEY_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=False) as txn:
        return txn.stat(subDb)['entries']


def saveHistory(did, data, sigs):
    """
        Store a rotation history and signatures

        :param did: string
            W3C did string
        :param data: dict
            A dict containing the rotation history and signatures

    """
    certifiable_data = {
        "history": data,
        "signatures": sigs
    }
    subDb = dideryDB.open_db(DB_KEY_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=True) as txn:
        txn.put(
            did.encode(),
            json.dumps(certifiable_data).encode()
        )

    return certifiable_data


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
    """
        Get all rotation histories in a range between the offset and offset+limit

        :param offset: int starting point of the range
        :param limit: int maximum number of entries to return
        :return: dict
    """
    subDb = dideryDB.open_db(DB_KEY_HISTORY_NAME)
    values = {"data": []}

    with dideryDB.begin(db=subDb, write=False) as txn:
        cursor = txn.cursor()

        count = 0
        for key, value in cursor:
            if count >= limit+offset:
                break

            if offset < count+1:
                values["data"].append(json.loads(value))

            count += 1

    return values


def deleteHistory(did):
    """
        Find and delete a key rotation history matching the supplied did.

    :param did: string
        W3C did identifier for history object
    :return: boolean
    """
    subDb = dideryDB.open_db(DB_KEY_HISTORY_NAME)

    with dideryDB.begin(db=subDb, write=True) as txn:
        status = txn.delete(did.encode())

        return status


def otpBlobCount():
    """
        Gets a count of the number of entries in the table

        :return: int count
    """
    subDb = dideryDB.open_db(DB_OTP_BLOB_NAME)

    with dideryDB.begin(db=subDb, write=False) as txn:
        return txn.stat(subDb)['entries']


def saveOtpBlob(did, data, sigs):
    """
        Store a otp encrypted key and signatures

        :param did: string
            W3C did string
        :param data: dict
            A dict containing the otp encrypted key and signatures

    """
    certifiable_data = {
        "otp_data": data,
        "signatures": sigs
    }
    subDb = dideryDB.open_db(DB_OTP_BLOB_NAME)

    with dideryDB.begin(db=subDb, write=True) as txn:
        txn.put(
            did.encode(),
            json.dumps(certifiable_data).encode()
        )

    return certifiable_data


def getOtpBlob(did):
    """
        Find and return an otp encrypted key matching the supplied did.

        :param did: string
            W3C did identifier for history object
        :return: dict
    """
    subDb = dideryDB.open_db(DB_OTP_BLOB_NAME)

    with dideryDB.begin(db=subDb, write=False) as txn:
        raw_data = txn.get(did.encode())

        if raw_data is None:
            return None

        return json.loads(raw_data)


def getAllOtpBlobs(offset=0, limit=10):
    """
            Get all otp encrypted keys in a range between the offset and offset+limit

            :param offset: int starting point of the range
            :param limit: int maximum number of entries to return
            :return: dict
        """
    subDb = dideryDB.open_db(DB_OTP_BLOB_NAME)
    values = {"data": []}

    with dideryDB.begin(db=subDb, write=False) as txn:
        cursor = txn.cursor()

        count = 0
        for key, value in cursor:
            if count >= limit + offset:
                break

            if offset < count + 1:
                values["data"].append(json.loads(value))

            count += 1

    return values


def deleteOtpBlob(did):
    """
        Find and delete a otp encrypted blob matching the supplied did.

    :param did: string
        W3C did identifier for history object
    :return: boolean
    """
    subDb = dideryDB.open_db(DB_OTP_BLOB_NAME)

    with dideryDB.begin(db=subDb, write=True) as txn:
        status = txn.delete(did.encode())

        return status


def loadTestData(name, data):
    pass
