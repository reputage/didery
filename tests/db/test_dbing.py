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


def testEmptyHistoryCount():
    dbing.setupDbEnv(DB_DIR_PATH)

    count = dbing.historyCount()

    assert count == 0


def testHistoryCount():
    dbing.setupDbEnv(DB_DIR_PATH)

    dbHistory = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistory, write=True) as txn:
        data = b'{"id": "did:dad:-OVHx0sv_jJePGB9LBZaWDlrLkxMNlOeHPdHysViK9k=", "signer": 0, "signers": ["-OVHx0sv_jJePGB9LBZaWDlrLkxMNlOeHPdHysViK9k=", "5Bp8Z8_UOWZBtVxffoTVF3QYkE-W-CpKa6VnN27CcN8="]}'
        id = b'did:dad:-OVHx0sv_jJePGB9LBZaWDlrLkxMNlOeHPdHysViK9k='

        txn.put(id, data)

    count = dbing.historyCount()

    assert count == 1


def testSaveHistory():
    dbing.setupDbEnv(DB_DIR_PATH)

    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    exp_data = dbing.saveHistory(DID, data, sigs)

    dbHistory = dbing.dideryDB.open_db(dbing.DB_KEY_HISTORY_NAME)

    with dbing.dideryDB.begin(db=dbHistory, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()


def testGetHistory():
    dbing.setupDbEnv(DB_DIR_PATH)

    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    exp_data = dbing.saveHistory(DID, data, sigs)

    actual_data = dbing.getHistory(DID)

    assert actual_data == exp_data


def testGetNonExistentHistory():
    dbing.setupDbEnv(DB_DIR_PATH)

    actual_data = dbing.getHistory(DID)

    assert actual_data is None


def testGetAllHistories():
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    dbing.setupDbEnv(DB_DIR_PATH)

    data = {
        "id": DID,
        "signer": 0,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    history1 = dbing.saveHistory(DID, data, sigs)

    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    data = json.loads(body)
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), sk)]

    history2 = dbing.saveHistory(did, data, sigs)

    exp_data = {
        'data': [
            history1,
            history2
        ]
    }

    actual_data = dbing.getAllHistories()

    assert actual_data == exp_data


def testGetAllHistoriesOnEmptyDB():
    dbing.setupDbEnv(DB_DIR_PATH)

    actual_data = dbing.getAllHistories()

    assert actual_data == {'data': []}


def testDeleteHistory():
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    data = json.loads(body)
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), sk)]

    dbing.saveHistory(did, data, sigs)

    status = dbing.deleteHistory(did)

    assert status is True
    assert dbing.getHistory(did) is None


def testDeleteNonExistentHistory():
    status = dbing.deleteHistory(DID)

    assert status is False


def testEmptyOtpCount():
    dbing.setupDbEnv(DB_DIR_PATH)

    count = dbing.otpBlobCount()

    assert count == 0


def testOtpBlobCount():
    dbing.setupDbEnv(DB_DIR_PATH)

    dbOtpBlob = dbing.dideryDB.open_db(dbing.DB_OTP_BLOB_NAME)

    with dbing.dideryDB.begin(db=dbOtpBlob, write=True) as txn:
        data = b'{"id": "did:dad:Y2CR8pS8z2YvJQN-FH_wprtF1TyA0jTlXC3MrMmaNyY=", "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"}'
        id = b'did:dad:Y2CR8pS8z2YvJQN-FH_wprtF1TyA0jTlXC3MrMmaNyY='

        txn.put(id, data)

    count = dbing.otpBlobCount()

    assert count == 1


def testSaveOtpBlob():
    dbing.setupDbEnv(DB_DIR_PATH)

    data = {
        "id": DID,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    exp_data = dbing.saveOtpBlob(DID, data, sigs)

    dbOtpBlob = dbing.dideryDB.open_db(dbing.DB_OTP_BLOB_NAME)

    with dbing.dideryDB.begin(db=dbOtpBlob, write=True) as txn:
        actual_data = txn.get(DID.encode())

    assert actual_data == json.dumps(exp_data).encode()


def testGetOtpBlob():
    dbing.setupDbEnv(DB_DIR_PATH)

    data = {
        "id": DID,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }

    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    exp_data = dbing.saveOtpBlob(DID, data, sigs)

    actual_data = dbing.getOtpBlob(DID)

    assert actual_data == exp_data


def testGetNonExistentOtpBlob():
    dbing.setupDbEnv(DB_DIR_PATH)

    actual_data = dbing.getOtpBlob(DID)

    assert actual_data is None


def testGetAllOtpBlobs():
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    dbing.setupDbEnv(DB_DIR_PATH)

    data = {
        "id": DID,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    otpBlob1 = dbing.saveOtpBlob(DID, data, sigs)

    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    data = {
        "id": did,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), sk)]

    otpBlob2 = dbing.saveOtpBlob(did, data, sigs)

    exp_data = {
        'data': [
            otpBlob1,
            otpBlob2
        ]
    }

    actual_data = dbing.getAllOtpBlobs()

    assert actual_data == exp_data


def testGetAllOtpBlobsOnEmptyDB():
    dbing.setupDbEnv(DB_DIR_PATH)

    actual_data = dbing.getAllOtpBlobs()

    assert actual_data == {'data': []}


def testDeleteOtpBlob():
    data = {
        "id": DID,
        "blob": "aj;skldfjaoisfjweoijfoiajfo;iasjvjncowrnoiarejnfoj;csacivnfgo;afiewvajdfvo;hnafddjio;ahjfgoia;ehroi;hs"
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]

    dbing.saveOtpBlob(DID, data, sigs)

    status = dbing.deleteOtpBlob(DID)

    assert status is True
    assert dbing.getHistory(DID) is None


def testDeleteNonExistentOtpBlob():
    status = dbing.deleteOtpBlob(DID)

    assert status is False
