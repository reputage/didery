import falcon
try:
    import simplejson as json
except ImportError:
    import json

from didery.routing import *


def testPostValidation(client):
    # Test missing host_address field
    body = b'{' \
           b'"port": 7541, ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain host_address field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing port field
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain port field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing name field
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"main": true' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain name field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty host_address
    body = b'{' \
           b'"host_address": "", ' \
           b'"port": "a", ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"host_address field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty port
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": "", ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"port field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty name
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"name": "", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"name field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty main
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"name": "alpha", ' \
           b'"main": ""' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"main field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test invalid bool for main
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"name": "alpha", ' \
           b'"main": "a"' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"main field must be a boolean value."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test invalid port values
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": "a", ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"port field must be a number."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 70000, ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"port field must be a number between 1 and 65535."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result


def testValidPost(client):
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_post(RELAY_BASE_PATH, body=body)
    assert response.status == falcon.HTTP_200
    # TODO:
    # assert response.content == exp_result


def testPutValidation(client):
    uid = 1
    # Test missing host_address field
    body = b'{' \
           b'"port": 7541, ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain host_address field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing port field
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain port field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing name field
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Missing Required Field", "description": ' \
                 b'"Request must contain name field."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty host_address
    body = b'{' \
           b'"host_address": "", ' \
           b'"port": "a", ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"host_address field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty port
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": "", ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"port field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty name
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"name": "", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"name field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test empty main
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"name": "alpha", ' \
           b'"main": ""' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"main field cannot be empty."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test invalid bool for main
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"name": "alpha", ' \
           b'"main": "a"' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"main field must be a boolean value."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test invalid port values
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": "a", ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"port field must be a number."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 70000, ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)

    exp_result = b'{"title": "Malformed Field", "description": ' \
                 b'"port field must be a number between 1 and 65535."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result

    # Test missing uid
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}".format(RELAY_BASE_PATH), body=body)

    exp_result = b'{"title": "Incomplete Request", "description": ' \
                 b'"uid required."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result


def testValidPut(client):
    uid = 1
    body = b'{' \
           b'"host_address": "127.0.0.1", ' \
           b'"port": 7541, ' \
           b'"name": "alpha", ' \
           b'"main": true' \
           b'}'
    response = client.simulate_put("{0}/{1}".format(RELAY_BASE_PATH, uid), body=body)
    print(response.content)
    assert response.status == falcon.HTTP_200
    # TODO:
    # assert response.content == exp_result


def testDeleteValidation(client):
    response = client.simulate_delete("{0}".format(RELAY_BASE_PATH))

    exp_result = b'{"title": "Incomplete Request", "description": ' \
                 b'"uid required."}'

    assert response.status == falcon.HTTP_400
    assert response.content == exp_result


def testValidDelete(client):
    response = client.simulate_delete("{0}/{1}".format(RELAY_BASE_PATH, 1))

    assert response.status == falcon.HTTP_200
    # TODO:
    # assert response.content == exp_result
