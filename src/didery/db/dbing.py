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
historyDB = None
otpDB = None
eventsDB = None


def setupDbEnv(baseDirPath=None, port=8080, mode="method"):
    """
    Setup the module globals gDbDirPath, and dideryDB using baseDirPath
    if provided otherwise use DATABASE_DIR_PATH
    :param baseDirPath: string
        directory where the database is located
    :param port: int
        used to differentiate dbs for multiple didery servers running on the same computer
    :param mode: string
        Didery's operating mode
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

    createDBWrappers(mode=mode)

    return dideryDB


def createDBWrappers(mode="method"):
    global historyDB, otpDB, eventsDB

    if mode == "promiscuous":
        historyDB = PromiscuousHistoryDB()
        eventsDB = PromiscuousEventsDB()
    elif mode == "race":
        historyDB = RaceHistoryDB()
        eventsDB = RaceEventsDB()
    elif mode == "method":
        historyDB = BaseHistoryDB()
        eventsDB = MethodEventsDB()
    else:
        historyDB = BaseHistoryDB()
        eventsDB = BaseEventsDB()

    otpDB = BaseBlobDB()


class DB:
    def __init__(self, namedDB):
        """
        :param namedDB: string
            name of the table to be accessed
        """
        self.namedDB = namedDB

    def count(self):
        """
            Gets a count of the number of entries in the table

            :return: int count
        """
        subDb = dideryDB.open_db(self.namedDB)

        with dideryDB.begin(db=subDb, write=False) as txn:
            return txn.stat(subDb)['entries']

    def save(self, key, data):
        """
            Store a key value pair

            :param key: string
                key to identify data
            :param data: dict
                A dict of the data to be stored

        """
        # TODO check if did length in bytes exceeds lmdb's max key length
        # TODO register an error in the error DB if it is
        subDb = dideryDB.open_db(self.namedDB)

        with dideryDB.begin(db=subDb, write=True) as txn:
            txn.put(
                key.encode(),
                json.dumps(data).encode()
            )

    def get(self, key):
        """
            Find and return a key value pair

            :param key: string
                key to look up
            :return: dict
        """
        subDb = dideryDB.open_db(self.namedDB)

        with dideryDB.begin(db=subDb, write=False) as txn:
            raw_data = txn.get(key.encode())

            if raw_data is None:
                return None

            return json.loads(raw_data)

    def getAll(self, offset=0, limit=10):
        """
            Get all key value pairs in a range between the offset and offset+limit

            :param offset: int starting point of the range
            :param limit: int maximum number of entries to return
            :return: dict
        """
        subDb = dideryDB.open_db(self.namedDB)
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

    def delete(self, key):
        """
            Find and delete a key value pair matching the supplied key.

            :param key: string
                key to delete
            :return: boolean
        """
        subDb = dideryDB.open_db(self.namedDB)

        with dideryDB.begin(db=subDb, write=True) as txn:
            status = txn.delete(key.encode())

            return status


class BaseEventsDB:
    def __init__(self, db=None):
        if db is None:
            self.db = DB(DB_EVENT_HISTORY_NAME)
        else:
            self.db = db

    def eventCount(self):
        """
            Gets a count of the number of entries in the table

            :return: int count
        """
        return self.db.count()

    def saveEvent(self, did, data, sigs):
        """
            Store an event and signatures

            :param did: string
                W3C DID string
            :param data: dict
                A dict containing the rotation history and signatures
            :param sigs: dict
                A dict containing the rotation history signatures
        """
        db_entry = [
            [
                {
                    "event": data,
                    "signatures": sigs
                },
            ]
        ]

        old_data = self.getEvent(did)
        if old_data is not None:
            db_entry[0].extend(old_data)

        self.db.save(did, db_entry)

        return db_entry

    def getEvent(self, did):
        """
            Find and return an event history matching the supplied did.

            :param did: string
                W3C DID identifier for rotation history events
            :return: dict
        """
        return self.db.get(did)

    def getAllEvents(self, offset=0, limit=10):
        """
            Get all events in a range between the offset and offset+limit

            :param offset: int starting point of the range
            :param limit: int maximum number of entries to return
            :return: dict
        """
        return self.db.getAll(offset, limit)

    def deleteEvent(self, did):
        """
            Find and delete the rotation events matching the supplied did.

        :param did: string
            W3C DID identifier for rotation history events
        :return: boolean
        """
        return self.db.delete(did)


class MethodEventsDB(BaseEventsDB):
    def __init__(self, db=None):
        """
        :param db: DB for interacting with lmdb
        """
        BaseEventsDB.__init__(self, db)

    def saveEvent(self, did, data, sigs):
        """
            Store an event and signatures

            :param did: string
                W3C DID string
            :param data: dict
                A dict containing the rotation history and signatures
            :param sigs: dict
                A dict containing the rotation history signatures
        """
        root_vk = data['signers'][0]
        event = self.getEvent(did)

        db_entry = [
            [
                {
                    "event": data,
                    "signatures": sigs
                },
            ]
        ]

        # Make sure we grab, format, and append existing data
        if event is not None:
            for key, item in enumerate(event):
                if item[0]["event"]["signers"][0] == root_vk:
                    db_entry[0].extend(item)

        self.db.save(did, db_entry)

        return db_entry


class RaceEventsDB(BaseEventsDB):
    def __init__(self, db=None):
        """
        :param db: DB for interacting with lmdb
        """
        BaseEventsDB.__init__(self, db)

    def saveEvent(self, did, data, sigs):
        """
            Store an event and signatures

            :param did: string
                W3C DID string
            :param data: dict
                A dict containing the rotation history and signatures
            :param sigs: dict
                A dict containing the rotation history signatures
        """
        db_entry = []
        event = self.getEvent(did)

        update = {
            "event": data,
            "signatures": sigs
        }

        # Make sure existing data is formatted correctly
        if event is not None:
            temp = [update]
            temp.extend(event[0])
            event[0] = temp

            db_entry = event
        else:
            db_entry.append([update])

        self.db.save(did, db_entry)

        return db_entry


class PromiscuousEventsDB(BaseEventsDB):
    def __init__(self, db=None):
        """
        :param db: DB for interacting with lmdb
        """
        BaseEventsDB.__init__(self, db)

    def saveEvent(self, did, data, sigs):
        """
            Store an event and signatures. Most recently updated event history will be the first in the list

            :param did: string
                W3C DID string
            :param data: dict
                A dict containing the rotation history and signatures
            :param sigs: dict
                A dict containing the rotation history signatures
        """
        db_entry = []
        root_vk = data['signers'][0]
        event = self.getEvent(did)

        update = {
            "event": data,
            "signatures": sigs
        }

        if event is not None:
            temp1 = []
            temp2 = []
            for key, item in enumerate(event):
                if item[0]["event"]["signers"][0] == root_vk:
                    temp1.append(update)
                    temp1.extend(item)
                else:
                    temp2.append(item)

            if len(temp1) == 0:
                temp1.append(update)

            db_entry.append(temp1)
            db_entry.extend(temp2)
        else:
            db_entry.append([update])

        self.db.save(did, db_entry)

        return db_entry


class BaseHistoryDB:
    def __init__(self, db=None):
        """
            :param db: DB for interacting with lmdb
        """
        if db is None:
            self.db = DB(DB_KEY_HISTORY_NAME)
        else:
            self.db = db

    def historyCount(self):
        """
            Returns the number of entries in the table

            :return: int count
        """
        return self.db.count()

    def saveHistory(self, did, data, sigs):
        """
            Store a rotation history and signatures

            :param did: string
                W3C did string
            :param data: dict
                A dict containing the rotation history
            :param sigs: dict
                A dict containing the rotation history signatures

        """
        certifiable_data = {
            "history": data,
            "signatures": sigs
        }

        self.db.save(did, certifiable_data)

        return certifiable_data

    def getHistory(self, did):
        """
            Find and return a key rotation history matching the supplied did.

            :param did: string
                W3C did identifier for history object
            :return: dict
        """
        return self.db.get(did)

    def getAllHistories(self, offset=0, limit=10):
        """
            Get all rotation histories in a range between the offset and offset+limit

            :param offset: int starting point of the range
            :param limit: int maximum number of entries to return
            :return: dict
        """
        return self.db.getAll(offset, limit)

    def deleteHistory(self, did):
        """
            Find and delete a key rotation history matching the supplied did.

            :param did: string
                W3C did identifier for history object
            :return: boolean
        """
        return self.db.delete(did)


class RaceHistoryDB(BaseHistoryDB):
    def __init__(self, db=None):
        """
        :param db: DB for interacting with lmdb
        """
        BaseHistoryDB.__init__(self, db)

    def saveHistory(self, did, data, sigs):
        """
            Store a rotation history and signatures

            :param did: string
                W3C did string
            :param data: dict
                A dict containing the rotation history
            :param sigs: dict
                A dict containing the rotation history signatures
        """
        root_vk = data['signers'][0]
        history = self.getHistory(did)

        update = {
            "history": data,
            "signatures": sigs
        }

        # Make sure existing data is formatted correctly
        if history is not None:
            if "history" not in history:
                history[root_vk] = update
                update = history

        self.db.save(did, update)

        return history


class PromiscuousHistoryDB(BaseHistoryDB):
    def __init__(self, db=None):
        """
        :param db: DB for interacting with lmdb
        """
        BaseHistoryDB.__init__(self, db)

    def saveHistory(self, did, data, sigs):
        """
            Store a rotation history and signatures

            :param did: string
                W3C did string
            :param data: dict
                A dict containing the rotation history
            :param sigs: dict
                A dict containing the rotation history signatures
        """
        root_vk = data['signers'][0]
        history = self.getHistory(did)

        # Make sure existing data is formatted correctly
        if history is not None:
            if "history" in history:
                key = history["history"]["signers"][0]

                history = {
                    key: history
                }
        else:
            history = {}

        history[root_vk] = {
            "history": data,
            "signatures": sigs
        }

        self.db.save(did, history)

        return history


class BaseBlobDB:
    def __init__(self, db=None):
        """
            :param db: DB for interacting with lmdb
                This is mostly for mocking the db in testing
        """
        if db is None:
            self.db = DB(DB_OTP_BLOB_NAME)
        else:
            self.db = db

    def otpBlobCount(self):
        """
            Returns the number of entries in the table

            :return: int count
        """
        return self.db.count()

    def saveOtpBlob(self, did, data, sigs):
        """
            Store a otp encrypted key and signatures

            :param did: string
                W3C did string
            :param data: dict
                A dict containing the otp encrypted keys and signatures
            :param sigs: dict
                A dict containing the otp encrypted keys signatures

        """
        certifiable_data = {
            "otp_data": data,
            "signatures": sigs
        }

        self.db.save(did, certifiable_data)

        return certifiable_data

    def getOtpBlob(self, did):
        """
            Find and return an otp encrypted key matching the supplied did.

            :param did: string
                W3C did identifier for history object
            :return: dict
        """
        return self.db.get(did)

    def getAllOtpBlobs(self, offset=0, limit=10):
        """
            Get all otp encrypted keys in a range between the offset and offset+limit

            :param offset: int starting point of the range
            :param limit: int maximum number of entries to return
            :return: dict
        """
        return self.db.getAll(offset, limit)

    def deleteOtpBlob(self, did):
        """
            Find and delete a otp encrypted blob matching the supplied did.

            :param did: string
                W3C did identifier for history object
            :return: boolean
        """
        return self.db.delete(did)
