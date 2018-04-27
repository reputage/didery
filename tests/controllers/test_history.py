import falcon
try:
    import simplejson as json
except ImportError:
    import json

from didery.routing import *


def testPostValidation(client):
    # Test missing id field
    body = b'{' \
            b'"changed" : "2000-01-01T00:00:00+00:00", ' \
            b'"signer": 2, ' \
            b'"signers": ' \
            b'[' \
            b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
            b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
            b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
            b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
            b']' \
            b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain id field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing changed field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain changed field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing signer field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed" : "2000-01-01T00:00:00+00:00", ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain signer field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing signers field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed" : "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain signers field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result


def testValidPost(client):
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed" : "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    response = client.simulate_post(HISTORY_BASE_PATH, body=body)
    assert response.status == falcon.HTTP_200
    # TODO:
    # assert response.content == expected_response
