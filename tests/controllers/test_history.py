'''
    Tests can be run from the terminal with the following command:
        pytest tests/controllers

    To see test coverage install pytest-cov with pip then run this command:
        py.test --cov-report term-missing --cov=src/didery/controllers/ tests/controllers/
'''
import didery.crypto.eddsa as eddsa
import didery.crypto.ecdsa as ecdsa
import falcon
import pytest
import libnacl
import arrow
import urllib.parse

import tests.testing_utils.utils

try:
    import simplejson as json
except ImportError:
    import json

from copy import deepcopy
from falcon import testing
from ioflo.base import storing

from didery.routing import *
from didery.help import helping as h
from didery.db import dbing as db


SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
VK = b"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
DID = "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

verifyRequest = tests.testing_utils.utils.verifyPublicApiRequest
SEED = b'PTi\x15\xd5\xd3`\xf1u\x15}^r\x9bfH\x02l\xc6\x1b\x1d\x1c\x0b9\xd7{\xc0_\xf2K\x93`'
PUT_URL = "{0}/{1}".format(HISTORY_BASE_PATH, DID)
GET_ONE_URL = PUT_URL

postData = {
            "id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "changed": "2000-01-01T00:00:00+00:00",
            "signer": 0,
            "signers": [
                "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
                "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
            ]
       }

putData = {
            "id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "changed": "2000-01-01T00:00:00+00:00",
            "signer": 1,
            "signers": [
                "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
                "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
            ]
       }


def setupBasicHistory(client, numSigners=2):
    # Setup
    # seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=numSigners)
    vk = h.bytesToStr64u(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    return vk, sk, did, body


def setupRevokedHistory(client):
    vk, sk, did, body = setupBasicHistory(client)

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 2
    body['signers'].append(None)

    signature = eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            signature,
            signature)
    }

    client.simulate_put("{}/{}".format(HISTORY_BASE_PATH, did), body=json.dumps(body).encode(), headers=headers)

    return vk, sk, did, body


def testKeyRevocation(client):
    vk, sk, did, body = setupBasicHistory(client)

    # Test Key Revocation
    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 2
    body['signers'].append(None)

    signature = eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            signature,
            signature)
    }

    exp_result = [
        {
            "history": {
                "id": did,
                "changed": "2000-01-01T00:00:01+00:00",
                "signer": 2,
                "signers": [
                    vk,
                    vk,
                    None
                ]
            },
            "signatures": {
                "signer": signature,
                "rotation": signature
            }
        }
    ]

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_200)


def testKeyRevocationExtendedSigners(client):
    vk, sk, did, body = setupBasicHistory(client, numSigners=6)

    # Test Key Revocation
    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 6
    body['signers'].append(None)

    signature = eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            signature,
            signature)
    }

    exp_result = [
        {
            "history": {
                "id": did,
                "changed": "2000-01-01T00:00:01+00:00",
                "signer": 6,
                "signers": [
                    vk,
                    vk,
                    vk,
                    vk,
                    vk,
                    vk,
                    None
                ]
            },
            "signatures": {
                "signer": signature,
                "rotation": signature
            }
        }
    ]

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_200)


def testRotateNullKey(client):
    vk, sk, did, body = setupRevokedHistory(client)

    # try to rotate away from the null key
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 3
    body['signers'].append(vk)
    body['signers'].append(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "signers keys cannot be null unless revoking a key."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)

    # try to rotate away from the null key
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 4
    body['signers'].append(vk)
    body['signers'].append(vk)
    body['signers'].append(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "signers keys cannot be null unless revoking a key."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def testPrematureNullRotation(client):
    vk, sk, did, body = setupBasicHistory(client)

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 4
    body['signers'].append(None)
    body['signers'].append(None)
    body['signers'].append(None)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "signers keys cannot be null unless revoking a key."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def testPutPreRotationIsNull(client):
    vk, sk, did, body = setupBasicHistory(client)

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 1
    body['signers'].append(None)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "signers keys cannot be null unless revoking a key."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def testPutPreRotationIsEmpty(client):
    vk, sk, did, body = setupBasicHistory(client)

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 1
    body['signers'].append("")

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "signers keys cannot be empty."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def basicValidation(reqFunc, url, data):
    # Test missing id field
    body = deepcopy(data)
    del body['id']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain id field."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing changed field
    body = deepcopy(data)
    del body['changed']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain changed field."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing signer field
    body = deepcopy(data)
    del body['signer']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain signer field."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing signers field
    body = deepcopy(data)
    del body['signers']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain signers field."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test empty id field
    body = deepcopy(data)
    body['id'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "id field cannot be empty."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test empty changed field
    body = deepcopy(data)
    body['changed'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "changed field cannot be empty."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test invalid signers value
    body = deepcopy(data)
    body['signers'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "signers field must be a list or array."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signer field is an int
    body = deepcopy(data)
    body['signer'] = "a"

    exp_result = {
        "title": "Validation Error",
        "description": "signer field must be a number."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that changed field is a valid ISO date
    body = deepcopy(data)
    body['changed'] = "01-01T00:00:00+00:00"

    exp_result = {
        "title": "Validation Error",
        "description": "ISO datetime could not be parsed."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testValidPost(client):
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)

    signature = eddsa.signResource(body, sk)

    headers = {
        "Signature": 'signer="{0}"'.format(signature)
    }

    exp_result = [
        {
            "history": json.loads(body.decode()),
            "signatures": {
                "signer": signature
            }
        }
    ]

    verifyRequest(client.simulate_post,
                  HISTORY_BASE_PATH,
                  json.loads(body.decode()),
                  headers=headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_201)


def testPostPreRotationIsNull(client):
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)

    body = json.loads(body)
    body['signers'][1] = None
    body = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    exp_result = {
        "title": "Validation Error",
        "description": "signers keys cannot be null on inception."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testPostPreRotationIsEmpty(client):
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)

    body = json.loads(body)
    body['signers'][1] = ""
    body = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    exp_result = {
        "title": "Validation Error",
        "description": "signers keys cannot be empty."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testPostEmptySignatureHeader(client):
    headers = {"Signature": ""}

    body = deepcopy(postData)
    body = json.dumps(body, ensure_ascii=False).encode('utf-8')

    exp_result = {
        "title": "Authorization Error",
        "description": "Empty Signature header."
    }

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
    assert response.status == falcon.HTTP_401
    assert json.loads(response.content) == exp_result


def testPostMissingSignatureHeader(client):
    body = deepcopy(postData)
    body = json.dumps(body, ensure_ascii=False).encode('utf-8')

    exp_result = {
        "title": "Missing header value",
        "description": "The Signature header is required."
    }

    response = client.simulate_post(HISTORY_BASE_PATH, body=body)
    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testPostMissingSignerTag(client):
    body = deepcopy(postData)

    headers = {
        "Signature": 'test="' + eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), SK) + '"'
    }

    exp_result = {
        "title": "Authorization Error",
        "description": "Signature header missing signature for \"signer\"."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, headers, exp_result, falcon.HTTP_401)


def testPostInvalidSignature(client):
    body = deepcopy(postData)
    body['signers'][0] = "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for signer field. Unverifiable signature."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_401)


def testPostDIDAndPublicKeyMatch(client):
    # SECURITY:
    # Test the public key in the id field did matches the first public key in rotation history
    body = deepcopy(postData)
    body['id'] = "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error",
        "description": "The first key in the signers field does not belong to this DID."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPostValidation(client):
    # Run basic validation tests
    basicValidation(client.simulate_post, HISTORY_BASE_PATH, postData)


def testPostPartialDid(client):
    body = deepcopy(postData)
    body['id'] = "did:fake"

    exp_result = {
        "title": "Validation Error",
        "description": "Invalid did format. Could not parse DID."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPostInvalidDidScheme(client):
    body = deepcopy(postData)
    body['id'] = "fake:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error", "description": "Invalid did format. Invalid Scheme Value."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPostEmptyPreRotation(client):
    # Test that signers field requires two keys
    body = deepcopy(postData)
    body['signers'] = ["Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="]

    exp_result = {
        "title": "Validation Error",
        "description": "Missing pre rotated key in \"signers\" field."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPostEmptySignersField(client):
    # Test that signers field requires two keys
    body = deepcopy(postData)
    body['signers'] = []

    exp_result = {
        "title": "Validation Error",
        "description": "signers field cannot be empty."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPostValidSignersField(client):
    body = deepcopy(postData)
    body['signers'] = ["NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="]

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_status=falcon.HTTP_201)


def testPostSignerIsZero(client):
    # Test that signer field is a valid index into signers field
    body = deepcopy(postData)
    body['signer'] = 4

    exp_result = {
        "title": "Validation Error",
        "description": "signer field must equal 0 on creation of new rotation history."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPostRouting(client):
    # Test that server doesn't crash if anything is added after /history
    body = deepcopy(postData)
    path = "{0}/{1}".format(HISTORY_BASE_PATH, "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=")

    verifyRequest(client.simulate_post, path, body, exp_status=falcon.HTTP_404)


def testPutUrlDIDAndIdDIDMatch(client):
    body = deepcopy(putData)
    body['id'] = "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error",
        "description": "Url did must match id field did."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutUrlDIDAndIdDIDDifferentReferences(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    # Test Valid rotation event
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    body = json.loads(body)
    body["id"] = did + "/some/path?query=true#fragment"
    body = json.dumps(body).encode()

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 1
    body['signers'].append(body['signers'][0])

    signer = eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)
    rotation = eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(signer, rotation)
    }

    exp_result = [
        {
            "history": {
                "id": did + "/some/path?query=true#fragment",
                "changed": "2000-01-01T00:00:01+00:00",
                "signer": 1,
                "signers": [
                    "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
                    "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
                    "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
                ]
            },
            "signatures": {
                "signer": signer,
                "rotation": rotation
            }
        }
    ]

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_200)


def testPutEmptySignatureHeader(client):
    headers = {"Signature": ""}
    body = deepcopy(putData)

    exp_result = {
        "title": "Authorization Error",
        "description": "Empty Signature header."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, headers, exp_result, falcon.HTTP_401)


def testPutMissingSignatureHeader(client):
    body = deepcopy(putData)

    exp_result = {
        "title": "Missing header value",
        "description": "The Signature header is required."
    }

    response = client.simulate_put(PUT_URL, body=json.dumps(body, ensure_ascii=False).encode('utf-8'))
    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testPutMissingRotationSignature(client):
    body = deepcopy(putData)

    headers = {
        "Signature": 'signer="' + eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), SK) + '"'
    }

    exp_result = {
        "title": "Authorization Error",
        "description": "Signature header missing signature for \"rotation\"."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, headers, exp_result, falcon.HTTP_401)


def testPutMissingSignerSignature(client):
    body = deepcopy(putData)
    headers = {
        "Signature": 'rotation="' + eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), SK) + '"'
    }

    exp_result = {
        "title": "Authorization Error",
        "description": "Signature header missing signature for \"signer\"."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, headers, exp_result, falcon.HTTP_401)


