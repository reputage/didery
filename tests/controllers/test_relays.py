'''
    Tests can be run from the terminal with the following command:
        pytest tests/controllers

    To see test coverage install pytest-cov with pip then run this command:
        py.test --cov-report term-missing --cov=src/didery/controllers/ tests/controllers/
'''

import falcon

import tests.testing_utils.utils

try:
    import simplejson as json
except ImportError:
    import json

from copy import deepcopy

from didery.routing import *
from didery.help import helping as h


verifyRequest = tests.testing_utils.utils.verifyManagementApiRequest

data = {
    "host_address": "127.0.0.1",
    "port": 7541,
    "name": "alpha",
    "main": True,
    "changed": "2000-01-01T00:00:00+00:00",
    "uid": 1
}


def addTestData(client):
    body = deepcopy(data)
    del body['uid']

    response = client.simulate_post(RELAY_BASE_PATH, body=json.dumps(body, ensure_ascii=False))

    return json.loads(response.content)['uid']


def basicValidation(reqFunc, url):
    # Test missing host_address field
    body = deepcopy(data)
    del body['host_address']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain host_address field."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test missing port field
    body = deepcopy(data)
    del body['port']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain port field."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test missing name field
    body = deepcopy(data)
    del body['name']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain name field."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test missing changed field
    body = deepcopy(data)
    del body['changed']

    exp_result = {
        "title": "Missing Required Field",
        "description": "Request must contain changed field."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test empty host_address
    body = deepcopy(data)
    body['host_address'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "host_address field cannot be empty."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test empty port
    body = deepcopy(data)
    body['port'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "port field cannot be empty."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test empty name
    body = deepcopy(data)
    body['name'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "name field cannot be empty."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test empty main
    body = deepcopy(data)
    body['main'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "main field cannot be empty."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test empty changed
    body = deepcopy(data)
    body['changed'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "changed field cannot be empty."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test invalid bool for main
    body = deepcopy(data)
    body['main'] = "a"

    exp_result = {
        "title": "Validation Error",
        "description": "main field must be a boolean value."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    # Test invalid port values
    body = deepcopy(data)
    body['port'] = "a"

    exp_result = {
        "title": "Validation Error",
        "description": "port field must be a number."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    body = deepcopy(data)
    body['port'] = 70000

    exp_result = {
        "title": "Validation Error",
        "description": "port field must be a number between 1 and 65535."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)

    body = deepcopy(data)
    body['port'] = 0

    exp_result = {
        "title": "Validation Error",
        "description": "port field must be a number between 1 and 65535."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)


def testPostValidation(client):
    basicValidation(client.simulate_post, RELAY_BASE_PATH)

    # Test uid in post request
    body = deepcopy(data)

    exp_result = {
        "title": "Validation Error",
        "description": "If uid is known use PUT."
    }

    verifyRequest(client.simulate_post, RELAY_BASE_PATH, body, exp_result, falcon.HTTP_400)


def testValidPost(client):
    body = deepcopy(data)
    del body['uid']

    # TODO:
    # assert response.content == exp_result
    verifyRequest(client.simulate_post, RELAY_BASE_PATH, body, exp_status=falcon.HTTP_201)

    body = deepcopy(data)
    del body['uid']
    del body['main']

    verifyRequest(client.simulate_post, RELAY_BASE_PATH, body, exp_status=falcon.HTTP_201)


def testPutValidation(client):
    url = "{}/1".format(RELAY_BASE_PATH)

    basicValidation(client.simulate_put, url)

    # Test missing uid in url
    body = deepcopy(data)

    exp_result = {
        "title": "Validation Error",
        "description": "uid required in url."
    }

    verifyRequest(client.simulate_put, RELAY_BASE_PATH, body, exp_result, falcon.HTTP_400)

    # Test url uid matches the uid in the body
    body = deepcopy(data)

    exp_result = {
        "title": "Validation Error",
        "description": "uid in url must match uid in body."
    }

    verifyRequest(client.simulate_put, "{}/2".format(RELAY_BASE_PATH), body, exp_result, falcon.HTTP_400)

    # Test url uid matches the uid in the body
    body = deepcopy(data)
    body['uid'] = "2"

    exp_result = {"title": "404 Not Found"}

    verifyRequest(client.simulate_put, "{}/2".format(RELAY_BASE_PATH), body, exp_result, falcon.HTTP_404)

    # Test changed field has been updated
    uid = addTestData(client)
    body = deepcopy(data)
    body['uid'] = uid

    exp_result = {
        "title": "Validation Error",
        "description": "\"changed\" field not later than previous update."
    }

    verifyRequest(client.simulate_put, "{0}/{1}".format(RELAY_BASE_PATH, uid), body, exp_result, falcon.HTTP_400)


def testValidPut(client):
    uid = addTestData(client)
    url = "{0}/{1}".format(RELAY_BASE_PATH, uid)

    # TODO:
    # assert response.content == exp_result
    body = deepcopy(data)
    body['uid'] = uid
    body['changed'] = "2000-01-01T00:00:01+00:00"

    verifyRequest(client.simulate_put, url, body, exp_status=falcon.HTTP_200)

    # Test request without uid in body
    body = deepcopy(data)
    del body['uid']
    body['changed'] = "2000-01-01T00:00:02+00:00"

    verifyRequest(client.simulate_put, url, body, exp_status=falcon.HTTP_200)

    # Test empty uid values
    body = deepcopy(data)
    body['uid'] = ""
    body['changed'] = "2000-01-01T00:00:03+00:00"

    verifyRequest(client.simulate_put, url, body, exp_status=falcon.HTTP_200)


def testGetAllValidation(client):
    # Test that query params have values
    response = client.simulate_get(RELAY_BASE_PATH, query_string="offset&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string missing value(s)."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(RELAY_BASE_PATH, query_string="offset=10&limit")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string missing value(s)."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    # Test that query params values are ints
    response = client.simulate_get(RELAY_BASE_PATH, query_string="offset=a&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(RELAY_BASE_PATH, query_string="offset=10&limit=d")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(RELAY_BASE_PATH, query_string="offset=10&limit=")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(RELAY_BASE_PATH, query_string="offset=&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testGetAll(client):
    response = client.simulate_get(RELAY_BASE_PATH)

    resp = json.loads(response.content)

    assert response.status == falcon.HTTP_200
    assert len(resp) == 4

    for val in resp.items():
        assert val[0] == val[1]['uid']
        assert val[1]['host_address'] == "127.0.0.1"
        assert val[1]['port'] == 7541
        assert val[1]['name'] == "alpha"
        assert val[1]['status'] == "connected"

    response = client.simulate_get(RELAY_BASE_PATH, query_string="offset=100&limit=10")

    exp_result = {}

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result


def testDeleteValidation(client):
    # Test that uid is in url
    exp_result = {
        "title": "Validation Error",
        "description": "uid required in url."
    }

    verifyRequest(client.simulate_delete, RELAY_BASE_PATH, exp_result=exp_result,  exp_status=falcon.HTTP_400)

    # Test resource exists
    exp_result = {"title": "404 Not Found"}

    verifyRequest(
        client.simulate_delete,
        "{0}/5".format(RELAY_BASE_PATH),
        exp_result=exp_result,
        exp_status=falcon.HTTP_404
    )


def testValidDelete(client):
    uid = addTestData(client)

    response = client.simulate_get(RELAY_BASE_PATH)

    assert uid in json.loads(response.content)

    verifyRequest(client.simulate_delete, "{0}/{1}".format(RELAY_BASE_PATH, uid), exp_status=falcon.HTTP_200)

    response = client.simulate_get(RELAY_BASE_PATH)

    assert uid not in json.loads(response.content)
