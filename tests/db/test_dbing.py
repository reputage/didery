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


def testGetAllHistoriesWithBadlimit(historyDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    historyDB.saveHistory(DID, data, sigs)

    exp_data = {
        'data': []
    }

    actual_data = historyDB.getAllHistories(limit=0)

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

    eventsDB.saveEvent(DID, data, sigs)

    exp_data = [
        [
            {
                "event": data,
                "signatures": sigs
            },
        ]
    ]

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
        [
            {
                "event": rotation,
                "signatures": sigs2
            },
            {
                "event": inception,
                "signatures": sigs
            }
        ]
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
        [
            {
                "event": data,
                "signatures": sigs
            },
        ]
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
        'data': [
            [
                [
                    {
                        "event": data,
                        "signatures": sigs
                    }
                ]
            ],
            [
                [
                    {
                        "event": data2,
                        "signatures": sigs2
                    }
                ]
            ]
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


def testCreatePromiscuousEvent(promiscuousEventsDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    promiscuousEventsDB.saveEvent(DID, data, sigs)

    exp_data = [
        [
            {
                "event": data,
                "signatures": sigs
            }
        ]
    ]

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()


def testUpdatePromiscuousEvent(promiscuousEventsDB):
    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    promiscuousEventsDB.saveEvent(DID, inception, inceptionSigs)

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = promiscuousEventsDB.saveEvent(DID, rotation, rotationSigs)

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": rotation,
                "signatures": rotationSigs
            },
            {
                "event": inception,
                "signatures": inceptionSigs
            }
        ]
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()

    # Try updating events with hacked DID
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    inception2 = json.loads(body)
    inception2["id"] = DID
    inception2Sigs = [didery.crypto.eddsa.signResource(json.dumps(inception2).encode(), sk)]

    returned_data = promiscuousEventsDB.saveEvent(DID, inception2, inception2Sigs)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": inception2,
                "signatures": inception2Sigs
            }
        ],
        [
            {
                "event": rotation,
                "signatures": rotationSigs
            },
            {
                "event": inception,
                "signatures": inceptionSigs
            }
        ],
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()


def testUpdatePromiscuousEventModeSwitch():
    dbing.setupDbEnv(DB_DIR_PATH)

    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    dbing.eventsDB.saveEvent(DID, inception, inceptionSigs)

    dbing.createDBWrappers(mode="promiscuous")

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = dbing.eventsDB.saveEvent(DID, rotation, rotationSigs)

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": rotation,
                "signatures": rotationSigs
            },
            {
                "event": inception,
                "signatures": inceptionSigs
            }
        ]
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()


def testUpdateWithHackedEventPromiscuousModeSwitch():
    dbing.setupDbEnv(DB_DIR_PATH)
    
    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    dbing.eventsDB.saveEvent(DID, inception, inceptionSigs)

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = dbing.eventsDB.saveEvent(DID, rotation, rotationSigs)

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": rotation,
                "signatures": rotationSigs
            },
            {
                "event": inception,
                "signatures": inceptionSigs
            }
        ]
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()

    # Try updating events with hacked DID
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    inception2 = json.loads(body)
    inception2["id"] = DID
    inception2Sigs = [didery.crypto.eddsa.signResource(json.dumps(inception2).encode(), sk)]

    dbing.createDBWrappers(mode="promiscuous")
    returned_data = dbing.eventsDB.saveEvent(DID, inception2, inception2Sigs)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": inception2,
                "signatures": inception2Sigs
            }
        ],
        [
            {
                "event": rotation,
                "signatures": rotationSigs
            },
            {
                "event": inception,
                "signatures": inceptionSigs
            }
        ],
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()


def testCreateRaceEvent(raceEventsDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    raceEventsDB.saveEvent(DID, data, sigs)

    exp_data = [
        [
            {
                "event": data,
                "signatures": sigs
            },
        ]
    ]

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()


def testUpdateRaceEvent(raceEventsDB):
    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    raceEventsDB.saveEvent(DID, inception, inceptionSigs)

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = raceEventsDB.saveEvent(DID, rotation, rotationSigs)

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": rotation,
                "signatures": rotationSigs
            },
            {
                "event": inception,
                "signatures": inceptionSigs
            },
        ]
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()


def testUpdatePromiscuousEventInRaceMode():
    dbing.setupDbEnv(DB_DIR_PATH, mode="promiscuous")

    # Try updating events with hacked DID
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    inception2 = json.loads(body)
    inception2["id"] = DID
    inception2Sigs = [didery.crypto.eddsa.signResource(json.dumps(inception2).encode(), sk)]

    dbing.eventsDB.saveEvent(DID, inception2, inception2Sigs)

    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    returned_data = dbing.eventsDB.saveEvent(DID, inception, inceptionSigs)

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": inception,
                "signatures": inceptionSigs
            }
        ],
        [
            {
                "event": inception2,
                "signatures": inception2Sigs
            }
        ],
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()

    # Try updating events with hacked DID
    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    dbing.createDBWrappers(mode="race")
    returned_data = dbing.eventsDB.saveEvent(DID, rotation, rotationSigs)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": rotation,
                "signatures": rotationSigs
            },
            {
                "event": inception,
                "signatures": inceptionSigs
            }
        ],
        [
            {
                "event": inception2,
                "signatures": inception2Sigs
            }
        ]
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()