def testPutInvalidSignerSignature(client):
    body = deepcopy(putData)
    body['signers'][1] = "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148="

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for rotation field. Unverifiable signature."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_401)


def testPutInvalidRotationSignature(client):
    body = deepcopy(putData)
    body['signers'][0] = "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
    body['signers'][1] = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for signer field. Unverifiable signature."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_401)


def testPutCryptography(client):
    # validate that signer and rotation signature fields are working correctly
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk = libnacl.crypto_sign_seed_keypair(seed)
    pvk, psk = libnacl.crypto_sign_seed_keypair(seed)
    ppvk, ppsk = libnacl.crypto_sign_seed_keypair(seed)

    did = h.makeDid(vk)
    vk = h.bytesToStr64u(vk)
    pvk = h.bytesToStr64u(pvk)
    ppvk = h.bytesToStr64u(ppvk)
    body = {
        "id": did,
        "changed": str(arrow.utcnow()),
        "signer": 0,
        "signers": [vk, pvk]
    }
    bbody = json.dumps(body, ensure_ascii=False).encode('utf-8')
    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(bbody, sk))
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, headers=headers, exp_status=falcon.HTTP_201)

    body['signer'] = 1
    body['changed'] = str(arrow.utcnow())
    body['signers'].append(ppvk)
    bbody = json.dumps(body, ensure_ascii=False).encode('utf-8')
    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(bbody, sk),
                                                           eddsa.signResource(bbody, psk))
    }
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    verifyRequest(client.simulate_put, url, body, headers=headers, exp_status=falcon.HTTP_200)


def testPutValidation(client):
    # Run basic validation tests
    basicValidation(client.simulate_put, PUT_URL, putData)


def testPutResourceMustAlreadyExist(client):
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'

    # Test that did resource already exists
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=1)

    exp_result = {"title": "404 Not Found"}

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  json.loads(body),
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_404)


def testPutSignersHasThreeKeys(client):
    # Test that signers field has three keys
    body = deepcopy(putData)
    del body['signers'][3]
    del body['signers'][2]

    exp_result = {
        "title": "Validation Error",
        "description": "signers field missing keys."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutSignersNotEmpty(client):
    body = deepcopy(putData)
    body['signers'] = []

    exp_result = {
        "title": "Validation Error",
        "description": "signers field missing keys."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutValidSignersField(client):
    body = deepcopy(putData)
    body['signer'] = 0
    body['signers'] = [
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
    ]
    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_status=falcon.HTTP_201)

    body = deepcopy(putData)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signers'] = [
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
    ]

    verifyRequest(client.simulate_put, PUT_URL, body, exp_status=falcon.HTTP_200)


def testPutInvalidSignerIndex(client):
    # Test that signer field is a valid index into signers field
    body = deepcopy(putData)
    body['signer'] = 4

    exp_result = {
        "title": "Validation Error",
        "description": "\"signer\" cannot reference the first or last key in the \"signers\" field on PUT requests."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutSingerNotZero(client):
    body = deepcopy(putData)
    body['signer'] = 0

    exp_result = {
        "title": "Validation Error",
        "description": "\"signer\" cannot reference the first or last key in the \"signers\" field on PUT requests."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutRequiresNewPreRotation(client):
    # Test that signers field has a pre-rotated key
    body = deepcopy(putData)
    body['signer'] = 3

    exp_result = {
        "title": "Validation Error",
        "description": "Missing pre rotated key in \"signers\" field."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutRequiresDidInUrl(client):
    # Test that the url has a did in it
    body = deepcopy(putData)

    exp_result = {
        "title": "Validation Error",
        "description": "DID value missing from url."
    }

    verifyRequest(client.simulate_put, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutChangedFieldMustUpdate(client):
    # Test that changed field is greater than previous date
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=4)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['signer'] = 1

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "\"changed\" field not later than previous update."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def testPutSignerFieldHasNewKeys(client):
    # Test that signers field length hasn't changed
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=4)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['signer'] = 1
    body['changed'] = "2000-01-01T00:00:01+00:00"

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "signers field is missing keys."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def testPutSignerFieldMissingKeys(client):
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=4)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['signer'] = 1
    body['changed'] = "2000-01-01T00:00:01+00:00"
    del body['signers'][3]

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "signers field is missing keys."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def testPutChangeVerifiedKeys(client):
    # Test that previously verified keys have not been changed
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=4)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['signer'] = 1
    body['changed'] = "2000-01-01T00:00:01+00:00"
    del body['signers'][3]
    body['signers'].append("Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=")
    body['signers'].append("Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=")

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "signers field missing previously verified keys."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def testPutUpdatedSignerField(client):
    # test that signer field is updated from previous requests
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    # send inception event
    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    # rotate once
    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 1
    body['signers'].append(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_status=falcon.HTTP_200)


