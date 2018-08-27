'''
    Tests can be run from the terminal with the following command:
        pytest tests/controllers

    To see test coverage install pytest-cov with pip then run this command:
        py.test --cov-report term-missing --cov=src/didery/controllers/ tests/controllers/
'''

import falcon
import libnacl
import arrow

try:
    import simplejson as json
except ImportError:
    import json

from copy import deepcopy

from didery.routing import *
from didery.help import helping as h
from didery.db import dbing as db


SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
VK = b"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
DID = "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

verifyRequest = h.verifyPublicApiRequest
SEED = b'PTi\x15\xd5\xd3`\xf1u\x15}^r\x9bfH\x02l\xc6\x1b\x1d\x1c\x0b9\xd7{\xc0_\xf2K\x93`'

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


def testKeyRevocation(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'

    # Test Valid rotation event
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.keyToKey64u(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(body, sk),
                                                           h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    # revoke key
    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 2
    body['signers'].append(None)

    signature = h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            signature,
            signature)
    }

    exp_result = {
        "history": {
            "id": "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
            "changed": "2000-01-01T00:00:01+00:00",
            "signer": 2,
            "signers": [
                "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
                "iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=",
                None
            ]
        },
        "signatures": {
            "signer": signature,
            "rotation": signature
        }
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_200)

    # try to rotate away from the null key
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 3
    body['signers'].append(vk)
    body['signers'].append(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
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
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
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

    # try to rotate into the null key prematurely
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(body, sk),
                                                           h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 4
    body['signers'].append(None)
    body['signers'].append(None)
    body['signers'].append(None)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
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
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)

    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 1
    body['signers'].append(None)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
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
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)

    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 1
    body['signers'].append("")

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
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
    body = postData

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_status=falcon.HTTP_201)
    # TODO:
    # assert json.loads(response.content) == expected_response


def testPostPreRotationIsNull(client):
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)

    body = json.loads(body)
    body['signers'][1] = None
    body = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()

    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
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
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)

    body = json.loads(body)
    body['signers'][1] = ""
    body = json.dumps(body, ensure_ascii=False, separators=(",", ":")).encode()

    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
    }

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    exp_result = {
        "title": "Validation Error",
        "description": "signers keys cannot be empty."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testPostSignValidation(client):
    headers = {"Signature": ""}

    # Test missing Signature Header
    body = deepcopy(postData)
    body = json.dumps(body, ensure_ascii=False).encode('utf-8')

    exp_result = {
        "title": "Authorization Error",
        "description": "Empty Signature header."
    }

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
    assert response.status == falcon.HTTP_401
    assert json.loads(response.content) == exp_result

    exp_result = {
        "title": "Missing header value",
        "description": "The Signature header is required."
    }

    response = client.simulate_post(HISTORY_BASE_PATH, body=body)
    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    # Test missing signer tag in signature header
    body = deepcopy(postData)

    headers = {
        "Signature": 'test="' + h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), SK) + '"'
    }

    exp_result = {
        "title": "Authorization Error",
        "description": "Signature header missing \"signer\" tag and signature."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, headers, exp_result, falcon.HTTP_401)

    # Test invalid signature
    body = deepcopy(postData)
    body['signers'][0] = "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request body and signature. Unverifiable signature."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_401)

    # Test the public key in the id field did matches the first public key in rotation history
    body = deepcopy(postData)
    body['id'] = "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error",
        "description": "The DIDs key must match the first key in the signers field."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPostValidation(client):
    # Run basic validation tests
    basicValidation(client.simulate_post, HISTORY_BASE_PATH, postData)

    # Test valid did format in id field
    body = deepcopy(postData)
    body['id'] = "did:fake:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error",
        "description": "Invalid did format. Invalid DID method"
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    body = deepcopy(postData)
    body['id'] = "did:fake"

    exp_result = {
        "title": "Validation Error",
        "description": "Invalid did format. Invalid DID value"
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    body = deepcopy(postData)
    body['id'] = "fake:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error", "description": "Invalid did format. Invalid DID identifier"
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has two keys
    body = deepcopy(postData)
    body['signers'] = ["Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="]

    exp_result = {
        "title": "Validation Error",
        "description": "signers field must contain at least the current public key and its first pre-rotation."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has two keys
    body = deepcopy(postData)
    body['signers'] = []

    exp_result = {
        "title": "Validation Error",
        "description": "signers field must contain at least the current public key and its first pre-rotation."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has two keys
    body = deepcopy(postData)
    body['signers'] = ["NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="]

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_status=falcon.HTTP_201)

    # Test that signer field is a valid index into signers field
    body = deepcopy(postData)
    body['signer'] = 4

    exp_result = {
        "title": "Validation Error",
        "description": "signer field must equal 0 on creation of new rotation history."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that server doesn't crash if anything is added after /history
    body = deepcopy(postData)
    path = "{0}/{1}".format(HISTORY_BASE_PATH, "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=")

    verifyRequest(client.simulate_post, path, body, exp_status=falcon.HTTP_404)


def testPutSignValidation(client):
    url = "{0}/{1}".format(HISTORY_BASE_PATH, DID)
    headers = {"Signature": ""}

    # Test url did matches id did
    body = deepcopy(putData)
    body['id'] = "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error",
        "description": "Url did must match id field did."
    }

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing Signature Header
    body = deepcopy(putData)

    exp_result = {
        "title": "Authorization Error",
        "description": "Empty Signature header."
    }

    verifyRequest(client.simulate_put, url, body, headers, exp_result, falcon.HTTP_401)

    exp_result = {
        "title": "Missing header value",
        "description": "The Signature header is required."
    }

    response = client.simulate_put(url, body=json.dumps(body, ensure_ascii=False).encode('utf-8'))
    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    # Test partial signature header
    headers = {
        "Signature": 'signer="' + h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), SK) + '"'
    }

    exp_result = {
        "title": "Authorization Error",
        "description": "Signature header missing signature for \"rotation\"."
    }

    verifyRequest(client.simulate_put, url, body, headers, exp_result, falcon.HTTP_401)

    headers = {
        "Signature": 'rotation="' + h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), SK) + '"'
    }

    exp_result = {
        "title": "Authorization Error",
        "description": "Signature header missing signature for \"signer\"."
    }

    verifyRequest(client.simulate_put, url, body, headers, exp_result, falcon.HTTP_401)

    # Test invalid signer signature
    body = deepcopy(putData)
    body['signers'][1] = "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148="

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for rotation field. Unverifiable signature."
    }

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_401)

    # Test invalid rotation signature
    body = deepcopy(putData)
    body['signers'][0] = "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
    body['signers'][1] = "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for signer field. Unverifiable signature."
    }

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_401)

    # validate that signer and rotation signature fields are working correctly
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk = libnacl.crypto_sign_seed_keypair(seed)
    pvk, psk = libnacl.crypto_sign_seed_keypair(seed)
    ppvk, ppsk = libnacl.crypto_sign_seed_keypair(seed)

    did = h.makeDid(vk)
    vk = h.keyToKey64u(vk)
    pvk = h.keyToKey64u(pvk)
    ppvk = h.keyToKey64u(ppvk)
    body = {
        "id": did,
        "changed": str(arrow.utcnow()),
        "signer": 0,
        "signers": [vk, pvk]
    }
    bbody = json.dumps(body, ensure_ascii=False).encode('utf-8')
    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(bbody, sk))
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, headers=headers, exp_status=falcon.HTTP_201)

    body['signer'] = 1
    body['changed'] = str(arrow.utcnow())
    body['signers'].append(ppvk)
    bbody = json.dumps(body, ensure_ascii=False).encode('utf-8')
    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(bbody, sk),
                                                           h.signResource(bbody, psk))
    }
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    verifyRequest(client.simulate_put, url, body, headers=headers, exp_status=falcon.HTTP_200)


