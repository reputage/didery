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


PUT_URL = "{0}/{1}".format(BLOB_BASE_PATH, "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=")


def basicValidation(reqFunc, url):
    # Test missing id field
    body = b'{' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'
    response = reqFunc(url, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain id field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing blob field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'
    response = reqFunc(url, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain blob field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing changed field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'   "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9y' \
           b'juKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"' \
           b'}'
    response = reqFunc(url, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain changed field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty id field
    body = b'{"id": "", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'
    response = reqFunc(url, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"id field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty blob field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'
    response = reqFunc(url, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"blob field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": ""' \
           b'}'
    response = reqFunc(url, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"changed field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result


def testPostValidation(client):
    basicValidation(client.simulate_post, BLOB_BASE_PATH)


def testValidPost(client):
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'
    response = client.simulate_post(BLOB_BASE_PATH, body=body)

    assert response.status == falcon.HTTP_200
    # TODO:
    # assert response.content == exp_result


def testPutValidation(client):
    # Test url missing did
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'
    response = client.simulate_put(BLOB_BASE_PATH, body=body)

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"DID value missing from url."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test did in url matches id field did
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'
    response = client.simulate_put(
        "{0}/{1}".format(BLOB_BASE_PATH, "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="),
        body=body
    )

    exp_result = b'{"title": "Malformed \\"id\\" Field", "description": ' \
                 b'"Url did must match id field did."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    basicValidation(client.simulate_put, PUT_URL)


def testValidPut(client):
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw", ' \
           b'"changed": "2000-01-01T00:00:00+00:00"' \
           b'}'
    response = client.simulate_put(PUT_URL, body=body)

    assert response.status == falcon.HTTP_200
    # TODO:
    # assert response.content == exp_result
