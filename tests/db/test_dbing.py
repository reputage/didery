import didery.crypto.eddsa

try:
    import simplejson as json
except ImportError:
    import json

from didery.db import dbing
from didery.help import helping as help


DB_DIR_PATH = "/tmp/db_setup_test"
SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
VK = b"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
DID = "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="


def testSetupDbEnvWithPath():
    env = dbing.setupDbEnv(DB_DIR_PATH)
    assert env.path() == DB_DIR_PATH

    assert dbing.gDbDirPath == DB_DIR_PATH
    assert dbing.dideryDB is env


def testSetupDbEnvWithOutPath():
    # Cant test this without potentially deleting production databases
    pass


def testSetupDbEnvWithPort():
    # Cant test this without potentially deleting production databases
    pass


def testEmptyHistoryCount(historyDB):
    count = historyDB.historyCount()

    assert count == 0


def testHistoryCount():
    dbing.setupDbEnv(DB_DIR_PATH)

    dbHistory = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistory, write=True) as txn:
        data = b'{"id": "did:dad:-OVHx0sv_jJePGB9LBZaWDlrLkxMNlOeHPdHysViK9k=", "signer": 0, "signers": ["-OVHx0sv_jJePGB9LBZaWDlrLkxMNlOeHPdHysViK9k=", "5Bp8Z8_UOWZBtVxffoTVF3QYkE-W-CpKa6VnN27CcN8="]}'
        id = b'did:dad:-OVHx0sv_jJePGB9LBZaWDlrLkxMNlOeHPdHysViK9k='

        txn.put(id, data)

    count = dbing.historyDB.historyCount()

    assert count == 1


def testSaveHistory(historyDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    exp_data = historyDB.saveHistory(DID, data, sigs)

    dbHistory = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistory, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()


def testGetHistory(historyDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    exp_data = historyDB.saveHistory(DID, data, sigs)

    actual_data = historyDB.getHistory(DID)

    assert actual_data == exp_data


def testGetNonExistentHistory(historyDB):
    actual_data = historyDB.getHistory(DID)

    assert actual_data is None


def testGetAllHistories(historyDB):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    history1 = historyDB.saveHistory(DID, data, sigs)

    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    data = json.loads(body)
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), sk)]

    history2 = historyDB.saveHistory(did, data, sigs)

    exp_data = {
        'data': [
            history1,
            history2
        ]
    }

    actual_data = historyDB.getAllHistories()

    assert actual_data == exp_data


def testGetAllHistoriesOnEmptyDB(historyDB):
    actual_data = historyDB.getAllHistories()

    assert actual_data == {'data': []}


def testDeleteHistory(historyDB):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    data = json.loads(body)
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), sk)]

    historyDB.saveHistory(did, data, sigs)

    status = historyDB.deleteHistory(did)

    assert status is True
    assert historyDB.getHistory(did) is None


def testDeleteNonExistentHistory(historyDB):
    status = historyDB.deleteHistory(DID)

    assert status is False


def testEmptyOtpCount(otpDB):
    count = otpDB.otpBlobCount()

    assert count == 0


def testOtpBlobCount(otpDB):
    dbOtpBlob = dbing.dideryDB.open_db(dbing.DB_OTP_BLOB_NAME)

    with dbing.dideryDB.begin(db=dbOtpBlob, write=True) as txn:
        data = b'{"id": "did:dad:Y2CR8pS8z2YvJQN-FH_wprtF1TyA0jTlXC3MrMmaNyY=", "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"}'
        id = b'did:dad:Y2CR8pS8z2YvJQN-FH_wprtF1TyA0jTlXC3MrMmaNyY='

        txn.put(id, data)

    count = otpDB.otpBlobCount()

    assert count == 1


