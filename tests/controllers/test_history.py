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


SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"
VK = b"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="
DID = "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="

verifyRequest = h.verifyRequest


def testValidPost(client):
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_status=falcon.HTTP_200)
    # TODO:
    # assert response.content == expected_response


def testPostSignValidation(client):
    headers = {"Signature": ""}

    # Test missing Signature Header
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": "Empty Signature header."}'

    response = client.simulate_post(HISTORY_BASE_PATH, body=body, headers=headers)
    assert response.status == falcon.HTTP_401
    assert response.content == exp_result

    exp_result = b'{"title": "Missing header value", "description": "The Signature ' \
                 b'header is required."}'

    response = client.simulate_post(HISTORY_BASE_PATH, body=body)
    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing signer tag in signature header
    headers = {
        "Signature": 'test="' + h.signResource(body, SK) + '"'
    }

    exp_result = b'{"title": "Validation Error", "description": "' \
                 b'Signature header missing \\"signer\\" tag and signature."}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, headers, exp_result, falcon.HTTP_401)

    # Test invalid signature
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": "Could not validate the request body and signature. ' \
                 b'Unverifiable signature."}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_401)

    # Test the public key in the id field did matches the first public key in rotation history
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    exp_result = b'{"title": "Malformed Field", "description": "The DIDs key must match the first key in the ' \
                 b'signers field."}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testValidPostSignature(client):
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=" ' \
           b']' \
           b'}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_status=falcon.HTTP_200)
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

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test valid did format in id field
    body = b'{"id": "did:fake:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
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

    exp_result = b'{"title": "Invalid DID", "description": ' \
                 b'"Invalid DID method"}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    body = b'{"id": "did:fake", ' \
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

    exp_result = b'{"title": "Invalid DID", "description": ' \
                 b'"Malformed DID value"}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    body = b'{"id": "fake:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
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

    exp_result = b'{"title": "Invalid DID", "description": ' \
                 b'"Invalid DID identifier"}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing signers field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2' \
           b'}'

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain signers field."}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test invalid signers value
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ""' \
           b'}'

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signers field must be a list or array."}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has two keys
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[]' \
           b'}'

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"signers field must contain at least the current public key and its first pre-rotation."}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has two keys
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="' \
           b']' \
           b'}'
    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_status=falcon.HTTP_200)

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

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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
                 b'"signer field must equal 0 on creation of new rotation history."}'

    verifyRequest(client.simulate_post, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testPutSignValidation(client):
    url = HISTORY_BASE_PATH + '/{}'.format(DID)
    headers = {"Signature": ""}

    # Test url did matches id did
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

    exp_result = b'{"title": "Malformed \\"id\\" Field", "description": "Url did must match id field did."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing Signature Header
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": "Invalid or ' \
                 b'missing Signature header."}'

    verifyRequest(client.simulate_put, url, body, headers, exp_result, falcon.HTTP_401)

    exp_result = b'{"title": "Missing header value", "description": "The Signature ' \
                 b'header is required."}'

    response = client.simulate_put(url, body=body)
    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test partial signature header
    headers = {
        "Signature": 'signer="' + h.signResource(body, SK) + '"'
    }

    exp_result = b'{"title": "Validation Error", "description": "' \
                 b'Signature header missing signature for \\"rotation\\"."}'

    verifyRequest(client.simulate_put, url, body, headers, exp_result, falcon.HTTP_401)

    headers = {
        "Signature": 'rotation="' + h.signResource(body, SK) + '"'
    }

    exp_result = b'{"title": "Validation Error", "description": "' \
                 b'Signature header missing signature for \\"signer\\"."}'

    verifyRequest(client.simulate_put, url, body, headers, exp_result, falcon.HTTP_401)

    # Test invalid signer signature
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 1, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": "Could not validate the request signature for ' \
                 b'rotation field. Unverifiable signature."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_401)

    # Test invalid rotation signature
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 1, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": "Could not validate the request signature for ' \
                 b'signer field. Unverifiable signature."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_401)


def testPutValidation(client):
    url = '{0}/{1}'.format(HISTORY_BASE_PATH, DID)

    # Test that did already exists
    body = b'{"id": "did:dad:3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    exp_result = b'{"title": "Resource Not Found", "description": "Resource with did ' \
                 b'\\"did:dad:3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=\\" not found."}'

    verifyRequest(client.simulate_put,
                  "{0}/{1}".format(HISTORY_BASE_PATH, "did:dad:3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="),
                  body,
                  exp_result=exp_result,
                  exp_status=falcon.HTTP_404)

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

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test missing signers field
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2' \
           b'}'

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain signers field."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    exp_result = b'{"title": "Malformed \\"id\\" Field", "description": ' \
                 b'"id field cannot be empty."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    exp_result = b'{"title": "Malformed \\"changed\\" Field", "description": ' \
                 b'"changed field cannot be empty."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test invalid signers value
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ""' \
           b'}'

    exp_result = b'{"title": "Malformed \\"signers\\" Field", "description": ' \
                 b'"signers field must be a list or array."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has three keys
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="' \
           b']' \
           b'}'

    exp_result = b'{"title": "Invalid Request", "description": ' \
                 b'"PUT endpoint is for rotation events. Must contain at least the original key, a current signing ' \
                 b'key, and a pre-rotated key."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has three keys
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 2, ' \
           b'"signers": ' \
           b'[]' \
           b'}'

    exp_result = b'{"title": "Invalid Request", "description": ' \
                 b'"PUT endpoint is for rotation events. Must contain at least the original key, a current signing ' \
                 b'key, and a pre-rotated key."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has three keys
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"changed": "2000-01-01T00:00:01+00:00", ' \
           b'"signer": 1, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="' \
           b']' \
           b'}'

    verifyRequest(client.simulate_put, url, body, exp_status=falcon.HTTP_200)

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

    exp_result = b'{"title": "Malformed \\"signer\\" Field", "description": ' \
                 b'"signer field must be a number."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

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

    exp_result = b'{"title": "Malformed \\"signer\\" Field", "description": ' \
                 b'"\\"signer\\" cannot reference the first or last key in the \\"signers\\" field on PUT requests."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signer is not 0
    body = b'{"id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 0, ' \
           b'"signers": ' \
           b'[' \
           b'    "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=", ' \
           b'    "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=", ' \
           b'    "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=", ' \
           b'    "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=" ' \
           b']' \
           b'}'

    exp_result = b'{"title": "Malformed \\"signer\\" Field", "description": ' \
                 b'"\\"signer\\" cannot reference the first or last key in the \\"signers\\" field on PUT requests."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that signers field has a pre-rotated key
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

    exp_result = b'{"title": "Malformed \\"signer\\" Field", "description": ' \
                 b'"Missing pre rotated key in the signers field."}'

    verifyRequest(client.simulate_put, url, body, exp_result=exp_result, exp_status=falcon.HTTP_400)

    # Test that the url has a did in it
    body = b'{"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'"changed": "2000-01-01T00:00:00+00:00", ' \
           b'"signer": 1, ' \
           b'"signers": ' \
           b'[' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
           b'    "NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="' \
           b']' \
           b'}'

    exp_result = b'{"title": "Validation Error", "description": ' \
                 b'"DID value missing from url."}'

    verifyRequest(client.simulate_put, HISTORY_BASE_PATH, body, exp_result=exp_result, exp_status=falcon.HTTP_400)


def testGetAll(client):
    response = client.simulate_get(HISTORY_BASE_PATH)
    exp_result = b'{"data": [' \
                 b'{"history": {' \
                 b'"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
                 b'"changed": "2000-01-01T00:00:01+00:00", ' \
                 b'"signer": 1, ' \
                 b'"signers": [' \
                 b'"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
                 b'"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
                 b'"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="' \
                 b']' \
                 b'}, ' \
                 b'"signatures": {' \
                 b'"signer": "nsf4Dhz_R44dZsbggmXFH0tcaviXqbuIYRHZeK4vQt6W5hTiyOrI9H9ARyGm2oTgkBzcm7-cx7glgLjDwgfeCw==", ' \
                 b'"rotation": "nsf4Dhz_R44dZsbggmXFH0tcaviXqbuIYRHZeK4vQt6W5hTiyOrI9H9ARyGm2oTgkBzcm7-cx7glgLjDwgfeCw=="' \
                 b'}' \
                 b'}' \
                 b']' \
                 b'}'

    assert response.status == falcon.HTTP_200
    assert response.content == exp_result


def testGetOne(client):
    url = "{0}/{1}".format(HISTORY_BASE_PATH, DID)

    # Test basic valid Get One
    response = client.simulate_get(url)

    exp_result = b'{"history": {' \
                 b'"id": "did:dad:NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
                 b'"changed": "2000-01-01T00:00:01+00:00", ' \
                 b'"signer": 1, ' \
                 b'"signers": [' \
                 b'"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
                 b'"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=", ' \
                 b'"NOf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw="' \
                 b']' \
                 b'}, ' \
                 b'"signatures": {' \
                 b'"signer": "nsf4Dhz_R44dZsbggmXFH0tcaviXqbuIYRHZeK4vQt6W5hTiyOrI9H9ARyGm2oTgkBzcm7-cx7glgLjDwgfeCw==", ' \
                 b'"rotation": "nsf4Dhz_R44dZsbggmXFH0tcaviXqbuIYRHZeK4vQt6W5hTiyOrI9H9ARyGm2oTgkBzcm7-cx7glgLjDwgfeCw=="' \
                 b'}' \
                 b'}'

    assert response.status == falcon.HTTP_200
    assert response.content == exp_result

    # Test GET with non existent resource
    response = client.simulate_get("{0}/{1}".format(
        HISTORY_BASE_PATH,
        "did:dad:COf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=")
    )

    exp_result = b'{"title": "Resource Does Not Exist", "description": "Could not find resource with ' \
                 b'did \\"did:dad:COf6ZghvGNbFc_wr3CC0tKZHz1qWAR4lD5aM-i0zSjw=\\"."}'

    assert response.status == falcon.HTTP_404
    assert response.content == exp_result
