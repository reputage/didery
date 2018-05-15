import falcon
try:
    import simplejson as json
except ImportError:
    import json

from ..help import helping
from .. import didering


def basicValidation(req, resp, resource, params):
    """
        Do common validation tasks and prepare
        body of request for processing.
        :param req: Request object
    """
    raw = helping.parseReqBody(req)
    body = req.body

    required = ["id", "blob", "changed"]
    helping.validateRequiredFields(required, body)

    signature = req.get_header("Signature", required=True)
    sigs = helping.parseSignatureHeader(signature)

    if len(sigs) == 0:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Empty Signature header.')

    sig = sigs.get('signer')  # str not bytes
    if not sig:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Signature header missing "signer" tag and signature.')

    if body['id'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'id field cannot be empty.')

    if body['blob'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'blob field cannot be empty.')

    if body['changed'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'changed field cannot be empty.')

    try:
        didKey = helping.extractDidParts(body['id'])
    except ValueError as ex:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               "Invalid did format. {}".format(str(ex)))

    return raw, sig, didKey


def validatePost(req, resp, resource, params):
    """
    Validate incoming POST requests.
    :param req: Request object
    :param resp: Response object
    :param resource: OtpBlob object
    :param params: dict of url params
    """
    raw, sig, didKey = basicValidation(req, resp, resource, params)

    try:
        helping.validateSignedResource(sig, raw, didKey)
    except didering.ValidationError as ex:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Could not validate the request body and signature. {}.'.format(ex))


def validatePut(req, resp, resource, params):
    """
    Validate incoming PUT requests.
    :param req: Request object
    :param resp: Response object
    :param resource: OtpBlob object
    :param params: dict of url params
    """

    if 'did' not in params:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'DID value missing from url.')

    raw, sig, didKey = basicValidation(req, resp, resource, params)

    # Prevent did data from being clobbered
    if params['did'] != req.body['id']:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'Url did must match id field did.')

    try:
        helping.validateSignedResource(sig, raw, didKey)
    except didering.ValidationError as ex:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Could not validate the request body and signature. {}.'.format(ex))


class OtpBlob:
    def __init__(self, store=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store

    """
    For manual testing of the endpoint:
        http localhost:8000/blob/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=
        http localhost:8000/blob
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
                "id": did,
                "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
                "changed": "2000-01-01T00:00:00+00:00"
            }
        else:
            body = {
                "data": [{
                    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
                    "changed": "2000-01-01T00:00:00+00:00"
                },
                {
                    "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
                    "changed": "2000-01-01T00:00:00+00:00"
                }]
            }

        resp.body = json.dumps(body, ensure_ascii=False)

    """
        For manual testing of the endpoint:
        http POST localhost:8000/blob id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" blob="AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
    """
    @falcon.before(validatePost)
    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        # TODO make sure resource does NOT already exists

        resp.body = json.dumps(req.body, ensure_ascii=False)

    """
        For manual testing of the endpoint:
        http PUT localhost:8000/blob/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" blob="AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
    """
    @falcon.before(validatePut)
    def on_put(self, req, resp, did):
        """
        Handle and respond to incoming PUT request.
        :param req: Request object
        :param resp: Response object
        :param did: did string
        """
        # TODO make sure resource already exists
        # TODO make sure time in changed field is greater than existing changed field

        resp.body = json.dumps(req.body, ensure_ascii=False)
