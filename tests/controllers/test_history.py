import falcon
try:
    import simplejson as json
except ImportError:
    import json

from didery.routing import *
from didery.help import helping


SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
VK = b"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="


def runPostTest(client, body, exp_result=None, exp_status=None):
    headers = {
        "Signature": 'signer="' + helping.signResource(body, SK) + '"; rotation="' + helping.signResource(body,
                                                                                                          SK) + '"'
    }

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)

    if exp_status is not None:
        assert response.status == exp_status
    if exp_result is not None:
        assert response.content == exp_result


def testPostSignValidation(client):
    headers = {"Signature": ""}

    # Test missing Signature Header
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

    exp_result = b'{"title": "Validation Error", "description": "Invalid or ' \
                 b'missing Signature header."}'

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
    assert response.status == falcon.HTTP_401
    assert response.content == exp_result

    exp_result = b'{"title": "Missing header value", "description": "The Signature ' \
                 b'header is required."}'

    response = client.simulate_post(HISTORY_BASE_PATH, body=body)
    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test partial signature header
    headers = {
        "Signature": 'signer="' + helping.signResource(body, SK) + '"'
    }

    exp_result = b'{"title": "Validation Error", "description": "' \
                 b'Signature header missing signature for \\"rotation\\"."}'

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
    assert response.status == falcon.HTTP_401
    assert response.content == exp_result

    headers = {
        "Signature": 'rotation="' + helping.signResource(body, SK) + '"'
    }

    exp_result = b'{"title": "Validation Error", "description": "' \
                 b'Signature header missing signature for \\"signer\\"."}'

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
    assert response.status == falcon.HTTP_401
    assert response.content == exp_result


def testValidPostSignature(client):
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=" ' \
           b']' \
           b'}'

    runPostTest(client, body, None, falcon.HTTP_200)
    # TODO:
    # assert response.content == exp_result


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

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain id field."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

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

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain changed field."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

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

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain signer field."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

    # Test missing signers field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2' \
           b'}'

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain signers field."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

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

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"id field cannot be empty."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

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

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"changed field cannot be empty."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

    # Test invalid signers value
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ""' \
           b'}'

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signers field must be a list or array."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

    # Test that signers field has two keys
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="' \
           b']' \
           b'}'

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signers field must contain at least the current public key and its first pre-rotation."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

    # Test that signers field has two keys
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[]' \
           b'}'

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signers field must contain at least the current public key and its first pre-rotation."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

    # Test that signers field has two keys
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="' \
           b']' \
           b'}'
    runPostTest(client, body, None, falcon.HTTP_200)

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

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signer field must be a number."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

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

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signer field must be between 0 and size of signers field."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)

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

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"Missing pre rotated key in the signers field."}'

    runPostTest(client, body, exp_result, falcon.HTTP_400)


def testValidPost(client):
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=" ' \
           b']' \
           b'}'

    runPostTest(client, body, None, falcon.HTTP_200)
    # TODO:
    # assert response.content == expected_response