def testPutValidation(client):
    url = "{0}/{1}".format(HISTORY_BASE_PATH, DID)
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'

    # Test that did resource already exists
    vk, sk, did, body = h.genDidHistory(seed, signer=1)

    exp_result = {"title": "404 Not Found"}

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(body, sk),
                                                           h.signResource(body, sk))
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  json.loads(body),
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_404)

    # Run basic validation tests
    basicValidation(client.simulate_put, url, putData)

    # Test that signers field has three keys
    body = deepcopy(putData)
    del body['signers'][3]
    del body['signers'][2]

    exp_result = {
        "title": "Validation Error",
        "description": "PUT endpoint is for rotation events. Must contain at least the original key, a current signing"
                       " key, and a pre-rotated key."
    }

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has three keys
    body = deepcopy(putData)
    body['signers'] = []

    exp_result = {
        "title": "Validation Error",
        "description": "PUT endpoint is for rotation events. Must contain at least the original key, a current signing"
                       " key, and a pre-rotated key."
    }

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has three keys
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

    verifyRequest(client.simulate_put, url, body, exp_status=falcon.HTTP_200)

    # Test that signer field is a valid index into signers field
    body = deepcopy(putData)
    body['signer'] = 4

    exp_result = {
        "title": "Validation Error",
        "description": "\"signer\" cannot reference the first or last key in the \"signers\" field on PUT requests."
    }

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signer is not 0
    body = deepcopy(putData)
    body['signer'] = 0

    exp_result = {
        "title": "Validation Error",
        "description": "\"signer\" cannot reference the first or last key in the \"signers\" field on PUT requests."
    }

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has a pre-rotated key
    body = deepcopy(putData)
    body['signer'] = 3

    exp_result = {
        "title": "Validation Error",
        "description": "Missing pre rotated key in the signers field."
    }

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that the url has a did in it
    body = deepcopy(putData)

    exp_result = {
        "title": "Validation Error",
        "description": "DID value missing from url."
    }

    verifyRequest(client.simulate_put, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that changed field is greater than previous date
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=4)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(body, sk),
                                                           h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers) # Add did to database

    body = json.loads(body)
    body['signer'] = 1

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
                                                           h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
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

    # Test that signers field length hasn't changed
    body['changed'] = "2000-01-01T00:00:01+00:00"

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
                                                           h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
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

    del body['signers'][3]

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
                                                           h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
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

    # Test that previously verified keys have not been changed
    body['signers'].append("Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=")
    body['signers'].append("Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=")

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
                                                           h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
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

    # test that signer field is updated from previous requests
    seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.keyToKey64u(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(body, sk),
                                                           h.signResource(body, sk))
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
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_status=falcon.HTTP_200)

    # send updated history with new public key but unchanged signer field
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 1
    body['signers'].append(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
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
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(body, sk),
                                                           h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"
    body['signer'] = 1
    body['signers'].append(body['signers'][0])

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
                                                           h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
    }

    exp_result = {
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

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, did),
                  body,
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_200)