def testPutUnchangedSignerField(client):
    # send updated history with new public key but unchanged signer field
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    # send inception event
    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 1
    body['signers'].append(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
    }

    # rotate once
    client.simulate_put("{0}/{1}".format(HISTORY_BASE_PATH, did),
                        body=json.dumps(body).encode(),
                        headers=headers)

    # Add new pre-rotated key but don't update signer field
    body['signers'].append(vk)
    body['changed'] = "2000-01-01T00:00:03+00:00"

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
    }

    exp_result = {
        "title": "Validation Error",
        "description": "signer field must be one greater than previous."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def testValidPut(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    # Test Valid rotation event
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(eddsa.signResource(body, sk),
                                                           eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 1
    body['signers'].append(body['signers'][0])

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
    }

    exp_result = [
        {
            "history": {
                "id": "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
                "changed": "2000-01-01T00:00:01+00:00",
                "signer": 1,
                "signers": [
                    "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
                    "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
                    "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
                ]
            },
            "signatures": {
                "signer": "bu-HIoIp2ZtBqsZtURP_q6rm8WPuDQGtN6maXbDHZbVHJ-QfGpwvXkE-fmi7XymvQJnS9tZXFQ5MPos5u09HDw==",
                "rotation": "bu-HIoIp2ZtBqsZtURP_q6rm8WPuDQGtN6maXbDHZbVHJ-QfGpwvXkE-fmi7XymvQJnS9tZXFQ5MPos5u09HDw=="
            }
        }
    ]

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_200)


def testGetAllInvalidQueryString(client):
    # Test that query params have values
    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string missing value(s)."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset=10&limit")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string missing value(s)."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testGetAllInvalidQueryValue(client):
    # Test that query params values are ints
    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset=a&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset=10&limit=d")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testGetAllNegativeQueryValue(client):
    # Test that query params values are ints
    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset=-1&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a positive number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset=0&limit=-10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a positive number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testGetAllEmptyQueryValue(client):
    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset=10&limit=")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset=&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testValidGetAll(client):
    history1 = {
        "id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
        "changed": "2000-01-01T00:00:01+00:00",
        "signer": 1,
        "signers": [
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
        ]
    }
    history1_sigs = {
        "signer": "bANC2XMeQS2DGvazrW7n5NpBHgn7Pv9jrmxId0cxcjFjuHE4zi7AK-tsf2Ocim0p-b8Z5Go6TsyaURE0VKgVCw==",
        "rotation": "bANC2XMeQS2DGvazrW7n5NpBHgn7Pv9jrmxId0cxcjFjuHE4zi7AK-tsf2Ocim0p-b8Z5Go6TsyaURE0VKgVCw=="
    }
    db.historyDB.saveHistory(DID, history1, history1_sigs)

    history2_did = "did:dad:KAApprffJUn1e9ugNmpM9JBswxJvEU8_XCljDCoxkII="
    history2 = {
        "id": history2_did,
        "changed": "2000-01-01T00:00:00+00:00",
        "signer": 0,
        "signers": [
            "KAApprffJUn1e9ugNmpM9JBswxJvEU8_XCljDCoxkII=",
            "KAApprffJUn1e9ugNmpM9JBswxJvEU8_XCljDCoxkII=",
            "KAApprffJUn1e9ugNmpM9JBswxJvEU8_XCljDCoxkII=",
            "KAApprffJUn1e9ugNmpM9JBswxJvEU8_XCljDCoxkII="
        ]
    }
    history2_sigs = {
        "signer": "tR1_GN9E7oTYbAGebDTlliRJLjy5IFEHTjvimgg3g9xHJHp82cEyNMnViUbg_TULdGAdkpfvzT9icujXuC3EDw==",
        "rotation": "tR1_GN9E7oTYbAGebDTlliRJLjy5IFEHTjvimgg3g9xHJHp82cEyNMnViUbg_TULdGAdkpfvzT9icujXuC3EDw=="
    }
    db.historyDB.saveHistory(history2_did, history2, history2_sigs)

    history3_did = "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
    history3 = {
        "id": history3_did,
        "changed": "2000-01-01T00:00:01+00:00",
        "signer": 1,
        "signers": [
            "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
            "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
            "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY="
        ]
    }
    history3_sigs = {
        "signer": "bu-HIoIp2ZtBqsZtURP_q6rm8WPuDQGtN6maXbDHZbVHJ-QfGpwvXkE-fmi7XymvQJnS9tZXFQ5MPos5u09HDw==",
        "rotation": "bu-HIoIp2ZtBqsZtURP_q6rm8WPuDQGtN6maXbDHZbVHJ-QfGpwvXkE-fmi7XymvQJnS9tZXFQ5MPos5u09HDw=="
    }
    db.historyDB.saveHistory(history3_did, history3, history3_sigs)

    response = client.simulate_get(HISTORY_BASE_PATH)
    result = json.loads(response.content)

    exp_result = {
        "data": [
            [
                {
                    "history": history2,
                    "signatures": history2_sigs
                }
            ],
            [
                {
                    "history": history1,
                    "signatures": history1_sigs
                }
            ],
            [
                {
                    "history": history3,
                    "signatures": history3_sigs
                }
            ],
        ]
    }

    assert response.status == falcon.HTTP_200
    assert result == exp_result

    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset=100&limit=10")

    exp_result = {}

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result


def testGetAllEmptyDB(client):
    response = client.simulate_get(HISTORY_BASE_PATH)

    exp_result = {}

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result


def testGetOneEmptyDB(client):
    # Test that 404 is returned when db is empty
    response = client.simulate_get(GET_ONE_URL)

    assert response.status == falcon.HTTP_404


def testValidGetOne(client):
    # Test basic valid Get One
    body = deepcopy(putData)
    body['signer'] = 0
    body['signers'] = [
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
    ]
    sig = eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), SK)
    headers = {
        "Signature": 'signer="{0}"'.format(sig)
    }
    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, headers=headers, exp_status=falcon.HTTP_201)

    response = client.simulate_get(GET_ONE_URL)

    exp_result = [
        {
            "history": body,
            "signatures": {
                "signer": sig
            }
        }
    ]

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result


def testGetOneNonExistent(client):
    # Test GET with non existent resource

    # Add something to the DB
    body = deepcopy(putData)
    body['signer'] = 0
    body['signers'] = [
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
    ]
    headers = {
        "Signature": 'signer="{0}"'.format(
            eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), SK))
    }
    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, headers=headers, exp_status=falcon.HTTP_201)

    response = client.simulate_get("{0}/{1}".format(
        HISTORY_BASE_PATH,
        "did:dad:COf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=")
    )

    exp_result = {"title": "404 Not Found"}

    assert response.status == falcon.HTTP_404
    assert json.loads(response.content) == exp_result


