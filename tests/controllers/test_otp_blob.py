'''
    Tests can be run from the terminal with the following command:
        pytest tests/controllers

    To see test coverage install pytest-cov with pip then run this command:
        py.test --cov-report term-missing --cov=src/didery/controllers/ tests/controllers/
'''
import didery.crypto.eddsa as eddsa
import didery.crypto.ecdsa as ecdsa
import falcon
import libnacl

import tests.testing_utils.utils

try:
    import simplejson as json
except ImportError:
    import json

from collections import OrderedDict as ODict
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

verifyRequest = tests.testing_utils.utils.verifyPublicApiRequest


def genOtpBlob(seed=None, changed="2000-01-01T00:00:00+00:00", crypto="EdDSA"):
    if crypto == "EdDSA":
        if seed is None:
            seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
        vk, sk = eddsa.generateByteKeys(seed)
    else:
        vk, sk = ecdsa.generateByteKeys()

    did = h.makeDid(vk)
    body = {
        "id": did,
        "changed": changed,
        "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0Q"
                "D9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
    }

    return vk, sk, did, json.dumps(body, ensure_ascii=False).encode('utf-8')


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
    body['id'] = "did:dad"

    exp_result = {
        "title": "Validation Error",
        "description": "Invalid did format. Could not parse DID."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    body = deepcopy(data)
    body['id'] = "fake:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

    exp_result = {
        "title": "Validation Error",
        "description": "Invalid did format. Invalid Scheme Value."
    }

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def signatureValidation(reqFunc, url):
    headers = {"Signature": ""}

    # Test missing Signature Header
    body = deepcopy(data)

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
    body = deepcopy(data)

    headers = {
        "Signature": 'test="' + eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), SK) + '"'
    }

    exp_result = {
        "title": "Authorization Error",
        "description": 'Signature header missing signature for "signer".'
    }

    verifyRequest(reqFunc, url, body, headers, exp_result, falcon.HTTP_401)

    # Test invalid signature
    body = deepcopy(data)

    exp_result = {
        'title': 'Authorization Error',
        'description': 'Could not validate the request signature for signer field. Unverifiable signature.'
    }

    headers = {"Signature": 'signer="{0}"'.format(
        eddsa.signResource(json.dumps(body, ensure_ascii=False).encode('utf-8'), BAD_SK))}

    verifyRequest(reqFunc, url, body, headers, exp_result, falcon.HTTP_401)


def testPostSignValidation(client):
    signatureValidation(client.simulate_post, BLOB_BASE_PATH)


def testPostValidation(client):
    basicValidation(client.simulate_post, BLOB_BASE_PATH)


def testValidPost(client):
    body = deepcopy(data)

    signature = eddsa.signResource(json.dumps(body).encode(), SK)
    headers = {
        "Signature": 'signer="{0}"'.format(signature)
    }

    exp_result = {
        "otp_data": body,
        "signatures": {
            "signer": signature
        }
    }

    verifyRequest(client.simulate_post,
                  BLOB_BASE_PATH,
                  body,
                  headers=headers,
                  exp_status=falcon.HTTP_201,
                  exp_result=exp_result)


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


def testPutNonExistentResource(client):
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'

    # Test that did resource already exists
    vk, sk, did, body = genOtpBlob(seed)

    exp_result = {"title": "404 Not Found"}

    headers = {
        "Signature": 'signer="{}"'.format(eddsa.signResource(body, sk))
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(BLOB_BASE_PATH, did),
                  json.loads(body),
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_404)


