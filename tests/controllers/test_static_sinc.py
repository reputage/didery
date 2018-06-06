import falcon

try:
    import simplejson as json
except ImportError:
    import json


def testStaticSinc(client):
    # Test valid GET
    response = client.simulate_get('/')
    assert response.status == falcon.HTTP_200

    # Test valid GET
    response = client.simulate_get('/static')
    assert response.status == falcon.HTTP_200

    # Test invalid GET
    response = client.simulate_get('/invalid')

    assert json.loads(response.content)['title'] == "Missing Resource"
    assert response.status == falcon.HTTP_404