def testDeleteUrlMissingDid(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)

    # Test missing url did
    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"vk": vk}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, sk))}

    response = client.simulate_delete(HISTORY_BASE_PATH, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_400
    assert resp_content["title"] == "Validation Error"
    assert resp_content["description"] == "DID value missing from url."


def testDeleteNoSignatureHeader(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"vk": vk}, ensure_ascii=False).encode()

    response = client.simulate_delete(url, body=data)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_400
    assert resp_content["title"] == "Missing header value"
    assert resp_content["description"] == "The Signature header is required."


def testDeleteEmptySignatureHeader(client):
    # Test empty Signature header
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"vk": vk}, ensure_ascii=False).encode()
    headers = {"Signature": ""}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_401
    assert resp_content["title"] == "Authorization Error"
    assert resp_content["description"] == "Empty Signature header."


def testDeleteBadSignatureHeader(client):
    # Test bad Signature header tag
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"vk": vk}, ensure_ascii=False).encode()
    headers = {"Signature": 'rotation="{0}"'.format(eddsa.signResource(data, sk))}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_401
    assert resp_content["title"] == "Authorization Error"
    assert resp_content["description"] == 'Signature header missing signature for "signer".'


def testDeleteNonExistentResource(client):
    # Test delete non existent resource
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)
    data = json.dumps({"vk": vk}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, sk))}

    client.simulate_delete(url, body=data, headers=headers)
    response = client.simulate_delete(url, body=data, headers=headers)

    assert response.status == falcon.HTTP_404


def testDeleteInvalidSignature(client):
    # Test invalid signature
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"vk": vk}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, SK))}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_401
    assert resp_content["title"] == "Authorization Error"
    assert resp_content["description"] == "Could not validate the request signature for signer field. Unverifiable signature."


def testDeleteMissingRequiredFields(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, sk))}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_400
    assert resp_content["title"] == "Missing Required Field"
    assert resp_content["description"] == "Request must contain vk field."


def testValidDelete(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    signature = eddsa.signResource(body, sk)
    headers = {
        "Signature": 'signer="{0}"'.format(signature)
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"vk": vk}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, sk))}
    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_200
    assert resp_content["deleted"][0]["history"] == json.loads(body)
    assert resp_content["deleted"][0]["signatures"]["signer"] == signature


def testValidEcdsaPost(client):
    cryptoScheme = "ECDSA"
    vk, sk, did, body = ecdsa.genDidHistory(numSigners=2)

    signature = ecdsa.signResource(body, sk)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    exp_result = [
        {
            "history": json.loads(body.decode()),
            "signatures": {
                "name": cryptoScheme,
                "signer": signature
            }
        }
    ]

    verifyRequest(client.simulate_post,
                  HISTORY_BASE_PATH,
                  json.loads(body.decode()),
                  headers=headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_201)


def testValidSecp256k1Post(client):
    cryptoScheme = "secp256k1"
    vk, sk, did, body = ecdsa.genDidHistory(numSigners=2)

    signature = ecdsa.signResource(body, sk)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    exp_result = [
        {
            "history": json.loads(body.decode()),
            "signatures": {
                "name": cryptoScheme,
                "signer": signature
            }
        }
    ]

    verifyRequest(client.simulate_post,
                  HISTORY_BASE_PATH,
                  json.loads(body.decode()),
                  headers=headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_201)


def testInvalidEcdsaPostSig(client):
    cryptoScheme = "ECDSA"
    vk, sk, did, body = ecdsa.genDidHistory(changed="2000-01-01T00:00:00+00:00", numSigners=2)
    vk = h.bytesToStr64u(vk)

    signature = ecdsa.signResource(body, sk)

    body = json.loads(body.decode())
    body["changed"] = "2000-01-01T11:11:11+11:11"

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for signer field. Unverifiable signature."
    }

    verifyRequest(client.simulate_post,
                  HISTORY_BASE_PATH,
                  body,
                  headers=headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_401)


def testInvalidSecp256k1PostSig(client):
    cryptoScheme = "secp256k1"
    vk, sk, did, body = ecdsa.genDidHistory(changed="2000-01-01T00:00:00+00:00", numSigners=2)
    vk = h.bytesToStr64u(vk)

    signature = ecdsa.signResource(body, sk)

    body = json.loads(body.decode())
    body["changed"] = "2000-01-01T11:11:11+11:11"

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for signer field. Unverifiable signature."
    }

    verifyRequest(client.simulate_post,
                  HISTORY_BASE_PATH,
                  body,
                  headers=headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_401)


def testValidEcdsaPut(client):
    cryptoScheme = "ECDSA"

    # Test Valid rotation event
    vk, sk, did, body = ecdsa.genDidHistory(numSigners=2)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, ecdsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 1
    body['signers'].append(body['signers'][0])
    signature = ecdsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"; rotation="{2}"'.format(
            cryptoScheme,
            signature,
            signature)
    }

    exp_result = [
        {
            "history": body,
            "signatures": {
                "name": cryptoScheme,
                "signer": signature,
                "rotation": signature
            }
        }
    ]

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_200)


def testValidSecp256k1Put(client):
    cryptoScheme = "secp256k1"

    # Test Valid rotation event
    vk, sk, did, body = ecdsa.genDidHistory(numSigners=2)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, ecdsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 1
    body['signers'].append(body['signers'][0])
    signature = ecdsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"; rotation="{2}"'.format(
            cryptoScheme,
            signature,
            signature)
    }

    exp_result = [
        {
            "history": body,
            "signatures": {
                "name": cryptoScheme,
                "signer": signature,
                "rotation": signature
            }
        }
    ]

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_200)


def testInvalidEcdsaPutSig(client):
    cryptoScheme = "ECDSA"

    # Test Valid rotation event
    vk, sk, did, body = ecdsa.genDidHistory(numSigners=2)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, ecdsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 1
    body['signers'].append(body['signers'][0])
    signature = ecdsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"; rotation="{2}"'.format(
            cryptoScheme,
            signature,
            signature)
    }

    # Invalidate signature
    body['changed'] = "2000-01-01T11:11:11+11:11"

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for rotation field. Unverifiable signature."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_401)


def testInvalidSecp256k1PutSig(client):
    cryptoScheme = "secp256k1"

    # Test Valid rotation event
    vk, sk, did, body = ecdsa.genDidHistory(numSigners=2)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, ecdsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 1
    body['signers'].append(body['signers'][0])
    signature = ecdsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"; rotation="{2}"'.format(
            cryptoScheme,
            signature,
            signature)
    }

    # Invalidate signature
    body['changed'] = "2000-01-01T11:11:11+11:11"

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for rotation field. Unverifiable signature."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_401)


