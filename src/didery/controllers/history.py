import falcon
try:
    import simplejson as json
except ImportError:
    import json

from ..help import helping
from .. import didering


def validatePost(req, resp, resource, params):
    """
    Validate incoming POST request and prepare
    body of request for processing.
    :param req: Request object
    """

    raw = helping.parseReqBody(req)
    body = req.body

    required = ["id", "changed", "signer", "signers"]
    helping.validateRequiredFields(required, body)

    signature = req.get_header("Signature", required=True)
    sigs = helping.parseSignatureHeader(signature)

    if len(sigs) == 0:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Validation Error',
                               'Invalid or missing Signature header.')

    sig = sigs.get('signer')  # str not bytes
    if not sig:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Validation Error',
                               'Signature header missing signature for "signer".')

    sig = sigs.get('rotation')  # str not bytes
    if not sig:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Validation Error',
                               'Signature header missing signature for "rotation".')

    try:
        if not isinstance(body['signers'], list):
            body['signers'] = json.loads(
                body['signers'].replace("'", '"')
            )
    except ValueError:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'signers field must be a list or array.')

    if body['id'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'id field cannot be empty.')

    if body['changed'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'changed field cannot be empty.')

    if len(body['signers']) < 2:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'signers field must contain at least the current public key and its first pre-rotation.')

    try:
        int(body['signer'])
    except ValueError:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'signer field must be a number.')

    if int(body['signer']) < 0 or int(body['signer']) >= len(body['signers']):
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'signer field must be between 0 and size of signers field.')

    if int(body['signer']) + 1 == len(body['signers']):
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Field',
                               'Missing pre rotated key in the signers field.')

    index = int(body['signer'])
    try:
        helping.validateSignedResource(sig, raw, body['signers'][index])
    except didering.ValidationError as ex:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Validation Error',
                               'Could not validate the request body. {}'.format(ex))

    try:
        helping.validateSignedResource(sig, raw, body['signers'][index+1])
    except didering.ValidationError as ex:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Validation Error',
                               'Could not validate the request body. {}'.format(ex))


class History:
    def __init__(self, store=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store

    """
    For manual testing of the endpoint:
        http localhost:8000/history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=
        http localhost:8000/history
    """
    def on_get(self, req, resp, did=None):
        """
        Handle and respond to incoming GET request.
        :param req: Request object
        :param resp: Response object
        :param did: string
            URL parameter specifying a rotation history
        """
        if did is not None:
            body = {
                "history":
                {
                    "id": did,
                    "changed" : "2000-01-01T00:00:00+00:00",
                    "signer": 2,
                    "signers":
                    [
                        "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                        "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
                    ]
                },
                "signatures":
                [
                    "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
                ]
            }
        else:
            body = {
                "data": [{
                    "history":
                    {
                        "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                        "changed" : "2000-01-01T00:00:00+00:00",
                        "signer": 2,
                        "signers":
                        [
                            "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                            "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                            "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                            "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
                        ]
                    },
                    "signatures":
                    [
                        "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
                        "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
                    ]
                }, {
                    "history":
                    {
                        "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                        "changed" : "2000-01-01T00:00:00+00:00",
                        "signer": 1,
                        "signers":
                        [
                            "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                            "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                            "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
                        ]
                    },
                    "signatures":
                    [
                        "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw==",
                        "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
                    ]
                }]
            }

        resp.body = json.dumps(body, ensure_ascii=False)

    """
    For manual testing of the endpoint:
        http POST localhost:8000/history id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" changed="2000-01-01T00:00:00+00:00" signer=2 signers="['Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=', 'Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=', 'dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=', '3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=']"
    """
    @falcon.before(validatePost)
    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        result_json = req.body

        response_json = {
            "history": result_json,
            "signatures": [
                "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
                "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
            ]
        }

        resp.body = json.dumps(response_json, ensure_ascii=False)
