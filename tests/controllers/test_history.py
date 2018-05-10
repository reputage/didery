import falcon
try:
    import simplejson as json
except ImportError:
    import json

from didery.routing import *


def testPostValidation(client):
    # Test missing id field
    body = b'{' \
            b'"changed": "2000-01-01T00:00:00+00:00", ' \
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
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
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
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain signers field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty id field
    body = b'{"id": "", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
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

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"id field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty changed field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "", ' \
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

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"changed field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test invalid signers value
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ""' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signers field must be a list or array."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test that signers field has two keys
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="' \
           b']' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signers field must contain at least the current public key and its first pre-rotation."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[]' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signers field must contain at least the current public key and its first pre-rotation."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148="' \
           b']' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)
    assert response.status == falcon.HTTP_200

    # Test that signer field is an int
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": "a", ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signer field must be a number."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test that signer field is a valid index into signers field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 4, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signer field must be between 0 and size of signers field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test that there is a pre-rotated key included in signers field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 3, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'
    response = client.simulate_post(HISTORY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"Missing pre rotated key in the signers field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result


def testValidPost(client):
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
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