def testValidEcdsaDelete(client):
    cryptoScheme = "ECDSA"

    # Test Valid rotation event
    vk, sk, did, body = ecdsa.genDidHistory(numSigners=2)
    vk = h.bytesToStr64u(vk)
    signature = ecdsa.signResource(body, sk)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)
    data = json.dumps({"vk": vk}, ensure_ascii=False).encode()
    headers = {"Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, ecdsa.signResource(data, sk))}
    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_200
    assert resp_content["deleted"][0]["history"] == json.loads(body)
    assert resp_content["deleted"][0]["signatures"]["signer"] == signature


def testValidSecp256k1Delete(client):
    cryptoScheme = "secp256k1"

    # Test Valid rotation event
    vk, sk, did, body = ecdsa.genDidHistory(numSigners=2)
    vk = h.bytesToStr64u(vk)
    signature = ecdsa.signResource(body, sk)

    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)
    data = json.dumps({"vk": vk}, ensure_ascii=False).encode()
    headers = {"Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, ecdsa.signResource(data, sk))}
    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_200
    assert resp_content["deleted"][0]["history"] == json.loads(body)
    assert resp_content["deleted"][0]["signatures"]["signer"] == signature


class TestHistoryMethodMode:
    @pytest.fixture(scope="class")
    def testApp(self):
        """

        setup falcon and load REST endpoints

        """

        def app(mode="method"):
            store = storing.Store(stamp=0.0)
            testApp = falcon.API()
            loadEndPoints(testApp, store=store, mode=mode)
            db.createDBWrappers(mode)
            return testApp

        return app

    @pytest.fixture(autouse=True)
    def setupTearDown(self):
        """

        Pytest runs this function before every test when autouse=True
        Without autouse=True you would have to add a setupTeardown parameter
        to each test function

        """
        # setup
        dbPath = h.setupTmpBaseDir()
        db.setupDbEnv(dbPath, mode="method")

        yield dbPath  # this allows the test to run

        # teardown
        h.cleanupTmpBaseDir(dbPath)

    def testPostPromiscuous(self, testApp):
        # 1. setup with promiscuous mode
        # 2. add valid history and hacked history
        # 3. switch to race mode
        # 4. try a valid delete
        client = testing.TestClient(testApp("promiscuous"))

        # Insert valid history
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = client.simulate_post(HISTORY_BASE_PATH, body=history, headers=headers)
        assert response.status == falcon.HTTP_201

        # Insert hacked history
        hseed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        hvk, hsk, hdid, hhistory = eddsa.genDidHistory(hseed, signer=0, numSigners=2, method="fake")
        hvk = h.bytesToStr64u(hvk)

        hhistory = json.loads(hhistory.decode())
        hhistory["id"] = did
        hhistory = json.dumps(hhistory).encode()

        hsignature = eddsa.signResource(hhistory, hsk)

        headers = {
            "Signature": 'signer="{0}"'.format(hsignature)
        }

        response = client.simulate_post(HISTORY_BASE_PATH, body=hhistory, headers=headers)
        assert response.status == falcon.HTTP_201

        client = testing.TestClient(testApp("method"))

        history = json.loads(history)
        history['changed'] = "2000-01-01T00:00:01+00:00"
        history['signer'] = 1
        history['signers'].append(vk)
        history = json.dumps(history).encode()

        signer = eddsa.signResource(history, sk)
        rotation = eddsa.signResource(history, sk)

        headers = {
            "Signature": 'signer="{0}"; rotation="{1}"'.format(signer, rotation)
        }

        exp_result = [
            {
                "history": json.loads(history.decode()),
                "signatures": {
                    "signer": signer,
                    "rotation": rotation
                }
            }
        ]

        verifyRequest(client.simulate_put,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      json.loads(history.decode()),
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

    def testDeletePromiscuous(self, testApp):
        # 1. setup with promiscuous mode
        # 2. add valid history and hacked history
        # 3. switch to race mode
        # 4. try a valid delete
        client = testing.TestClient(testApp("promiscuous"))

        # Insert valid history
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = client.simulate_post(HISTORY_BASE_PATH, body=history, headers=headers)
        assert response.status == falcon.HTTP_201

        # Insert hacked history
        hseed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        hvk, hsk, hdid, hhistory = eddsa.genDidHistory(hseed, signer=0, numSigners=2, method="fake")
        hvk = h.bytesToStr64u(hvk)

        hhistory = json.loads(hhistory.decode())
        hhistory["id"] = did
        hhistory = json.dumps(hhistory).encode()

        hsignature = eddsa.signResource(hhistory, hsk)

        headers = {
            "Signature": 'signer="{0}"'.format(hsignature)
        }

        response = client.simulate_post(HISTORY_BASE_PATH, body=hhistory, headers=headers)
        assert response.status == falcon.HTTP_201

        client = testing.TestClient(testApp("method"))

        body = {"vk": vk}
        headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))}

        exp_result = {
            "deleted": [
                {
                    "history": json.loads(hhistory),
                    "signatures": {"signer": hsignature}
                },
                {
                    "history": json.loads(history),
                    "signatures": {"signer": signature}
                }
            ]
        }

        verifyRequest(client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)


class TestHistoryPromiscuousMode:
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

    def testValidGet(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
        assert response.status == falcon.HTTP_201

        response = promiscuous_client.simulate_get("{}/{}".format(HISTORY_BASE_PATH, did))

        exp_result = [
            {
                "history": json.loads(body.decode()),
                "signatures": {
                    "signer": signature
                }
            }
        ]

        assert response.status == falcon.HTTP_200
        assert json.loads(response.content) == exp_result

    def testValidGetAll(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk2 = h.bytesToStr64u(vk2)

        signature2 = eddsa.signResource(body2, sk2)

        headers2 = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body2, headers=headers2)

        body3 = json.loads(body2.decode())
        body3["id"] = did
        body3 = json.dumps(body3).encode()

        signature3 = eddsa.signResource(body3, sk2)

        headers3 = {
            "Signature": 'signer="{0}"'.format(signature3)
        }

        promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body3, headers=headers3)

        response = promiscuous_client.simulate_get(HISTORY_BASE_PATH)

        exp_result = {
            "data": [
                [
                    {
                        "history": json.loads(body2.decode()),
                        "signatures": {
                            "signer": signature2
                        }
                    }
                ],
                [
                    {
                        "history": json.loads(body3.decode()),
                        "signatures": {
                            "signer": signature3
                        }
                    },
                    {
                        "history": json.loads(body.decode()),
                        "signatures": {
                            "signer": signature
                        }
                    }
                ],
            ]
        }

        response_data = json.loads(response.content)
        assert response.status == falcon.HTTP_200
        assert len(response_data['data']) == 2
        # response_data order is unreliable
        # make sure that each history exists only once in response
        for result in exp_result['data']:
            matches = 0
            for data in response_data['data']:
                if data == result:
                    matches += 1

            assert matches == 1

    def testValidPost(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        exp_result = [
            {
                "history": json.loads(body.decode()),
                "signatures": {
                    "signer": signature
                }
            }
        ]

        verifyRequest(promiscuous_client.simulate_post,
                      HISTORY_BASE_PATH,
                      json.loads(body.decode()),
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_201)

    def testDuplicatePost(self, promiscuous_client):
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
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk2 = h.bytesToStr64u(vk2)

        body2 = json.loads(body2.decode())
        body2["id"] = did

        signature2 = eddsa.signResource(json.dumps(body2).encode(), sk2)

        headers = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        exp_result = [
            {
                "history": body2,
                "signatures": {
                    "signer": signature2
                }
            },
            {
                "history": json.loads(body.decode()),
                "signatures": {
                    "signer": signature
                }
            }
        ]

        verifyRequest(promiscuous_client.simulate_post,
                      HISTORY_BASE_PATH,
                      body2,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_201)

    def testValidPut(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        body = json.loads(body)
        body['changed'] = "2000-01-01T00:00:01+00:00"
        body['signer'] = 1
        body['signers'].append(vk)
        body = json.dumps(body).encode()

        signer = eddsa.signResource(body, sk)
        rotation = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"; rotation="{1}"'.format(signer, rotation)
        }

        exp_result = [
            {
                "history": json.loads(body.decode()),
                "signatures": {
                    "signer": signer,
                    "rotation": rotation
                }
            }
        ]

        verifyRequest(promiscuous_client.simulate_put,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      json.loads(body.decode()),
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

    def testDuplicatePut(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk2 = h.bytesToStr64u(vk2)

        body2 = json.loads(body2.decode())
        body2["id"] = did
        body2 = json.dumps(body2).encode()

        signature2 = eddsa.signResource(body2, sk2)

        headers2 = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body2, headers=headers2)

        body = json.loads(body)
        body['changed'] = "2000-01-01T00:00:01+00:00"
        body['signer'] = 1
        body['signers'].append(vk)
        body = json.dumps(body).encode()

        signer = eddsa.signResource(body, sk)
        rotation = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"; rotation="{1}"'.format(signer, rotation)
        }

        exp_result = [
            {
                "history": json.loads(body.decode()),
                "signatures": {
                    "signer": signer,
                    "rotation": rotation
                }
            },
            {
                "history": json.loads(body2.decode()),
                "signatures": {
                    "signer": signature2
                }
            }
        ]

        verifyRequest(promiscuous_client.simulate_put,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      json.loads(body.decode()),
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

    def testCascadingValidation(self, promiscuous_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="dad")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
        assert response.status == falcon.HTTP_201

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="dad")
        vk2 = h.bytesToStr64u(vk2)

        body2 = json.loads(body2.decode())
        body2["id"] = did

        signature2 = eddsa.signResource(json.dumps(body2).encode(), sk2)

        headers = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        exp_result = {
            "title": "Validation Error",
            "description": "The first key in the signers field does not belong to this DID."
        }

        verifyRequest(promiscuous_client.simulate_post,
                      HISTORY_BASE_PATH,
                      body2,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_400)

    def testValidDelete(self, promiscuous_client):
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
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk2 = h.bytesToStr64u(vk2)

        body2 = json.loads(body2.decode())
        body2["id"] = did
        body2 = json.dumps(body2).encode()

        signature2 = eddsa.signResource(body2, sk2)

        headers = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        response = promiscuous_client.simulate_post(HISTORY_BASE_PATH, body=body2, headers=headers)
        assert response.status == falcon.HTTP_201

        body3 = {"vk": vk}
        headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body3).encode(), sk))}

        exp_result = {
            "deleted": [
                {
                    "history": json.loads(body),
                    "signatures": {"signer": signature}
                }
            ]
        }

        verifyRequest(promiscuous_client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body3,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)


