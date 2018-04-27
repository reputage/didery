import falcon
try:
    import simplejson as json
except ImportError:
    import json

from didery.routing import *


def testPostValidation(client):
    # Test missing id field
    body = b'{' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"' \
           b'}'
    response = client.simulate_post(BLOB_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain id field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing blob field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="}'
    response = client.simulate_post(BLOB_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain blob field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty id field
    body = b'{"id": "", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"' \
           b'}'
    response = client.simulate_post(BLOB_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"id field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty blob field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": ""' \
           b'}'
    response = client.simulate_post(BLOB_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"blob field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result


def testValidPost(client):
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHN' \
           b'JZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"' \
           b'}'
    response = client.simulate_post(BLOB_BASE_PATH, body=body)
    assert response.status == falcon.HTTP_200
    # TODO:
    # assert response.content == exp_result
