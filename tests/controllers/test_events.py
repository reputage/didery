import falcon
import libnacl
import pytest

try:
    import simplejson as json
except ImportError:
    import json

import didery.crypto.eddsa as eddsa
import didery.crypto.ecdsa as ecdsa
import tests.testing_utils.utils

from didery.routing import *
from didery.help import helping as h
from didery.db import dbing as db


class TestEventsMethodMode:
    def testGet(self, client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        response = client.simulate_get("{}/{}".format(EVENTS_BASE_PATH, did))

        exp_result = [
            [
                {
                    "event": json.loads(body.decode()),
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        ]

        assert response.status == falcon.HTTP_200
        assert json.loads(response.content) == exp_result

    def testGetNonExistent(self, client):
        did = "did:dad:_j2Iy5Akv0kCR2xLD45YB3gC7DASTU68tGilx5peZ3w="

        response = client.simulate_get("{}/{}".format(EVENTS_BASE_PATH, did))

        assert response.status == falcon.HTTP_404

    def testGetAll(self, client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk2 = h.bytesToStr64u(vk2)

        signature2 = eddsa.signResource(body2, sk2)

        headers2 = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        client.simulate_post(HISTORY_BASE_PATH, body=body2, headers=headers2)

        response = client.simulate_get(EVENTS_BASE_PATH)

        exp_result = {
            "data": [
                [
                    [
                        {
                            "event": json.loads(body.decode()),
                            "signatures": {
                                "signer": signature
                            }
                        }
                    ]
                ],
                [
                    [
                        {
                            "event": json.loads(body2.decode()),
                            "signatures": {
                                "signer": signature2
                            }
                        }
                    ]
                ]
            ]
        }

        response_data = json.loads(response.content)
        assert response.status == falcon.HTTP_200
        assert len(response_data["data"]) == 2
        # response_data order is unreliable
        # make sure that each history exists only once in response
        for result in exp_result['data']:
            matches = 0
            for data in response_data['data']:
                if data == result:
                    matches += 1

            assert matches == 1

    def testGetAllMultiEvent(self, client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        body2 = json.loads(body)
        body2['changed'] = "2000-01-01T00:00:01+00:00"
        body2['signer'] = 1
        body2['signers'].append(vk)
        body2 = json.dumps(body2).encode()

        signer = eddsa.signResource(body2, sk)
        rotation = eddsa.signResource(body2, sk)

        headers = {
            "Signature": 'signer="{0}"; rotation="{1}"'.format(signer, rotation)
        }

        response = client.simulate_put("{}/{}".format(HISTORY_BASE_PATH, did), body=body2, headers=headers)

        assert response.status == falcon.HTTP_200

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk3, sk3, did3, body3 = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk3 = h.bytesToStr64u(vk3)

        signature3 = eddsa.signResource(body3, sk3)

        headers3 = {
            "Signature": 'signer="{0}"'.format(signature3)
        }

        client.simulate_post(HISTORY_BASE_PATH, body=body3, headers=headers3)

        response = client.simulate_get(EVENTS_BASE_PATH)

        exp_result = {
            "data": [
                [
                    [
                        {
                            "event": json.loads(body2.decode()),
                            "signatures": {
                                "signer": signer,
                                "rotation": rotation
                            }
                        },
                        {
                            "event": json.loads(body.decode()),
                            "signatures": {
                                "signer": signature
                            }
                        }
                    ]
                ],
                [
                    [
                        {
                            "event": json.loads(body3.decode()),
                            "signatures": {
                                "signer": signature3
                            }
                        }
                    ]
                ]
            ]
        }

        response_data = json.loads(response.content)
        assert response.status == falcon.HTTP_200
        assert len(response_data["data"]) == 2
        # response_data order is unreliable
        # make sure that each history exists only once in response
        for result in exp_result['data']:
            matches = 0
            for data in response_data['data']:
                if data == result:
                    matches += 1

            assert matches == 1

    def testGetAllEmptyDB(self, client):
        response = client.simulate_get(EVENTS_BASE_PATH)

        assert response.status == falcon.HTTP_200
        assert json.loads(response.content) == {"data": []}


class TestEventsPromiscuousMode:
    @pytest.fixture(autouse=True)
    def setupTearDown(self):
        """

        Pytest runs this function before every test when autouse=True
        Without autouse=True you would have to add a setupTeardown parameter
        to each test function

        """
        # setup
        dbPath = h.setupTmpBaseDir()
        db.setupDbEnv(dbPath, mode="promiscuous")

        yield dbPath  # this allows the test to run

        # teardown
        h.cleanupTmpBaseDir(dbPath)

    def testGet(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        response = promiscuous_client.simulate_get("{}/{}".format(EVENTS_BASE_PATH, did))

        exp_result = [
            [
                {
                    "event": json.loads(body.decode()),
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        ]

        assert response.status == falcon.HTTP_200
        assert json.loads(response.content) == exp_result

    def testGetHacked(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        assert response.status == falcon.HTTP_201

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk2 = h.bytesToStr64u(vk2)

        body2 = json.loads(body2)
        body2["id"] = did
        body2 = json.dumps(body2).encode()

        signature2 = eddsa.signResource(body2, sk2)

        headers2 = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body2, headers=headers2)

        assert response.status == falcon.HTTP_201

        response = promiscuous_client.simulate_get("{}/{}".format(EVENTS_BASE_PATH, did))

        exp_result = [
            [
                {
                    "event": json.loads(body2.decode()),
                    "signatures": {
                        "signer": signature2
                    }
                }
            ],
            [
                {
                    "event": json.loads(body.decode()),
                    "signatures": {
                        "signer": signature
                    }
                }
            ],
        ]

        assert response.status == falcon.HTTP_200
        assert json.loads(response.content) == exp_result

    def testGetNonExistent(self, promiscuous_client):
        did = "did:dad:_j2Iy5Akv0kCR2xLD45YB3gC7DASTU68tGilx5peZ3w="

        response = promiscuous_client.simulate_get("{}/{}".format(EVENTS_BASE_PATH, did))

        assert response.status == falcon.HTTP_404

    def testGetAll(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk2 = h.bytesToStr64u(vk2)

        signature2 = eddsa.signResource(body2, sk2)

        headers2 = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body2, headers=headers2)

        response = promiscuous_client.simulate_get(EVENTS_BASE_PATH)

        exp_result = {
            "data": [
                [
                    [
                        {
                            "event": json.loads(body.decode()),
                            "signatures": {
                                "signer": signature
                            }
                        }
                    ]
                ],
                [
                    [
                        {
                            "event": json.loads(body2.decode()),
                            "signatures": {
                                "signer": signature2
                            }
                        }
                    ]
                ]
            ]
        }

        response_data = json.loads(response.content)
        assert response.status == falcon.HTTP_200
        assert len(response_data["data"]) == 2
        # response_data order is unreliable
        # make sure that each history exists only once in response
        for result in exp_result['data']:
            matches = 0
            for data in response_data['data']:
                if data == result:
                    matches += 1

            assert matches == 1

    def testGetAllMultiEvent(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        assert response.status == falcon.HTTP_201

        body2 = json.loads(body)
        body2['changed'] = "2000-01-01T00:00:01+00:00"
        body2['signer'] = 1
        body2['signers'].append(vk)
        body2 = json.dumps(body2).encode()

        signer = eddsa.signResource(body2, sk)
        rotation = eddsa.signResource(body2, sk)

        headers = {
            "Signature": 'signer="{0}"; rotation="{1}"'.format(signer, rotation)
        }

        response = promiscuous_client.simulate_put("{}/{}".format(HISTORY_BASE_PATH, did), body=body2, headers=headers)

        assert response.status == falcon.HTTP_200

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk3, sk3, did3, body3 = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk3 = h.bytesToStr64u(vk3)

        signature3 = eddsa.signResource(body3, sk3)

        headers3 = {
            "Signature": 'signer="{0}"'.format(signature3)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body3, headers=headers3)

        assert response.status == falcon.HTTP_201

        response = promiscuous_client.simulate_get(EVENTS_BASE_PATH)

        exp_result = {
            "data": [
                [
                    [
                        {
                            "event": json.loads(body2.decode()),
                            "signatures": {
                                "signer": signer,
                                "rotation": rotation
                            }
                        },
                        {
                            "event": json.loads(body.decode()),
                            "signatures": {
                                "signer": signature
                            }
                        }
                    ]
                ],
                [
                    [
                        {
                            "event": json.loads(body3.decode()),
                            "signatures": {
                                "signer": signature3
                            }
                        }
                    ]
                ]
            ]
        }

        response_data = json.loads(response.content)
        assert response.status == falcon.HTTP_200
        assert len(response_data["data"]) == 2
        # response_data order is unreliable
        # make sure that each history exists only once in response
        for result in exp_result['data']:
            matches = 0
            for data in response_data['data']:
                if data == result:
                    matches += 1

            assert matches == 1

    def testGetAllHacked(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        assert response.status == falcon.HTTP_201

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk2 = h.bytesToStr64u(vk2)

        body2 = json.loads(body2)
        body2["id"] = did
        body2 = json.dumps(body2).encode()

        signature2 = eddsa.signResource(body2, sk2)

        headers2 = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body2, headers=headers2)

        assert response.status == falcon.HTTP_201

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk3, sk3, did3, body3 = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk3 = h.bytesToStr64u(vk3)

        signature3 = eddsa.signResource(body3, sk3)

        headers3 = {
            "Signature": 'signer="{0}"'.format(signature3)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body3, headers=headers3)

        assert response.status == falcon.HTTP_201

        response = promiscuous_client.simulate_get(EVENTS_BASE_PATH)

        exp_result = {
            "data": [
                [
                    [
                        {
                            "event": json.loads(body2.decode()),
                            "signatures": {
                                "signer": signature2
                            }
                        }
                    ],
                    [
                        {
                            "event": json.loads(body.decode()),
                            "signatures": {
                                "signer": signature
                            }
                        }
                    ],
                ],
                [
                    [
                        {
                            "event": json.loads(body3.decode()),
                            "signatures": {
                                "signer": signature3
                            }
                        }
                    ]
                ]
            ]
        }

        response_data = json.loads(response.content)
        assert response.status == falcon.HTTP_200
        assert len(response_data["data"]) == 2
        # response_data order is unreliable
        # make sure that each history exists only once in response
        for result in exp_result['data']:
            matches = 0
            for data in response_data['data']:
                if data == result:
                    matches += 1

            assert matches == 1

    def testGetAllEmptyDB(self, promiscuous_client):
        response = promiscuous_client.simulate_get(EVENTS_BASE_PATH)

        assert response.status == falcon.HTTP_200
        assert json.loads(response.content) == {"data": []}


class TestEventsRaceMode:
    @pytest.fixture(autouse=True)
    def setupTearDown(self):
        """

        Pytest runs this function before every test when autouse=True
        Without autouse=True you would have to add a setupTeardown parameter
        to each test function

        """
        # setup
        dbPath = h.setupTmpBaseDir()
        db.setupDbEnv(dbPath, mode="race")

        yield dbPath  # this allows the test to run

        # teardown
        h.cleanupTmpBaseDir(dbPath)

    def testGet(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        race_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        response = race_client.simulate_get("{}/{}".format(EVENTS_BASE_PATH, did))

        exp_result = [
            [
                {
                    "event": json.loads(body.decode()),
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        ]

        assert response.status == falcon.HTTP_200
        assert json.loads(response.content) == exp_result

    def testGetNonExistent(self, race_client):
        did = "did:dad:_j2Iy5Akv0kCR2xLD45YB3gC7DASTU68tGilx5peZ3w="

        response = race_client.simulate_get("{}/{}".format(EVENTS_BASE_PATH, did))

        assert response.status == falcon.HTTP_404

    def testGetAll(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        race_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk2 = h.bytesToStr64u(vk2)

        signature2 = eddsa.signResource(body2, sk2)

        headers2 = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        race_client.simulate_post(HISTORY_BASE_PATH, body=body2, headers=headers2)

        response = race_client.simulate_get(EVENTS_BASE_PATH)

        exp_result = {
            "data": [
                [
                    [
                        {
                            "event": json.loads(body.decode()),
                            "signatures": {
                                "signer": signature
                            }
                        }
                    ]
                ],
                [
                    [
                        {
                            "event": json.loads(body2.decode()),
                            "signatures": {
                                "signer": signature2
                            }
                        }
                    ]
                ]
            ]
        }

        response_data = json.loads(response.content)
        assert response.status == falcon.HTTP_200
        assert len(response_data["data"]) == 2
        # response_data order is unreliable
        # make sure that each history exists only once in response
        for result in exp_result['data']:
            matches = 0
            for data in response_data['data']:
                if data == result:
                    matches += 1

            assert matches == 1

    def testGetAllMultiEvent(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        race_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        body2 = json.loads(body)
        body2['changed'] = "2000-01-01T00:00:01+00:00"
        body2['signer'] = 1
        body2['signers'].append(vk)
        body2 = json.dumps(body2).encode()

        signer = eddsa.signResource(body2, sk)
        rotation = eddsa.signResource(body2, sk)

        headers = {
            "Signature": 'signer="{0}"; rotation="{1}"'.format(signer, rotation)
        }

        response = race_client.simulate_put("{}/{}".format(HISTORY_BASE_PATH, did), body=body2, headers=headers)

        assert response.status == falcon.HTTP_200

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk3, sk3, did3, body3 = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk3 = h.bytesToStr64u(vk3)

        signature3 = eddsa.signResource(body3, sk3)

        headers3 = {
            "Signature": 'signer="{0}"'.format(signature3)
        }

        race_client.simulate_post(HISTORY_BASE_PATH, body=body3, headers=headers3)

        response = race_client.simulate_get(EVENTS_BASE_PATH)

        exp_result = {
            "data": [
                [
                    [
                        {
                            "event": json.loads(body2.decode()),
                            "signatures": {
                                "signer": signer,
                                "rotation": rotation
                            }
                        },
                        {
                            "event": json.loads(body.decode()),
                            "signatures": {
                                "signer": signature
                            }
                        }
                    ]
                ],
                [
                    [
                        {
                            "event": json.loads(body3.decode()),
                            "signatures": {
                                "signer": signature3
                            }
                        }
                    ]
                ]
            ]
        }

        response_data = json.loads(response.content)
        assert response.status == falcon.HTTP_200
        assert len(response_data["data"]) == 2
        # response_data order is unreliable
        # make sure that each history exists only once in response
        for result in exp_result['data']:
            matches = 0
            for data in response_data['data']:
                if data == result:
                    matches += 1

            assert matches == 1

    def testGetAllEmptyDB(self, race_client):
        response = race_client.simulate_get(EVENTS_BASE_PATH)

        assert response.status == falcon.HTTP_200
        assert json.loads(response.content) == {"data": []}
