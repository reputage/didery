import falcon

try:
    import simplejson as json
except ImportError:
    import json

from didery.routing import *


def testGetAllInvalidQueryString(client):
    # Test that query params have values
    response = client.simulate_get(ERRORS_BASE_PATH, query_string="offset&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string missing value(s)."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(ERRORS_BASE_PATH, query_string="offset=10&limit")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string missing value(s)."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testGetAllInvalidQueryValue(client):
    # Test that query params values are ints
    response = client.simulate_get(ERRORS_BASE_PATH, query_string="offset=a&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(ERRORS_BASE_PATH, query_string="offset=10&limit=d")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testGetAllEmptyQueryValue(client):
    response = client.simulate_get(ERRORS_BASE_PATH, query_string="offset=10&limit=")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(ERRORS_BASE_PATH, query_string="offset=&limit=10")

    exp_result = {
        "title": "Malformed Query String",
        "description": "url query string value must be a number."
    }

    assert response.status == falcon.HTTP_400
    assert json.loads(response.content) == exp_result


def testValidGetAll(client):
    response = client.simulate_get(ERRORS_BASE_PATH)

    exp_result = {
        "data": [
            {
                "title": "Invalid Signature.",
                "msg": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= had an invalid rotation signature.",
                "time": "2000-01-01T00:00:00+00:00"
            },
            {
                "title": "Relay Unreachable.",
                "msg": "Could not establish a connection with relay servers.",
                "time": "2000-01-01T11:00:00+00:00"
            }
        ]
    }

    # TODO remove this when errors endpoint is finished.
    exp_result = {"data": []}

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result

    response = client.simulate_get(ERRORS_BASE_PATH, query_string="offset=100&limit=10")

    exp_result = {"data": []}

    assert response.status == falcon.HTTP_200
    assert json.loads(response.content) == exp_result
