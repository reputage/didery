import arrow

try:
    import simplejson as json
except ImportError:
    import json

import didery.crypto.eddsa

from didery.models.models import ValidatedHistoryModel, ValidatedEventsModel, BasicHistoryModel, DataModel
from didery.help import helping as h


SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
VK = b"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
DID = "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="


def testDataModel():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    test_model = DataModel(data)

    assert test_model.data == data


def testDataModelToJson():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    test_model = DataModel(data)

    assert test_model.toJson() == json.dumps(data)


def testDataModelToBytes():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    test_model = DataModel(data)

    assert test_model.toBytes() == json.dumps(data).encode()


def testDataModelFromJson():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    test_model = DataModel({})

    assert test_model.data == {}

    test_model.fromJson(json.dumps(data))

    assert test_model.data == data


def testDataModelFromBytes():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    test_model = DataModel({})

    assert test_model.data == {}

    test_model.fromBytes(json.dumps(data).encode())

    assert test_model.data == data


def testBasicHistoryModel():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }

    test_model = BasicHistoryModel(data)

    assert test_model.data == data
    assert test_model.history == data
    assert test_model.id == DID
    assert test_model.changed == data['changed']
    assert test_model.parsedChanged == arrow.get("2000-01-01T00:00:01+00:00")
    assert test_model.signer == 0
    assert test_model.signers == ["NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
                                  "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="]


def testValidatedHistoryModel():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]
    history = {
        "history": data,
        "signatures": sigs,
    }
    test_data = [
        history
    ]

    test_model = ValidatedHistoryModel(test_data, "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=")

    assert test_model.mode == "method"
    assert test_model.vk == "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
    assert test_model.index == 0
    assert test_model.id == DID
    assert test_model.changed == data['changed']
    assert test_model.parsedChanged == arrow.get("2000-01-01T00:00:01+00:00")
    assert test_model.signer == 0
    assert test_model.signers == ["NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
                                  "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="]
    assert test_model.history == data
    assert test_model.signatures == sigs
    assert test_model.selected == history


def testValidatedHistoryModelSetSelected():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]
    history = {
        "history": data,
        "signatures": sigs,
    }

    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    data2 = json.loads(body)
    data2["id"] = DID
    sigs2 = [didery.crypto.eddsa.signResource(json.dumps(data2).encode(), sk)]

    history2 = {
        "history": data2,
        "signatures": sigs2
    }

    test_data = [
        history,
        history2
    ]

    test_model = ValidatedHistoryModel(test_data, vk)

    assert test_model.vk == vk
    assert test_model.index == 1


def testEmptyValidatedHistoryModel():
    test_model = ValidatedHistoryModel(None)

    assert test_model.vk is None

    vk = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
    test_model.selected = vk

    assert test_model.vk == vk
    assert test_model.index is None


def testValidateHistoryModelUpdate():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]
    history = {
        "history": data,
        "signatures": sigs,
    }
    test_data = [
        history
    ]

    test_model = ValidatedHistoryModel(test_data)

    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    data2 = json.loads(body)
    data2["id"] = DID
    sigs2 = [didery.crypto.eddsa.signResource(json.dumps(data2).encode(), sk)]

    history2 = {
        "history": data2,
        "signatures": sigs2
    }
    test_data = [
        history2
    ]

    test_model.update(0, history2)

    assert test_model.data == test_data


def testValidateHistoryModelUpdateBadIndex():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]
    history = {
        "history": data,
        "signatures": sigs,
    }
    test_data = [
        history
    ]

    test_model = ValidatedHistoryModel(test_data)

    history2 = {}
    outOfRange = 1

    test_model.update(outOfRange, history2)

    assert test_model.data == test_data


def testValidateHistoryModelUpdateNone():
    data = {
        "id": DID,
        "signer": 0,
        "changed": "2000-01-01T00:00:01+00:00",
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]
    history = {
        "history": data,
        "signatures": sigs,
    }
    test_data = [
        history
    ]

    test_model = ValidatedHistoryModel(test_data, "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=")

    history2 = None

    test_model.update(0, history2)

    assert test_model.data == [None]


