import falcon
import arrow
try:
    import simplejson as json
except ImportError:
    import json

from ..help import helping
from .. import didering
from ..db import dbing as db


tempDB = {}


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
    req.signatures = sigs

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


def validateDelete(req, resp, resource, params):
    if 'did' not in params:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'DID value missing from url.')

    raw = helping.parseReqBody(req)
    signature = req.get_header("Signature", required=True)
    sigs = helping.parseSignatureHeader(signature)
    req.signatures = sigs
    body = req.body

    if len(sigs) == 0:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Empty Signature header.')

    signer = sigs.get('signer')  # str not bytes
    if not signer:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Signature header missing signature for "signer".')

    # Prevent did data from being clobbered
    if params['did'] != body['id']:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'Url did must match id field did.')

    otp = db.getOtpBlob(params['did'])
    req.otp = otp
    if otp is None:
        raise falcon.HTTPError(falcon.HTTP_404)

    vk = helping.extractDidParts(otp["otp_data"]['id'])

    try:
        helping.validateSignedResource(signer, raw, vk)
    except didering.ValidationError as ex:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Could not validate the request signature for signer field. {}.'.format(ex))


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
    @falcon.before(helping.parseQString)
    def on_get(self, req, resp, did=None):
        """
        Handle and respond to incoming GET request.
        :param req: Request object
        :param resp: Response object
        :param did: string
            URL parameter specifying a otp encrypted key
        """
        offset = req.offset
        limit = req.limit

        count = db.otpBlobCount()

        if did is not None:
            body = db.getOtpBlob(did)
            if body is None:
                raise falcon.HTTPError(falcon.HTTP_404)
        else:
            if offset >= count:
                resp.body = json.dumps({}, ensure_ascii=False)
                return

            body = db.getAllOtpBlobs(offset, limit)

            resp.append_header('X-Total-Count', count)

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
        result_json = req.body
        sigs = req.signatures
        did = result_json['id']

        if db.getOtpBlob(did) is not None:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Resource Already Exists',
                                   'Resource with did "{}" already exists. Use PUT request.'.format(result_json['id']))

        # TODO: review signature validation for any holes
        response_json = db.saveOtpBlob(did, result_json, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)
        resp.status = falcon.HTTP_201

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
        result_json = req.body
        sigs = req.signatures

        resource = db.getOtpBlob(did)

        if resource is None:
            raise falcon.HTTPError(falcon.HTTP_404)

        current = arrow.get(resource['otp_data']['changed'])
        update = arrow.get(result_json['changed'])
        if current >= update:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   '"changed" field not later than previous update.')

        # TODO: review signature validation for any holes
        response_json = db.saveOtpBlob(did, result_json, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)

    @falcon.before(validateDelete)
    def on_delete(self, req, resp, did):
        """
            Handle and respond to incoming PUT request.
            :param req: Request object
            :param resp: Response object
            :param did: decentralized identifier
        """
        resource = req.otp

        success = db.deleteOtpBlob(did)

        if not success:
            raise falcon.HTTPError(falcon.HTTP_500,
                                   'Deletion Error',
                                   'Error while attempting to delete the resource.')

        resp.body = json.dumps({"deleted": resource}, ensure_ascii=False)
