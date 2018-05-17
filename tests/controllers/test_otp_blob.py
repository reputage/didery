'''
    Tests can be run from the terminal with the following command:
        pytest tests/controllers

    To see test coverage install pytest-cov with pip then run this command:
        py.test --cov-report term-missing --cov=src/didery/controllers/ tests/controllers/
'''

import falcon
try:
    import simplejson as json
except ImportError:
    import json

from copy import deepcopy

from didery.routing import *
from didery.help import helping as h


SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
BAD_SK = b"\xcc\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
VK = b"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
DID = "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
PUT_URL = "{0}/{1}".format(BLOB_BASE_PATH, DID)

data = {
    "id": DID,
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6"
            "Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
    "changed": "2000-01-01T00:00:00+00:00"
}

verifyRequest = h.verifyPublicApiRequest


def basicValidation(reqFunc, url):
    # Test missing id field
    body = deepcopy(data)
    del body['id']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain id field."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing blob field
    body = deepcopy(data)
    del body['blob']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain blob field."
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

    # Test empty id field
    body = deepcopy(data)
    body['id'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "id field cannot be empty."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test empty blob field
    body = deepcopy(data)
    body['blob'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "blob field cannot be empty."
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

    # Test valid did format in id field
    body = deepcopy(data)
    body['id'] = "did:fake:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

    exp_result = {
        "title": "Validation Error",
        "description": "Invalid did format. Invalid DID method"
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    body = deepcopy(data)
    body['id'] = "did:dad"

    exp_result = {
        "title": "Validation Error",
        "description": "Invalid did format. Invalid DID value"
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    body = deepcopy(data)
    body['id'] = "fake:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

    exp_result = {
        "title": "Validation Error",
        "description": "Invalid did format. Invalid DID identifier"
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def signatureValidation(reqFunc, url):
    headers = {"Signature": ""}

    # Test missing Signature Header
    body = data

    exp_result = {
        "title": "Authorization Error",
        "description": "Empty Signature header."
    }

    verifyRequest(reqFunc, url, body, headers, exp_result, falcon.HTTP_401)

    body = json.dumps(data, ensure_ascii=False).encode('utf-8')
    exp_result = {
        "title": "Missing header value",
        "description": "The Signature header is required."
    }

    response = reqFunc(url, body=body)
    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    # Test missing signer tag in signature header
    body = data

    headers = {
        "Signature": 'test="' + h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), SK) + '"'
    }

    exp_result = {
        "title": "Authorization Error",
        "description": "Signature header missing \"signer\" tag and signature."
    }

    verifyRequest(reqFunc, url, body, headers, exp_result, falcon.HTTP_401)

    # Test invalid signature
    body = data

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request body and signature. Unverifiable signature."
    }

    headers = {"Signature": 'signer="{0}"'.format(h.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), BAD_SK))}

    verifyRequest(reqFunc, url, body, headers, exp_result, falcon.HTTP_401)


def testPostSignValidation(client):
    signatureValidation(client.simulate_post, BLOB_BASE_PATH)


def testPostValidation(client):
    basicValidation(client.simulate_post, BLOB_BASE_PATH)


def testValidPost(client):
    body = data

    # TODO:
    # assert response.content == exp_result
    verifyRequest(client.simulate_post, BLOB_BASE_PATH, body, exp_status=falcon.HTTP_200)


def testPutSignValidation(client):
    signatureValidation(client.simulate_put, PUT_URL)

    # Test url did matches id did
    body = deepcopy(data)
    body['id'] = "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="

    exp_result = {
        "title": "Validation Error",
        "description": "Url did must match id field did."
    }

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutValidation(client):
    # Test url missing did
    body = data

    exp_result = {
        "title": "Validation Error",
        "description": "DID value missing from url."
    }

    verifyRequest(client.simulate_put, BLOB_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Run basic tests
    basicValidation(client.simulate_put, PUT_URL)


def testValidPut(client):
    body = data

    # TODO:
    # assert response.content == exp_result
    verifyRequest(client.simulate_put, PUT_URL, body, exp_status=falcon.HTTP_200)