def testCreateMethodEvent(methodEventsDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    methodEventsDB.saveEvent(DID, data, sigs)

    exp_data = [
        [
            {
                "event": data,
                "signatures": sigs
            },
        ]
    ]

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()


def testUpdateMethodEvent(methodEventsDB):
    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    methodEventsDB.saveEvent(DID, inception, inceptionSigs)

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK),
                    didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = methodEventsDB.saveEvent(DID, rotation, rotationSigs)

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": rotation,
                "signatures": rotationSigs
            },
            {
                "event": inception,
                "signatures": inceptionSigs
            },
        ]
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()


def testUpdatePromiscuousEventInMethodMode():
    dbing.setupDbEnv(DB_DIR_PATH, mode="promiscuous")

    # Try updating events with hacked DID
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    inception2 = json.loads(body)
    inception2["id"] = DID
    inception2Sigs = [didery.crypto.eddsa.signResource(json.dumps(inception2).encode(), sk)]

    dbing.eventsDB.saveEvent(DID, inception2, inception2Sigs)

    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    returned_data = dbing.eventsDB.saveEvent(DID, inception, inceptionSigs)

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": inception,
                "signatures": inceptionSigs
            }
        ],
        [
            {
                "event": inception2,
                "signatures": inception2Sigs
            }
        ]
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()

    # Try updating events with hacked DID
    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    dbing.createDBWrappers(mode="method")
    returned_data = dbing.eventsDB.saveEvent(DID, rotation, rotationSigs)

    with dbing.dideryDB.begin(db=dbEvents, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        [
            {
                "event": rotation,
                "signatures": rotationSigs
            },
            {
                "event": inception,
                "signatures": inceptionSigs
            },
        ]
    ]

    assert actual_data == json.dumps(returned_data).encode()
    assert returned_data == exp_result
    assert actual_data == json.dumps(exp_result).encode()


def testCreatePromsicuousHistory(promiscuousHistoryDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    returned_data = promiscuousHistoryDB.saveHistory(DID, data, sigs)

    exp_data = [
        {
            "history": data,
            "signatures": sigs
        }
    ]

    dbHistory = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistory, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()
    assert returned_data == exp_data


def testUpdatePromiscuousHistory(promiscuousHistoryDB):
    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    promiscuousHistoryDB.saveHistory(DID, inception, inceptionSigs)

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = promiscuousHistoryDB.saveHistory(DID, rotation, rotationSigs)

    dbHistories = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": rotation,
            "signatures": rotationSigs
        }
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result

    # Try updating events with hacked DID
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    inception2 = json.loads(body)
    inception2["id"] = DID
    inception2Sigs = [didery.crypto.eddsa.signResource(json.dumps(inception2).encode(), sk)]

    returned_data = promiscuousHistoryDB.saveHistory(DID, inception2, inception2Sigs)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": inception2,
            "signatures": inception2Sigs
        },
        {
            "history": rotation,
            "signatures": rotationSigs
        },
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result


def testUpdatePromiscuousHistoryModeSwitch():
    dbing.setupDbEnv(DB_DIR_PATH)

    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    dbing.historyDB.saveHistory(DID, inception, inceptionSigs)

    dbing.createDBWrappers(mode="promiscuous")

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = dbing.historyDB.saveHistory(DID, rotation, rotationSigs)

    dbHistory = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistory, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": rotation,
            "signatures": rotationSigs
        }
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result


def testUpdateWithHackedHistoryPromiscuousModeSwitch():
    dbing.setupDbEnv(DB_DIR_PATH)

    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    dbing.historyDB.saveHistory(DID, inception, inceptionSigs)

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = dbing.historyDB.saveHistory(DID, rotation, rotationSigs)

    dbHistories = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": rotation,
            "signatures": rotationSigs
        },
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result

    # Try updating events with hacked DID
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    inception2 = json.loads(body)
    inception2["id"] = DID
    inception2Sigs = [didery.crypto.eddsa.signResource(json.dumps(inception2).encode(), sk)]

    dbing.createDBWrappers(mode="promiscuous")
    returned_data = dbing.historyDB.saveHistory(DID, inception2, inception2Sigs)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": inception2,
            "signatures": inception2Sigs
        },
        {
            "history": rotation,
            "signatures": rotationSigs
        },
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result


def testCreateRaceHistory(raceHistoryDB):
    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    returned_data = raceHistoryDB.saveHistory(DID, data, sigs)

    exp_data = [
        {
            "history": data,
            "signatures": sigs
        }
    ]

    dbHistory = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistory, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()
    assert returned_data == exp_data