def testSaveOtpBlob(otpDB):
    data = {
        "id": DID,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    exp_data = otpDB.saveOtpBlob(DID, data, sigs)

    dbOtpBlob = dbing.dideryDB.open_db(dbing.DB_OTP_BLOB_NAME)

    with dbing.dideryDB.begin(db=dbOtpBlob, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()


def testGetOtpBlob(otpDB):
    data = {
        "id": DID,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    exp_data = otpDB.saveOtpBlob(DID, data, sigs)

    actual_data = otpDB.getOtpBlob(DID)

    assert actual_data == exp_data


def testGetNonExistentOtpBlob(otpDB):
    actual_data = otpDB.getOtpBlob(DID)

    assert actual_data is None


def testGetAllOtpBlobs(otpDB):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    data = {
        "id": DID,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    otpBlob1 = otpDB.saveOtpBlob(DID, data, sigs)

    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    data = {
        "id": did,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), sk)]

    otpBlob2 = otpDB.saveOtpBlob(did, data, sigs)

    exp_data = {
        'data': [
            otpBlob1,
            otpBlob2
        ]
    }

    actual_data = otpDB.getAllOtpBlobs()

    assert actual_data == exp_data


def testGetAllOtpBlobsOnEmptyDB(otpDB):
    actual_data = otpDB.getAllOtpBlobs()

    assert actual_data == {'data': []}


def testDeleteOtpBlob(otpDB):
    data = {
        "id": DID,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    otpDB.saveOtpBlob(DID, data, sigs)

    status = otpDB.deleteOtpBlob(DID)

    assert status is True
    assert otpDB.getOtpBlob(DID) is None


def testDeleteNonExistentOtpBlob(otpDB):
    status = otpDB.deleteOtpBlob(DID)

    assert status is False


def testEmptyEventCount(eventsDB):
    count = eventsDB.eventCount()

    assert count == 0


def testEventCount(eventsDB):
    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=True) as txn:
        data = b'{"id": "did:dad:-OVHx0sv_jJePGB9LBZaWDlrLkxMNlOeHPdHysViK9k=", "signer": 0, "signers": ["-OVHx0sv_jJePGB9LBZaWDlrLkxMNlOeHPdHysViK9k=", "5Bp8Z8_UOWZBtVxffoTVF3QYkE-W-CpKa6VnN27CcN8="]}'
        id = b'did:dad:Y2CR8pS8z2YvJQN-FH_wprtF1TyA0jTlXC3MrMmaNyY='

        txn.put(id, data)

    count = eventsDB.eventCount()

    assert count == 1


def testCreateEventHistory(eventsDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    exp_data = eventsDB.saveEvent(DID, data, sigs)

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()


def testUpdateEventHistory(eventsDB):
    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    eventsDB.saveEvent(DID, inception, sigs)

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    sigs2 = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = eventsDB.saveEvent(DID, rotation, sigs2)

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=True) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "event": rotation,
            "signatures": sigs2
        },
        {
            "event": inception,
            "signatures": sigs
        }
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()


def testGetEvent(eventsDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    returned_data = eventsDB.saveEvent(DID, data, sigs)

    actual_data = eventsDB.getEvent(DID)

    exp_result = [
        {
            "event": data,
            "signatures": sigs
        },
    ]

    assert actual_data == returned_data
    assert actual_data == exp_result
    assert returned_data == exp_result


def testGetAllEventsOnEmptyDB(eventsDB):
    actual_data = eventsDB.getAllEvents()

    assert actual_data == {'data': []}


def testGetAllEvents(eventsDB):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    eventsDB.saveEvent(DID, data, sigs)

    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    sigs2 = [didery.crypto.eddsa.signResource(body, sk)]
    data2 = json.loads(body)

    eventsDB.saveEvent(did, data2, sigs2)

    exp_data = {
        'data': [[
            {
                "event": data,
                "signatures": sigs
            }],
            [{
                "event": data2,
                "signatures": sigs2
            }]
        ]
    }

    actual_data = eventsDB.getAllEvents()

    assert actual_data == exp_data


def testDeleteNonExistentEvent(eventsDB):
    status = eventsDB.deleteEvent(DID)

    assert status is False


def testDeleteEvent(eventsDB):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    data = json.loads(body)
    sigs = [didery.crypto.eddsa.signResource(body, sk)]

    eventsDB.saveEvent(did, data, sigs)

    status = eventsDB.deleteEvent(did)

    assert status is True
    assert eventsDB.getEvent(did) is None
