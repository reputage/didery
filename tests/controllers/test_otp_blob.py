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

from didery.routing import *
from didery.help import helping as h


PUT_URL = "{0}/{1}".format(BLOB_BASE_PATH, "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=")
SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
BAD_SK = b"\xcc\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
VK = b"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
DID = "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

verifyRequest = h.verifyRequest


def basicValidation(reqFunc, url):
    # Test missing id field
    body = b'{' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain id field."}'

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing blob field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain blob field."}'

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing changed field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'   "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9y' \
           b'juKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"' \
           b'}'

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain changed field."}'

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test empty id field
    body = b'{"id": "", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"id field cannot be empty."}'

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test empty blob field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"blob field cannot be empty."}'

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test empty changed field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": ""' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"changed field cannot be empty."}'

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test valid did format in id field
    body = b'{"id": "did:fake:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"Invalid did format. Invalid DID method"}'

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    body = b'{"id": "did:dad", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"Invalid did format. Invalid DID value"}'

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    body = b'{"id": "fake:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"Invalid did format. Invalid DID identifier"}'

    verifyRequest(reqFunc, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def signatureValidation(reqFunc, url):
    headers = {"Signature": ""}

    # Test missing Signature Header
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Authorization Error", "description": "Empty Signature header."}'

    verifyRequest(reqFunc, url, body, headers, exp_result, falcon.HTTP_401)

    exp_result = b'{"title": "Missing header value", "description": "The Signature ' \
                 b'header is required."}'

    response = reqFunc(url, body=body)
    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing signer tag in signature header
    headers = {
        "Signature": 'test="' + h.signResource(body, SK) + '"'
    }

    exp_result = b'{"title": "Authorization Error", "description": "' \
                 b'Signature header missing \\"signer\\" tag and signature."}'

    verifyRequest(reqFunc, url, body, headers, exp_result, falcon.HTTP_401)

    # Test invalid signature
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Authorization Error", "description": "Could not validate the request body and signature. ' \
                 b'Unverifiable signature."}'

    headers = {"Signature": 'signer="{0}"'.format(h.signResource(body, BAD_SK))}

    verifyRequest(reqFunc, url, body, headers, exp_result, falcon.HTTP_401)


def testPostSignValidation(client):
    signatureValidation(client.simulate_post, BLOB_BASE_PATH)


def testPostValidation(client):
    basicValidation(client.simulate_post, BLOB_BASE_PATH)


def testValidPost(client):
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    verifyRequest(client.simulate_post, BLOB_BASE_PATH, body, exp_status=falcon.HTTP_200)
    # TODO:
    # assert response.content == exp_result


def testPutSignValidation(client):
    signatureValidation(client.simulate_put, PUT_URL)

    # Test url did matches id did
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": "Url did must match id field did."}'

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutValidation(client):
    # Test url missing did
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"DID value missing from url."}'

    verifyRequest(client.simulate_put, BLOB_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test did in url matches id field did
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"Url did must match id field did."}'

    verifyRequest(client.simulate_put, PUT_URL, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Run basic tests
    basicValidation(client.simulate_put, PUT_URL)


def testValidPut(client):
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'

    verifyRequest(client.simulate_put, PUT_URL, body, exp_status=falcon.HTTP_200)
    # TODO:
    # assert response.content == exp_result
