import simplejson as json
from didery.crypto.eddsa import signResource


def verifyPublicApiRequest(reqFunc, url, body, headers=None, exp_result=None, exp_status=None):
    SK = b"\xb3\xd0\xbdL]\xcc\x08\x90\xa5\xbd\xc6\xa1 '\x82\x9c\x18\xecf\xa6x\xe2]Ux\xa5c\x0f\xe2\x86*\xa04\xe7\xfaf\x08o\x18\xd6\xc5s\xfc+\xdc \xb4\xb4\xa6G\xcfZ\x96\x01\x1e%\x0f\x96\x8c\xfa-3J<"

    body = json.dumps(body, ensure_ascii=False).encode('utf-8')

    if headers is None:
        headers = {
            "Signature": 'signer="{0}"; rotation="{1}"'.format(signResource(body, SK),
                                                               signResource(body, SK))
        }

    response = reqFunc(url, body=body, headers=headers)

    # print("status: {0},  content: {1}".format(response.status, response.content))
    if exp_result is not None:
        assert json.loads(response.content) == exp_result
    if exp_status is not None:
        assert response.status == exp_status


def verifyManagementApiRequest(reqFunc, url, body=None, exp_result=None, exp_status=None):

    response = reqFunc(url, body=json.dumps(body, ensure_ascii=False))

    # print("status: {0},  content: {1}".format(response.status, response.content))
    if exp_result is not None:
        assert json.loads(response.content) == exp_result
    if exp_status is not None:
        assert response.status == exp_status