class TestEventsModel:

    def test_model_creation(self):
        vk = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        data = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk,
                vk
            ]
        }
        sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]
        event_data = {
            "event": data,
            "signatures": sigs,
        }
        test_data = [
            [
                event_data,
                event_data
            ],
            [
                event_data
            ]
        ]

        test_model = ValidatedEventsModel(test_data)

        for events in test_model.data:
            for event in events:
                assert event.data == event_data

    def test_find(self):
        vk1 = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        data1 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk1,
                vk1
            ]
        }
        vk2 = "45NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zS="
        data2 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk2,
                vk2
            ]
        }
        sigs1 = [didery.crypto.eddsa.signResource(json.dumps(data1).encode(), SK)]
        sigs2 = [didery.crypto.eddsa.signResource(json.dumps(data2).encode(), SK)]
        event1 = {
            "event": data1,
            "signatures": sigs1,
        }
        event2 = {
            "event": data2,
            "signatures": sigs2,
        }
        test_data = [
            [
                event1,
                event1
            ],
            [
                event2
            ]
        ]

        test_model = ValidatedEventsModel(test_data)
        index = test_model.find(vk1)

        assert index == 0

        test_model = ValidatedEventsModel(test_data)
        index = test_model.find(vk2)

        assert index == 1

    def test_find_non_existent(self):
        vk = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        data = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk,
                vk
            ]
        }
        sigs = [didery.crypto.eddsa.signResource(json.dumps(data).encode(), SK)]
        event = {
            "event": data,
            "signatures": sigs,
        }

        bad_vk = "45NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zS="

        test_data = [
            [
                event,
                event
            ]
        ]

        test_model = ValidatedEventsModel(test_data)
        index = test_model.find(bad_vk)

        assert index is None

    def test_find_empty_data(self):
        test_data = []
        vk = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

        test_model = ValidatedEventsModel(test_data)
        index = test_model.find(vk)

        assert index is None

        test_model = ValidatedEventsModel(None)
        index = test_model.find(vk)

        assert index is None

    def test_to_dict(self):
        vk1 = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        data1 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk1,
                vk1
            ]
        }
        vk2 = "45NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zS="
        data2 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk2,
                vk2
            ]
        }
        sigs1 = [didery.crypto.eddsa.signResource(json.dumps(data1).encode(), SK)]
        sigs2 = [didery.crypto.eddsa.signResource(json.dumps(data2).encode(), SK)]
        event1 = {
            "event": data1,
            "signatures": sigs1,
        }
        event2 = {
            "event": data2,
            "signatures": sigs2,
        }
        test_data = [
            [
                event1,
                event1
            ],
            [
                event2
            ]
        ]

        test_model = ValidatedEventsModel(test_data)
        data = test_model.to_dict()

        assert data == test_data

    def test_to_list(self):
        vk1 = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        data1 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk1,
                vk1
            ]
        }
        vk2 = "45NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zS="
        data2 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk2,
                vk2
            ]
        }
        sigs1 = [didery.crypto.eddsa.signResource(json.dumps(data1).encode(), SK)]
        sigs2 = [didery.crypto.eddsa.signResource(json.dumps(data2).encode(), SK)]
        event1 = {
            "event": data1,
            "signatures": sigs1,
        }
        event2 = {
            "event": data2,
            "signatures": sigs2,
        }
        test_data = [
            [
                event1,
                event1
            ],
            [
                event2
            ]
        ]

        test_model = ValidatedEventsModel(test_data)
        data = test_model.to_list()

        assert data == test_data

    def test_to_json(self):
        vk1 = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        data1 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk1,
                vk1
            ]
        }
        vk2 = "45NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zS="
        data2 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk2,
                vk2
            ]
        }
        sigs1 = [didery.crypto.eddsa.signResource(json.dumps(data1).encode(), SK)]
        sigs2 = [didery.crypto.eddsa.signResource(json.dumps(data2).encode(), SK)]
        event1 = {
            "event": data1,
            "signatures": sigs1,
        }
        event2 = {
            "event": data2,
            "signatures": sigs2,
        }
        test_data = [
            [
                event1,
                event1
            ],
            [
                event2
            ]
        ]

        test_model = ValidatedEventsModel(test_data)
        data = test_model.toJson()

        assert data == json.dumps(test_data)

    def test_to_bytes(self):
        vk1 = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        data1 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk1,
                vk1
            ]
        }
        vk2 = "45NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zS="
        data2 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk2,
                vk2
            ]
        }
        sigs1 = [didery.crypto.eddsa.signResource(json.dumps(data1).encode(), SK)]
        sigs2 = [didery.crypto.eddsa.signResource(json.dumps(data2).encode(), SK)]
        event1 = {
            "event": data1,
            "signatures": sigs1,
        }
        event2 = {
            "event": data2,
            "signatures": sigs2,
        }
        test_data = [
            [
                event1,
                event1
            ],
            [
                event2
            ]
        ]

        test_model = ValidatedEventsModel(test_data)
        data = test_model.toBytes()

        assert data == json.dumps(test_data).encode()

    def test_from_json(self):
        vk1 = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        data1 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk1,
                vk1
            ]
        }
        sigs1 = [didery.crypto.eddsa.signResource(json.dumps(data1).encode(), SK)]
        event_data = {
            "event": data1,
            "signatures": sigs1,
        }
        test_data = [
            [
                event_data,
                event_data
            ],
            [
                event_data
            ]
        ]

        test_model = ValidatedEventsModel(None)
        test_model.fromJson(json.dumps(test_data))

        for events in test_model.data:
            for event in events:
                assert event.data == event_data

    def test_from_bytes(self):
        vk1 = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        data1 = {
            "id": DID,
            "signer": 0,
            "changed": "2000-01-01T00:00:01+00:00",
            "signers": [
                vk1,
                vk1
            ]
        }
        sigs1 = [didery.crypto.eddsa.signResource(json.dumps(data1).encode(), SK)]
        event_data = {
            "event": data1,
            "signatures": sigs1,
        }
        test_data = [
            [
                event_data,
                event_data
            ],
            [
                event_data
            ]
        ]

        test_model = ValidatedEventsModel(None)
        test_model.fromBytes(json.dumps(test_data).encode())

        for events in test_model.data:
            for event in events:
                assert event.data == event_data