def testGetAllValidation(client):
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
    db.saveHistory(DID, history1, history1_sigs)

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
    db.saveHistory(history2_did, history2, history2_sigs)

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
    db.saveHistory(history3_did, history3, history3_sigs)

    response = client.simulate_get(HISTORY_BASE_PATH)
    result = json.loads(response.content)

    exp_result = {
        "data": [
            {
                "history": history2,
                "signatures": history2_sigs
            },
            {
                "history": history1,
                "signatures": history1_sigs
            },
            {
                "history": history3,
                "signatures": history3_sigs
            }
        ]
    }

    assert response.status == falcon.HTTP_200
    assert result == exp_result

    response = client.simulate_get(HISTORY_BASE_PATH, query_string="offset=100&limit=10")

    exp_result = {}

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result


def testGetOne(client):
    url = "{0}/{1}".format(HISTORY_BASE_PATH, DID)

    # Test that 404 is returned when db is empty
    response = client.simulate_get(url)

    assert response.status == falcon.HTTP_404

    # Test basic valid Get One
    body = deepcopy(putData)
    body['signer'] = 0
    body['signers'] = [
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
        "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
    ]
    headers = {
        "Signature": 'signer="{0}"'.format(
            h.signResource(json.dumps(body, ensure_ascii=False).encode(), SK))
    }
    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, headers=headers, exp_status=falcon.HTTP_201)

    response = client.simulate_get(url)

    exp_result = {
        "history": {
            "id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "changed": "2000-01-01T00:00:00+00:00",
            "signer": 0,
            "signers": [
                "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
                "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
            ]
        },
        "signatures": {
            "signer": "xYbxaQtHsrispyZnd_3qf9xqBCXwgBq9pDnFP_5M2v-d-tNarUJeIY1wMeUcDTm808jG0kTwiXu9WApdao8FAA=="
        }
    }

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result

    # Test GET with non existent resource
    response = client.simulate_get("{0}/{1}".format(
        HISTORY_BASE_PATH,
        "did:dad:COf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=")
    )

    exp_result = {"title": "404 Not Found"}

    assert response.status == falcon.HTTP_404
    assert json.loads(response.content) == exp_result


def testDeleteValidation(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)

    # Test missing url did
    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(h.signResource(data, sk))}

    response = client.simulate_delete(HISTORY_BASE_PATH, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_400
    assert resp_content["title"] == "Validation Error"
    assert resp_content["description"] == "DID value missing from url."

    # Test no Signature header
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)
    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()

    response = client.simulate_delete(url, body=data)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_400
    assert resp_content["title"] == "Missing header value"
    assert resp_content["description"] == "The Signature header is required."

    # Test empty Signature header
    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": ""}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_401
    assert resp_content["title"] == "Authorization Error"
    assert resp_content["description"] == "Empty Signature header."

    # Test bad Signature header tag
    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'rotation="{0}"'.format(h.signResource(data, sk))}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_401
    assert resp_content["title"] == "Authorization Error"
    assert resp_content["description"] == 'Signature header missing signature for "signer".'

    # Test mismatched dids
    url = "{0}/{1}".format(HISTORY_BASE_PATH, DID)

    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(h.signResource(data, sk))}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_400
    assert resp_content["title"] == "Validation Error"
    assert resp_content["description"] == "Url did must match id field did."

    # Test delete non existent resource
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)
    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(h.signResource(data, sk))}

    client.simulate_delete(url, body=data, headers=headers)
    response = client.simulate_delete(url, body=data, headers=headers)

    assert response.status == falcon.HTTP_404

    # Test invalid signature
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(h.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(h.signResource(data, SK))}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)
    print(resp_content)

    assert response.status == falcon.HTTP_401
    assert resp_content["title"] == "Authorization Error"
    assert resp_content["description"] == "Could not validate the request signature for signer field. Unverifiable signature."


def testValidDelete(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = h.genDidHistory(seed, signer=0, numSigners=2)
    url = "{0}/{1}".format(HISTORY_BASE_PATH, did)

    signature = h.signResource(body, sk)
    headers = {
        "Signature": 'signer="{0}"'.format(signature)
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(h.signResource(data, sk))}
    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_200
    assert resp_content["deleted"]["history"] == json.loads(body)
    assert resp_content["deleted"]["signatures"]["signer"] == signature