def testPutUrlMissingDid(client):
    # Test url missing did
    body = deepcopy(data)

    exp_result = {
        "title": "Validation Error",
        "description": "DID value missing from url."
    }

    verifyRequest(client.simulate_put, BLOB_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutBasic(client):
    # Run basic tests
    basicValidation(client.simulate_put, PUT_URL)


def testPutUpdatedChangedField(client):
    # Test that changed field is greater than previous date
    seed = b'\x03\xa7w\xa6\x8c\xf3-&\xbf)\xdf\tk\xb5l\xc0-ry\x9bq\xecC\xbd\x1e\xe7\xdd\xe8\xad\x80\x95\x89'
    vk, sk, did, body = genOtpBlob(seed)

    headers = {
        "Signature": 'signer="{}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    exp_result = {
        "title": "Validation Error",
        "description": "\"changed\" field not later than previous update."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(BLOB_BASE_PATH, did),
                  json.loads(body),
                  headers,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_400)


def testValidPut(client):
    body = deepcopy(data)

    verifyRequest(client.simulate_post, BLOB_BASE_PATH, body, exp_status=falcon.HTTP_201)

    body['changed'] = "2000-01-01T00:00:01+00:00"

    signature = eddsa.signResource(json.dumps(body).encode(), SK)
    headers = {
        "Signature": 'signer="{0}"'.format(signature)
    }

    exp_result = {
        "otp_data": body,
        "signatures": {
            "signer": signature
        }
    }

    verifyRequest(client.simulate_put,
                  PUT_URL,
                  body,
                  headers=headers,
                  exp_status=falcon.HTTP_200,
                  exp_result=exp_result)


def testGetOneEmptyDB(client):
    # Test Get One with empty DB
    response = client.simulate_get("{0}/{1}".format(BLOB_BASE_PATH, DID))

    assert response.status == falcon.HTTP_404


def testValidGetOne(client):
    # Test basic valid Get One
    body = deepcopy(data)
    signature = eddsa.signResource(json.dumps(body).encode(), SK)

    headers = {
        "Signature": 'signer="{}"'.format(signature)
    }

    client.simulate_post(BLOB_BASE_PATH, body=json.dumps(body).encode(), headers=headers)

    response = client.simulate_get("{0}/{1}".format(BLOB_BASE_PATH, DID))

    exp_result = {
        "otp_data": {
            "id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=",
            "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9y"
                    "juKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
            "changed": "2000-01-01T00:00:00+00:00"
        },
        "signatures": {
            "signer": signature
        }
    }

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result


def testGetOneNonExistentResource(client):
    # Test GET with non existent resource
    response = client.simulate_get("{0}/{1}".format(
        BLOB_BASE_PATH,
        "did:dad:COf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=")
    )

    exp_result = {"title": "404 Not Found"}

    assert response.status == falcon.HTTP_404
    assert json.loads(response.content) == exp_result


def testGetAllInvalidQueryString(client):
    # Test that query params have values
    response = client.simulate_get(BLOB_BASE_PATH, query_string="offset&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string missing value(s)."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(BLOB_BASE_PATH, query_string="offset=10&limit")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string missing value(s)."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testGetAllInvalidQueryValue(client):
    # Test that query params values are ints
    response = client.simulate_get(BLOB_BASE_PATH, query_string="offset=a&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(BLOB_BASE_PATH, query_string="offset=10&limit=d")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testGetAllEmptyQueryValue(client):
    response = client.simulate_get(BLOB_BASE_PATH, query_string="offset=10&limit=")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(BLOB_BASE_PATH, query_string="offset=&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testGetAll(client):
    # setup
    vk1, sk1, did1, body1 = genOtpBlob()

    signature1 = eddsa.signResource(body1, sk1)

    headers = {
        "Signature": 'signer="{}"'.format(signature1)
    }

    client.simulate_post(BLOB_BASE_PATH, body=body1, headers=headers)  # Add did to database

    vk2, sk2, did2, body2 = genOtpBlob()

    signature2 = eddsa.signResource(body2, sk2)

    headers = {
        "Signature": 'signer="{}"'.format(signature2)
    }

    client.simulate_post(BLOB_BASE_PATH, body=body2, headers=headers)  # Add did to database

    # Test get all
    response = client.simulate_get(BLOB_BASE_PATH)

    resp_data = json.loads(response.content)
    body1 = json.loads(body1)
    body2 = json.loads(body2)

    assert response.status == falcon.HTTP_200
    assert "data" in resp_data
    assert len(resp_data["data"]) == 2

    resp_blob1 = resp_data["data"][0]
    resp_blob2 = resp_data["data"][1]

    assert resp_blob1["otp_data"]["id"] == body1["id"] or resp_blob2["otp_data"]["id"] == body1["id"]
    assert resp_blob1["otp_data"]["id"] == body2["id"] or resp_blob2["otp_data"]["id"] == body2["id"]
    assert resp_blob1["otp_data"]["id"] == body2["id"] or resp_blob2["otp_data"]["id"] == body2["id"]

    assert resp_blob1["signatures"]["signer"] == signature1 or resp_blob2["signatures"]["signer"] == signature1
    assert resp_blob1["signatures"]["signer"] == signature2 or resp_blob2["signatures"]["signer"] == signature2

    # Test offset and limit
    response = client.simulate_get(BLOB_BASE_PATH, query_string="offset=100&limit=10")

    exp_result = {}

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result


def testDeleteUrlMissingDid(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = genOtpBlob(seed)

    # Test missing url did
    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, sk))}

    response = client.simulate_delete(BLOB_BASE_PATH, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_400
    assert resp_content["title"] == "Validation Error"
    assert resp_content["description"] == "DID value missing from url."


def testDeleteNoSignatureHeader(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = genOtpBlob(seed)
    url = "{0}/{1}".format(BLOB_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()

    response = client.simulate_delete(url, body=data)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_400
    assert resp_content["title"] == "Missing header value"
    assert resp_content["description"] == "The Signature header is required."


def testDeleteEmptySignatureHeader(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = genOtpBlob(seed)
    url = "{0}/{1}".format(BLOB_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": ""}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_401
    assert resp_content["title"] == "Authorization Error"
    assert resp_content["description"] == "Empty Signature header."


def testDeleteBadSignatureHeader(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = genOtpBlob(seed)
    url = "{0}/{1}".format(BLOB_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'rotation="{0}"'.format(eddsa.signResource(data, sk))}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_401
    assert resp_content["title"] == "Authorization Error"
    assert resp_content["description"] == 'Signature header missing signature for "signer".'


def testDeleteMismatchedDids(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = genOtpBlob(seed)
    url = "{0}/{1}".format(BLOB_BASE_PATH, DID)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, sk))}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_400
    assert resp_content["title"] == "Validation Error"
    assert resp_content["description"] == "Url did must match id field did."


def testDeleteNonExistentResource(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = genOtpBlob(seed)
    url = "{0}/{1}".format(BLOB_BASE_PATH, did)
    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, sk))}

    client.simulate_delete(url, body=data, headers=headers)
    response = client.simulate_delete(url, body=data, headers=headers)

    assert response.status == falcon.HTTP_404


def testDeleteInvalidSignature(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = genOtpBlob(seed)
    url = "{0}/{1}".format(BLOB_BASE_PATH, did)

    headers = {
        "Signature": 'signer="{0}"'.format(eddsa.signResource(body, sk))
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, SK))}

    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_401
    assert resp_content["title"] == "Authorization Error"
    assert resp_content["description"] == "Could not validate the request signature for signer field. Unverifiable signature."


def testValidDelete(client):
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = genOtpBlob(seed)
    url = "{0}/{1}".format(BLOB_BASE_PATH, did)

    signature = eddsa.signResource(body, sk)
    headers = {
        "Signature": 'signer="{0}"'.format(signature)
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'signer="{0}"'.format(eddsa.signResource(data, sk))}
    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_200
    assert resp_content["deleted"]["otp_data"] == json.loads(body)
    assert resp_content["deleted"]["signatures"]["signer"] == signature


def testValidEcdsaPost(client):
    cryptoScheme = "ECDSA"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    exp_result = {
        "otp_data": json.loads(body),
        "signatures": {
            "name": cryptoScheme,
            "signer": signature
        }
    }

    verifyRequest(client.simulate_post,
                  BLOB_BASE_PATH,
                  json.loads(body),
                  headers=headers,
                  exp_status=falcon.HTTP_201,
                  exp_result=exp_result)


def testValidSecp256k1Post(client):
    cryptoScheme = "secp256k1"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    exp_result = {
        "otp_data": json.loads(body),
        "signatures": {
            "name": cryptoScheme,
            "signer": signature
        }
    }

    verifyRequest(client.simulate_post,
                  BLOB_BASE_PATH,
                  json.loads(body),
                  headers=headers,
                  exp_status=falcon.HTTP_201,
                  exp_result=exp_result)


def testInvalidEcdsaPostSig(client):
    cryptoScheme = "ECDSA"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    body = json.loads(body)
    body['changed'] = "2000-01-01T11:11:11+11:11"

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for signer field. Unverifiable signature."
    }

    verifyRequest(client.simulate_post,
                  BLOB_BASE_PATH,
                  body,
                  headers=headers,
                  exp_status=falcon.HTTP_401,
                  exp_result=exp_result)


def testInvalidSecp256k1PostSig(client):
    cryptoScheme = "secp256k1"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    body = json.loads(body)
    body['changed'] = "2000-01-01T11:11:11+11:11"

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for signer field. Unverifiable signature."
    }

    verifyRequest(client.simulate_post,
                  BLOB_BASE_PATH,
                  body,
                  headers=headers,
                  exp_status=falcon.HTTP_401,
                  exp_result=exp_result)


def testValidEcdsaPut(client):
    cryptoScheme = "ECDSA"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    verifyRequest(client.simulate_post, BLOB_BASE_PATH, json.loads(body), headers=headers, exp_status=falcon.HTTP_201)

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"

    signature = ecdsa.signResource(json.dumps(body).encode(), sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    exp_result = {
        "otp_data": body,
        "signatures": {
            "name": cryptoScheme,
            "signer": signature
        }
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(BLOB_BASE_PATH, did),
                  body,
                  headers=headers,
                  exp_status=falcon.HTTP_200,
                  exp_result=exp_result)


def testValidSecp256k1Put(client):
    cryptoScheme = "secp256k1"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    verifyRequest(client.simulate_post, BLOB_BASE_PATH, json.loads(body), headers=headers, exp_status=falcon.HTTP_201)

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"

    signature = ecdsa.signResource(json.dumps(body).encode(), sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    exp_result = {
        "otp_data": body,
        "signatures": {
            "name": cryptoScheme,
            "signer": signature
        }
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(BLOB_BASE_PATH, did),
                  body,
                  headers=headers,
                  exp_status=falcon.HTTP_200,
                  exp_result=exp_result)


def testInvalidEcdsaPutSig(client):
    cryptoScheme = "ECDSA"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    verifyRequest(client.simulate_post, BLOB_BASE_PATH, json.loads(body), headers=headers, exp_status=falcon.HTTP_201)

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"

    signature = ecdsa.signResource(json.dumps(body).encode(), sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    # Invalidate Signature
    body['changed'] = "2000-01-01T11:11:11+11:11"

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for signer field. Unverifiable signature."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(BLOB_BASE_PATH, did),
                  body,
                  headers=headers,
                  exp_status=falcon.HTTP_401,
                  exp_result=exp_result)


def testInvalidSecp256k1PutSig(client):
    cryptoScheme = "secp256k1"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    verifyRequest(client.simulate_post, BLOB_BASE_PATH, json.loads(body), headers=headers, exp_status=falcon.HTTP_201)

    body = json.loads(body)
    body['changed'] = "2000-01-01T00:00:01+00:00"

    signature = ecdsa.signResource(json.dumps(body).encode(), sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    # Invalidate Signature
    body['changed'] = "2000-01-01T11:11:11+11:11"

    exp_result = {
        "title": "Authorization Error",
        "description": "Could not validate the request signature for signer field. Unverifiable signature."
    }

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(BLOB_BASE_PATH, did),
                  body,
                  headers=headers,
                  exp_status=falcon.HTTP_401,
                  exp_result=exp_result)


def testValidEcdsaDelete(client):
    cryptoScheme = "ECDSA"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)
    url = "{0}/{1}".format(BLOB_BASE_PATH, did)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, ecdsa.signResource(data, sk))}
    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_200
    assert resp_content["deleted"]["otp_data"] == json.loads(body)
    assert resp_content["deleted"]["signatures"]["signer"] == signature


def testValidSecp256k1Delete(client):
    cryptoScheme = "secp256k1"

    vk, sk, did, body = genOtpBlob(crypto=cryptoScheme)
    url = "{0}/{1}".format(BLOB_BASE_PATH, did)

    signature = ecdsa.signResource(body, sk)
    headers = {
        "Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, signature)
    }

    client.simulate_post(BLOB_BASE_PATH, body=body, headers=headers)  # Add did to database

    data = json.dumps({"id": did}, ensure_ascii=False).encode()
    headers = {"Signature": 'name="{0}"; signer="{1}"'.format(cryptoScheme, ecdsa.signResource(data, sk))}
    response = client.simulate_delete(url, body=data, headers=headers)

    resp_content = json.loads(response.content)

    assert response.status == falcon.HTTP_200
    assert resp_content["deleted"]["otp_data"] == json.loads(body)
    assert resp_content["deleted"]["signatures"]["signer"] == signature
