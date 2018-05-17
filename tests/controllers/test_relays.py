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

from copy import deepcopy

from didery.routing import *
from didery.help import helping as h


verifyRequest = h.verifyManagementApiRequest

data = {
    "host_address": "127.0.0.1",
    "port": 7541,
    "name": "alpha",
    "main": True,
    "changed": "2000-01-01T00:00:00+00:00",
    "uid": 1
}


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

    # Test empty uid
    body = deepcopy(data)
    body['uid'] = ""

    exp_result = {
        "title": "Validation Error",
        "description": "uid field cannot be empty."
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

    # Test invalid uid values
    body = deepcopy(data)
    body['uid'] = "a"

    exp_result = {
        "title": "Validation Error",
        "description": "uid field must be a number."
    }

    verifyRequest(reqFunc, url, body, exp_result, falcon.HTTP_400)


def testPostValidation(client):
    basicValidation(client.simulate_post, RELAY_BASE_PATH)


def testValidPost(client):
    body = deepcopy(data)
    del body['uid']

    # TODO:
    # assert response.content == exp_result
    verifyRequest(client.simulate_post, RELAY_BASE_PATH, body, exp_status=falcon.HTTP_201)

    # Test valid uid values
    body = deepcopy(data)
    body['uid'] = 1

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

    # Test url uid is an int
    body = deepcopy(data)

    exp_result = {
        "title": "Validation Error",
        "description": "uid in url must be a number."
    }

    verifyRequest(client.simulate_put, "{}/a".format(RELAY_BASE_PATH), body, exp_result, falcon.HTTP_400)

    # Test url uid matches the uid in the body
    body = deepcopy(data)

    exp_result = {
        "title": "Validation Error",
        "description": "uid in url must match uid in body."
    }

    verifyRequest(client.simulate_put, "{}/2".format(RELAY_BASE_PATH), body, exp_result, falcon.HTTP_400)


def testValidPut(client):
    url = "{0}/1".format(RELAY_BASE_PATH)

    # TODO:
    # assert response.content == exp_result
    body = deepcopy(data)
    verifyRequest(client.simulate_put, url, body, exp_status=falcon.HTTP_200)

    # Test valid uid values
    body = deepcopy(data)
    body['uid'] = "1"

    verifyRequest(client.simulate_put, url, body, exp_status=falcon.HTTP_200)

    # Test request without uid in body
    body = deepcopy(data)
    del body['uid']

    verifyRequest(client.simulate_put, url, body, exp_status=falcon.HTTP_200)


def testDeleteValidation(client):
    exp_result = {
        "title": "Validation Error",
        "description": "uid required in url."
    }

    verifyRequest(client.simulate_delete, RELAY_BASE_PATH, exp_result=exp_result,  exp_status=falcon.HTTP_400)


def testValidDelete(client):
    # TODO:
    # assert response.content == exp_result
    verifyRequest(client.simulate_delete, "{0}/1".format(RELAY_BASE_PATH), exp_status=falcon.HTTP_200)