class TestHistoryRaceMode:
    @pytest.fixture(scope="class")
    def testApp(self):
        """

        setup falcon and load REST endpoints

        """

        def app(mode="method"):
            store = storing.Store(stamp=0.0)
            testApp = falcon.API()
            loadEndPoints(testApp, store=store, mode=mode)
            db.createDBWrappers(mode)
            return testApp

        return app

    @pytest.fixture(scope="class")
    def race_client(self, testApp):
        """

        This function utilizes the testApp() fixture above

        Pytest runs this function once per module

        testing.TestClient() is optional
        It allows you to avoid passing your app object into every
        simulate_xxx() function call

        """

        return testing.TestClient(testApp("race"))

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

    def testValidGet(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = race_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
        assert response.status == falcon.HTTP_201

        response = race_client.simulate_get("{}/{}".format(HISTORY_BASE_PATH, did))

        exp_result = [
            {
                "history": json.loads(body.decode()),
                "signatures": {
                    "signer": signature
                }
            }
        ]

        assert response.status == falcon.HTTP_200
        assert json.loads(response.content) == exp_result

    def testValidGetAll(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = race_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
        assert response.status == falcon.HTTP_201

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk2 = h.bytesToStr64u(vk2)

        signature2 = eddsa.signResource(body2, sk2)

        headers2 = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        response = race_client.simulate_post(HISTORY_BASE_PATH, body=body2, headers=headers2)
        assert response.status == falcon.HTTP_201

        response = race_client.simulate_get(HISTORY_BASE_PATH)

        exp_result = {
            "data": [
                [
                    {
                        "history": json.loads(body2.decode()),
                        "signatures": {
                            "signer": signature2
                        }
                    }
                ],
                [
                    {
                        "history": json.loads(body.decode()),
                        "signatures": {
                            "signer": signature
                        }
                    }
                ],
            ]
        }

        response_data = json.loads(response.content)
        assert response.status == falcon.HTTP_200
        assert len(response_data['data']) == 2
        # response_data order is unreliable
        # make sure that each history exists only once in response
        for result in exp_result['data']:
            matches = 0
            for data in response_data['data']:
                if data == result:
                    matches += 1

            assert matches == 1

    def testValidPost(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        exp_result = [
            {
                "history": json.loads(body.decode()),
                "signatures": {
                    "signer": signature
                }
            }
        ]

        verifyRequest(race_client.simulate_post,
                      HISTORY_BASE_PATH,
                      json.loads(body.decode()),
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_201)

    def testDuplicatePost(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = race_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
        assert response.status == falcon.HTTP_201

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk2 = h.bytesToStr64u(vk2)

        body2 = json.loads(body2.decode())
        body2["id"] = did

        signature2 = eddsa.signResource(json.dumps(body2).encode(), sk2)

        headers = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        exp_result = {
            "title": "Resource Already Exists",
            "description": "Resource with did \"{}\" already exists. Use PUT request.".format(did)
        }

        verifyRequest(race_client.simulate_post,
                      HISTORY_BASE_PATH,
                      body2,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_400)

    def testValidPut(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = race_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
        assert response.status == falcon.HTTP_201

        body = json.loads(body)
        body['changed'] = "2000-01-01T00:00:01+00:00"
        body['signer'] = 1
        body['signers'].append(vk)
        body = json.dumps(body).encode()

        signer = eddsa.signResource(body, sk)
        rotation = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"; rotation="{1}"'.format(signer, rotation)
        }

        exp_result = [
            {
                "history": json.loads(body.decode()),
                "signatures": {
                    "signer": signer,
                    "rotation": rotation
                }
            }
        ]

        verifyRequest(race_client.simulate_put,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      json.loads(body.decode()),
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

    def testCascadingValidation(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, body = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="dad")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(body, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = race_client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
        assert response.status == falcon.HTTP_201

        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk2, sk2, did2, body2 = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="dad")
        vk2 = h.bytesToStr64u(vk2)

        body2 = json.loads(body2.decode())
        body2["id"] = did

        signature2 = eddsa.signResource(json.dumps(body2).encode(), sk2)

        headers = {
            "Signature": 'signer="{0}"'.format(signature2)
        }

        exp_result = {
            "title": "Validation Error",
            "description": "The first key in the signers field does not belong to this DID."
        }

        verifyRequest(race_client.simulate_post,
                      HISTORY_BASE_PATH,
                      body2,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_400)

    def testValidDelete(self, race_client):
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = race_client.simulate_post(HISTORY_BASE_PATH, body=history, headers=headers)
        assert response.status == falcon.HTTP_201

        body = {"vk": vk}
        headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))}

        exp_result = {
            "deleted": [
                {
                    "history": json.loads(history),
                    "signatures": {"signer": signature}
                }
            ]
        }

        verifyRequest(race_client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

    def testDeletePromiscuous(self, testApp):
        # 1. setup with promiscuous mode
        # 2. add valid history and hacked history
        # 3. switch to race mode
        # 4. try a valid delete
        client = testing.TestClient(testApp("promiscuous"))

        # Insert valid history
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = client.simulate_post(HISTORY_BASE_PATH, body=history, headers=headers)
        assert response.status == falcon.HTTP_201

        # Insert hacked history
        hseed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        hvk, hsk, hdid, hhistory = eddsa.genDidHistory(hseed, signer=0, numSigners=2, method="fake")
        hvk = h.bytesToStr64u(hvk)

        hhistory = json.loads(hhistory.decode())
        hhistory["id"] = did
        hhistory = json.dumps(hhistory).encode()

        hsignature = eddsa.signResource(hhistory, hsk)

        headers = {
            "Signature": 'signer="{0}"'.format(hsignature)
        }

        response = client.simulate_post(HISTORY_BASE_PATH, body=hhistory, headers=headers)
        assert response.status == falcon.HTTP_201

        client = testing.TestClient(testApp("race"))

        body = {"vk": hvk}
        headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), hsk))}

        exp_result = {
            "deleted": [
                {
                    "history": json.loads(hhistory),
                    "signatures": {"signer": hsignature}
                }
            ]
        }

        verifyRequest(client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

    def testDeleteInvalidPromiscuous(self, testApp):
        # 1. setup with promiscuous mode
        # 2. add valid history and hacked history
        # 3. switch to race mode
        # 4. try an invalid delete
        client = testing.TestClient(testApp("promiscuous"))

        # Insert valid history
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2, method="fake")
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        headers = {
            "Signature": 'signer="{0}"'.format(signature)
        }

        response = client.simulate_post(HISTORY_BASE_PATH, body=history, headers=headers)
        assert response.status == falcon.HTTP_201

        # Insert hacked history
        hseed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        hvk, hsk, hdid, hhistory = eddsa.genDidHistory(hseed, signer=0, numSigners=2, method="fake")
        hvk = h.bytesToStr64u(hvk)

        hhistory = json.loads(hhistory.decode())
        hhistory["id"] = did
        hhistory = json.dumps(hhistory).encode()

        hsignature = eddsa.signResource(hhistory, hsk)

        headers = {
            "Signature": 'signer="{0}"'.format(hsignature)
        }

        response = client.simulate_post(HISTORY_BASE_PATH, body=hhistory, headers=headers)
        assert response.status == falcon.HTTP_201

        client = testing.TestClient(testApp("race"))

        body = {"vk": vk}
        headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))}

        exp_result = {
            "deleted": [
                {
                    "history": json.loads(history),
                    "signatures": {"signer": signature}
                }
            ]
        }

        verifyRequest(client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)