def testUpdateRaceHistory(raceHistoryDB):
    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    raceHistoryDB.saveHistory(DID, inception, inceptionSigs)

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = raceHistoryDB.saveHistory(DID, rotation, rotationSigs)

    dbHistories = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": rotation,
            "signatures": rotationSigs
        }
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result

    # Try updating history with hacked DID
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    inception2 = json.loads(body)
    inception2["id"] = DID
    inception2Sigs = [didery.crypto.eddsa.signResource(json.dumps(inception2).encode(), sk)]

    returned_data = raceHistoryDB.saveHistory(DID, inception2, inception2Sigs)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": inception2,
            "signatures": inception2Sigs
        },
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result


def testUpdateRaceHistoryModeSwitch():
    dbing.setupDbEnv(DB_DIR_PATH)

    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    dbing.historyDB.saveHistory(DID, inception, inceptionSigs)

    dbing.createDBWrappers(mode="race")

    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = dbing.historyDB.saveHistory(DID, rotation, rotationSigs)

    dbHistory = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistory, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": rotation,
            "signatures": rotationSigs
        }
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result


def testUpdateWithHackedHistoryRaceModeSwitch():
    dbing.setupDbEnv(DB_DIR_PATH)
    dbing.createDBWrappers(mode="promiscuous")

    # Try updating events with hacked DID
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    inception2 = json.loads(body)
    inception2["id"] = DID
    inception2Sigs = [didery.crypto.eddsa.signResource(json.dumps(inception2).encode(), sk)]

    dbing.historyDB.saveHistory(DID, inception2, inception2Sigs)

    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    returned_data = dbing.historyDB.saveHistory(DID, inception, inceptionSigs)

    dbHistories = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": inception,
            "signatures": inceptionSigs
        },
        {
            "history": inception2,
            "signatures": inception2Sigs
        },
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result

    # Switch modes
    dbing.createDBWrappers(mode="race")
    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = dbing.historyDB.saveHistory(DID, rotation, rotationSigs)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": rotation,
            "signatures": rotationSigs
        },
        {
            "history": inception2,
            "signatures": inception2Sigs
        },
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result


def testRaceModeUpdatesMostRecentlyChanged():
    dbing.setupDbEnv(DB_DIR_PATH)
    dbing.createDBWrappers(mode="promiscuous")

    inception = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    inceptionSigs = [didery.crypto.eddsa.signResource(json.dumps(inception).encode(), SK)]

    dbing.historyDB.saveHistory(DID, inception, inceptionSigs)

    # Try updating events with hacked DID
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    inception2 = json.loads(body)
    inception2["id"] = DID
    inception2Sigs = [didery.crypto.eddsa.signResource(json.dumps(inception2).encode(), sk)]

    returned_data = dbing.historyDB.saveHistory(DID, inception2, inception2Sigs)

    dbHistories = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": inception2,
            "signatures": inception2Sigs
        },
        {
            "history": inception,
            "signatures": inceptionSigs
        },
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result

    # Switch modes
    dbing.createDBWrappers(mode="race")
    rotation = {
        "id": DID,
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    rotationSigs = [didery.crypto.eddsa.signResource(json.dumps(rotation).encode(), SK)]

    returned_data = dbing.historyDB.saveHistory(DID, rotation, rotationSigs)

    with dbing.dideryDB.begin(db=dbHistories, write=False) as txn:
        actual_data = txn.get(DID.encode())

    exp_result = [
        {
            "history": rotation,
            "signatures": rotationSigs
        },
        {
            "history": inception,
            "signatures": inceptionSigs
        },
    ]

    assert actual_data == json.dumps(exp_result).encode()
    assert returned_data == exp_result


def testBaseHistoryDBInit():
    db = dbing.DB(dbing.DB_KEY_HISTORY_NAME)
    histroryDB = dbing.BaseHistoryDB(db)

    assert type(histroryDB) == dbing.BaseHistoryDB


def testBaseEventsDBInit():
    db = dbing.DB(dbing.DB_EVENT_HISTORY_NAME)
    eventsDB = dbing.BaseEventsDB(db)

    assert type(eventsDB) == dbing.BaseEventsDB


def testBaseBlobDBInit():
    db = dbing.DB(dbing.DB_OTP_BLOB_NAME)
    blobDB = dbing.BaseBlobDB(db)

    assert type(blobDB) == dbing.BaseBlobDB


def testBaseEventsDBSaveNew():
    dbing.setupDbEnv(DB_DIR_PATH)
    dbing.createDBWrappers(mode="BaseEventsDB")

    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    returned_data = dbing.eventsDB.saveEvent(DID, data, sigs)

    exp_data = [
        [
            {
                "event": data,
                "signatures": sigs
            }
        ]
    ]

    dbEvents = dbing.dideryDB.open_db(dbing.DB_EVENT_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbEvents, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()
    assert returned_data == exp_data
