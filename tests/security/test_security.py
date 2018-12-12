import falcon
import didery.crypto.eddsa
import tests.testing_utils.utils

try:
    import simplejson as json
except ImportError:
    import json

from copy import deepcopy

from didery.routing import *
from tests.controllers.test_history import setupRevokedHistory


SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
VK = b"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
DID = "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

verifyRequest = tests.testing_utils.utils.verifyPublicApiRequest
SEED = b'PTi\x15\xd5\xd3`\xf1u\x15}^r\x9bfH\x02l\xc6\x1b\x1d\x1c\x0b9\xd7{\xc0_\xf2K\x93`'
PUT_URL = "{0}/{1}".format(HISTORY_BASE_PATH, DID)

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


def testRotateNullKey(client):
    vk, sk, did, body = setupRevokedHistory(client)

    # try to rotate away from the null key
    body['changed'] = "2000-01-01T00:00:02+00:00"
    body['signer'] = 3
    body['signers'].append(vk)
    body['signers'].append(vk)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
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
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk),
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode(), sk))
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


def testPostDIDAndPublicKeyMatch(client):
    # SECURITY:
    # Test the public key in the id field did matches the first public key in rotation history
    body = deepcopy(postData)
    body['id'] = "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error",
        "description": "The DIDs key must match the first key in the signers field."
    }

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutUrlDIDAndIdDIDMatch(client):
    # SECURITY:
    # Make sure that a hacker cant insert their own info by placing changing the payload
    body = deepcopy(putData)
    body['id'] = "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error",
        "description": "Url did must match id field did."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutChangedFieldMustUpdate(client):
    # Test that changed field is greater than previous date
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=4)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(didery.crypto.eddsa.signResource(body, sk),
                                                           didery.crypto.eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['signer'] = 1

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
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


def testPutSignerFieldMissingKeys(client):
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=4)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(didery.crypto.eddsa.signResource(body, sk),
                                                           didery.crypto.eddsa.signResource(body, sk))
    }

    client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)  # Add did to database

    body = json.loads(body)
    body['signer'] = 1
    body['changed'] = "2000-01-01T00:00:01+00:00"
    del body['signers'][3]

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
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
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=4)

    headers = {
        "Signature": 'signer="{0}"; rotation="{1}"'.format(didery.crypto.eddsa.signResource(body, sk),
                                                           didery.crypto.eddsa.signResource(body, sk))
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
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk),
            didery.crypto.eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), sk))
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