class TestEventsDeletionMethodMode:
    @pytest.fixture(scope="class")
    def testApp(self):
        """

        setup falcon and load REST endpoints

        """

        def app(mode="method"):
            store = storing.Store(stamp=0.0)
            testApp = falcon.API()
            loadEndPoints(testApp, store=store, mode=mode)
            db.createDBWrappers(mode)
            return testApp

        return app

    @pytest.fixture(scope="class")
    def client(self, testApp):
        """

        This function utilizes the testApp() fixture above

        Pytest runs this function once per module

        testing.TestClient() is optional
        It allows you to avoid passing your app object into every
        simulate_xxx() function call

        """

        return testing.TestClient(testApp("method"))

    @pytest.fixture
    def dbs(self):
        def get_dbs(mode):
            db.createDBWrappers(mode)
            return db.historyDB, db.eventsDB

        return get_dbs

    @pytest.fixture(autouse=True)
    def setupTearDown(self):
        """

        Pytest runs this function before every test when autouse=True
        Without autouse=True you would have to add a setupTeardown parameter
        to each test function

        """
        # setup
        db_path = h.setupTmpBaseDir()
        db.setupDbEnv(db_path, mode="method")

        yield db_path  # this allows the test to run

        # teardown
        h.cleanupTmpBaseDir(db_path)

    def test_events_deletion(self, client, dbs):
        # setup
        history_db, events_db = dbs("method")
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        history = json.loads(history.decode())
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        assert events_db.getEvent(did) is not None
        assert history_db.getHistory(did) is not None

        # begin test
        body = {"vk": vk}
        headers = {
            "Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))
        }

        exp_result = {
            "deleted": [
                {
                    "history": history,
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        }

        verifyRequest(client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

        assert events_db.getEvent(did) is None
        assert history_db.getHistory(did) is None

    def test_promiscuous_events_deletion(self, client, dbs):
        # setup
        history_db, events_db = dbs("promiscuous")

        # did owner
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        history = json.loads(history.decode())
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # rotation
        history["signer"] = 1
        history["signers"].append(vk)

        signature = eddsa.signResource(json.dumps(history).encode(), sk)
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # hacked did
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        hvk, hsk, hdid, hhistory = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        hvk = h.bytesToStr64u(hvk)

        hhistory = json.loads(hhistory.decode())
        hhistory["id"] = did

        hsignature = eddsa.signResource(json.dumps(hhistory).encode(), hsk)
        hsignatures = {"signer": hsignature}

        history_db.saveHistory(did, hhistory, hsignatures)
        events_db.saveEvent(did, hhistory, hsignatures)

        # check setup success
        assert events_db.getEvent(did) is not None
        assert history_db.getHistory(did) is not None

        # begin test
        history_db, events_db = dbs("method")

        body = {"vk": vk}
        headers = {
            "Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))
        }

        exp_result = {
            "deleted": [
                {
                    "history": hhistory,
                    "signatures": {
                        "signer": hsignature
                    }
                },
                {
                    "history": history,
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        }

        verifyRequest(client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

        assert events_db.getEvent(did) is None
        assert history_db.getHistory(did) is None

    def test_race_events_deletion(self, client, dbs):
        # setup
        history_db, events_db = dbs("race")

        # did owner
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        history = json.loads(history.decode())
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # rotation
        history["signer"] = 1
        history["signers"].append(vk)

        signature = eddsa.signResource(json.dumps(history).encode(), sk)
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # check setup success
        assert events_db.getEvent(did) is not None
        assert history_db.getHistory(did) is not None

        # begin test
        history_db, events_db = dbs("method")

        body = {"vk": vk}
        headers = {
            "Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))
        }

        exp_result = {
            "deleted": [
                {
                    "history": history,
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        }

        verifyRequest(client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

        assert events_db.getEvent(did) is None
        assert history_db.getHistory(did) is None


class TestEventsDeletionPromiscuousMode:
    @pytest.fixture(scope="class")
    def testApp(self):
        """

        setup falcon and load REST endpoints

        """

        def app(mode="method"):
            store = storing.Store(stamp=0.0)
            testApp = falcon.API()
            loadEndPoints(testApp, store=store, mode=mode)
            db.createDBWrappers(mode)
            return testApp

        return app

    @pytest.fixture(scope="class")
    def promiscuous_client(self, testApp):
        """

        This function utilizes the testApp() fixture above

        Pytest runs this function once per module

        testing.TestClient() is optional
        It allows you to avoid passing your app object into every
        simulate_xxx() function call

        """

        return testing.TestClient(testApp("promiscuous"))

    @pytest.fixture
    def dbs(self):
        def get_dbs(mode):
            db.createDBWrappers(mode)
            return db.historyDB, db.eventsDB

        return get_dbs

    @pytest.fixture(autouse=True)
    def setupTearDown(self):
        """

        Pytest runs this function before every test when autouse=True
        Without autouse=True you would have to add a setupTeardown parameter
        to each test function

        """
        # setup
        db_path = h.setupTmpBaseDir()
        db.setupDbEnv(db_path, mode="promiscuous")

        yield db_path  # this allows the test to run

        # teardown
        h.cleanupTmpBaseDir(db_path)

    def test_events_deletion(self, promiscuous_client, dbs):
        # setup
        history_db, events_db = dbs("promiscuous")

        # did owner
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        history = json.loads(history.decode())
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # rotation
        history["signer"] = 1
        history["signers"].append(vk)

        signature = eddsa.signResource(json.dumps(history).encode(), sk)
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # hacked did
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        hvk, hsk, hdid, hhistory = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        hvk = h.bytesToStr64u(hvk)

        hhistory = json.loads(hhistory.decode())
        hhistory["id"] = did

        hsignature = eddsa.signResource(json.dumps(hhistory).encode(), hsk)
        hsignatures = {"signer": hsignature}

        history_db.saveHistory(did, hhistory, hsignatures)
        events_db.saveEvent(did, hhistory, hsignatures)

        # check setup success
        assert events_db.getEvent(did) is not None
        assert history_db.getHistory(did) is not None

        # begin test

        body = {"vk": vk}
        headers = {
            "Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))
        }

        exp_result = {
            "deleted": [
                {
                    "history": history,
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        }

        verifyRequest(promiscuous_client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

        remaining_events = events_db.getEvent(did)
        remaining_history = history_db.getHistory(did)
        exp_events = [
            [
                {
                    "event": hhistory,
                    "signatures": hsignatures,
                }
            ]
        ]

        assert remaining_events is not None
        assert remaining_history is not None

        assert exp_events == remaining_events.to_list()

    def test_method_events_deletion(self, promiscuous_client, dbs):
        # setup
        history_db, events_db = dbs("method")

        # did owner
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        history = json.loads(history.decode())
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # rotation
        history["signer"] = 1
        history["signers"].append(vk)

        signature = eddsa.signResource(json.dumps(history).encode(), sk)
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # check setup success
        assert events_db.getEvent(did) is not None
        assert history_db.getHistory(did) is not None

        # begin test
        history_db, events_db = dbs("promiscuous")

        body = {"vk": vk}
        headers = {
            "Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))
        }

        exp_result = {
            "deleted": [
                {
                    "history": history,
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        }

        verifyRequest(promiscuous_client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

        remaining_events = events_db.getEvent(did)
        remaining_history = history_db.getHistory(did)

        assert remaining_events is None
        assert remaining_history is None

    def test_race_events_deletion(self, promiscuous_client, dbs):
        # setup
        history_db, events_db = dbs("race")

        # did owner
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        history = json.loads(history.decode())
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # rotation
        history["signer"] = 1
        history["signers"].append(vk)

        signature = eddsa.signResource(json.dumps(history).encode(), sk)
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # check setup success
        assert events_db.getEvent(did) is not None
        assert history_db.getHistory(did) is not None

        # begin test
        history_db, events_db = dbs("promiscuous")

        body = {"vk": vk}
        headers = {
            "Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))
        }

        exp_result = {
            "deleted": [
                {
                    "history": history,
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        }

        verifyRequest(promiscuous_client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

        remaining_events = events_db.getEvent(did)
        remaining_history = history_db.getHistory(did)

        assert remaining_events is None
        assert remaining_history is None


class TestEventsDeletionRaceMode:
    @pytest.fixture(scope="class")
    def testApp(self):
        """

        setup falcon and load REST endpoints

        """

        def app(mode="method"):
            store = storing.Store(stamp=0.0)
            testApp = falcon.API()
            loadEndPoints(testApp, store=store, mode=mode)
            db.createDBWrappers(mode)
            return testApp

        return app

    @pytest.fixture(scope="class")
    def race_client(self, testApp):
        """

        This function utilizes the testApp() fixture above

        Pytest runs this function once per module

        testing.TestClient() is optional
        It allows you to avoid passing your app object into every
        simulate_xxx() function call

        """

        return testing.TestClient(testApp("race"))

    @pytest.fixture
    def dbs(self):
        def get_dbs(mode):
            db.createDBWrappers(mode)
            return db.historyDB, db.eventsDB

        return get_dbs

    @pytest.fixture(autouse=True)
    def setupTearDown(self):
        """

        Pytest runs this function before every test when autouse=True
        Without autouse=True you would have to add a setupTeardown parameter
        to each test function

        """
        # setup
        db_path = h.setupTmpBaseDir()
        db.setupDbEnv(db_path, mode="race")

        yield db_path  # this allows the test to run

        # teardown
        h.cleanupTmpBaseDir(db_path)

    def test_events_deletion(self, race_client, dbs):
        # setup
        history_db, events_db = dbs("race")

        # did owner
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        history = json.loads(history.decode())
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # rotation
        history["signer"] = 1
        history["signers"].append(vk)

        signature = eddsa.signResource(json.dumps(history).encode(), sk)
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # check setup success
        assert events_db.getEvent(did) is not None
        assert history_db.getHistory(did) is not None

        # begin test

        body = {"vk": vk}
        headers = {
            "Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))
        }

        exp_result = {
            "deleted": [
                {
                    "history": history,
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        }

        verifyRequest(race_client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

        remaining_events = events_db.getEvent(did)
        remaining_history = history_db.getHistory(did)

        assert remaining_events is None
        assert remaining_history is None

    def test_promiscuous_events_deletion(self, race_client, dbs):
        # setup
        history_db, events_db = dbs("promiscuous")

        # did owner
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        history = json.loads(history.decode())
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # rotation
        history["signer"] = 1
        history["signers"].append(vk)

        signature = eddsa.signResource(json.dumps(history).encode(), sk)
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # hacked did
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        hvk, hsk, hdid, hhistory = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        hvk = h.bytesToStr64u(hvk)

        hhistory = json.loads(hhistory.decode())
        hhistory["id"] = did

        hsignature = eddsa.signResource(json.dumps(hhistory).encode(), hsk)
        hsignatures = {"signer": hsignature}

        history_db.saveHistory(did, hhistory, hsignatures)
        events_db.saveEvent(did, hhistory, hsignatures)

        # check setup success
        assert events_db.getEvent(did) is not None
        assert history_db.getHistory(did) is not None

        # begin test
        history_db, events_db = dbs("race")

        body = {"vk": vk}
        headers = {
            "Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))
        }

        exp_result = {
            "deleted": [
                {
                    "history": history,
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        }

        verifyRequest(race_client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

        remaining_events = events_db.getEvent(did)
        remaining_history = history_db.getHistory(did)
        exp_events = [
            [
                {
                    "event": hhistory,
                    "signatures": hsignatures,
                }
            ]
        ]

        assert remaining_events is not None
        assert remaining_history is not None

        assert exp_events == remaining_events.to_list()

    def test_method_events_deletion(self, race_client, dbs):
        # setup
        history_db, events_db = dbs("method")

        # did owner
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk, did, history = eddsa.genDidHistory(seed, signer=0, numSigners=2)
        vk = h.bytesToStr64u(vk)

        signature = eddsa.signResource(history, sk)

        history = json.loads(history.decode())
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # rotation
        history["signer"] = 1
        history["signers"].append(vk)

        signature = eddsa.signResource(json.dumps(history).encode(), sk)
        signatures = {"signer": signature}

        history_db.saveHistory(did, history, signatures)
        events_db.saveEvent(did, history, signatures)

        # check setup success
        assert events_db.getEvent(did) is not None
        assert history_db.getHistory(did) is not None

        # begin test
        history_db, events_db = dbs("race")

        body = {"vk": vk}
        headers = {
            "Signature": 'signer="{0}"'.format(eddsa.signResource(json.dumps(body).encode(), sk))
        }

        exp_result = {
            "deleted": [
                {
                    "history": history,
                    "signatures": {
                        "signer": signature
                    }
                }
            ]
        }

        verifyRequest(race_client.simulate_delete,
                      "{}/{}".format(HISTORY_BASE_PATH, did),
                      body,
                      headers=headers,
                      exp_result=exp_result,
                      exp_status=falcon.HTTP_200)

        remaining_events = events_db.getEvent(did)
        remaining_history = history_db.getHistory(did)

        assert remaining_events is None
        assert remaining_history is None
