import falcon
import arrow

try:
    import simplejson as json
except ImportError:
    import json

from ..help import helping
from ..db import dbing as db
from ..controllers.validation import factory


def validate(req, resp, resource, params):
    """
    Validate incoming POST requests.
    :param req: Request object
    :param resp: Response object
    :param resource: OtpBlob object
    :param params: dict of url params
    """
    validator = factory.blobFactory(resource.mode, req, params)
    validator.validate()


class OtpBlob:
    def __init__(self, store=None, mode=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store
        self.mode = mode

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

        count = db.otpDB.otpBlobCount()

        if did is not None:
            body = db.otpDB.getOtpBlob(did)
            if body is None:
                raise falcon.HTTPError(falcon.HTTP_404)
        else:
            if offset >= count:
                resp.body = json.dumps({}, ensure_ascii=False)
                return

            body = db.otpDB.getAllOtpBlobs(offset, limit)

            resp.append_header('X-Total-Count', count)

        resp.body = json.dumps(body, ensure_ascii=False)

    @falcon.before(validate)
    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        result_json = req.body
        sigs = req.signatures
        did = result_json['id']

        if db.otpDB.getOtpBlob(did) is not None:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Resource Already Exists',
                                   'Resource with did "{}" already exists. Use PUT request.'.format(result_json['id']))

        # TODO: review signature validation for any holes
        response_json = db.otpDB.saveOtpBlob(did, result_json, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)
        resp.status = falcon.HTTP_201

    @falcon.before(validate)
    def on_put(self, req, resp, did):
        """
        Handle and respond to incoming PUT request.
        :param req: Request object
        :param resp: Response object
        :param did: did string
        """
        result_json = req.body
        sigs = req.signatures

        resource = db.otpDB.getOtpBlob(did)

        if resource is None:
            raise falcon.HTTPError(falcon.HTTP_404)

        current = arrow.get(resource['otp_data']['changed'])
        update = arrow.get(result_json['changed'])
        if current >= update:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   '"changed" field not later than previous update.')

        # TODO: review signature validation for any holes
        response_json = db.otpDB.saveOtpBlob(did, result_json, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)

    @falcon.before(validate)
    def on_delete(self, req, resp, did):
        """
            Handle and respond to incoming PUT request.
            :param req: Request object
            :param resp: Response object
            :param did: decentralized identifier
        """
        resource = req.otp

        success = db.otpDB.deleteOtpBlob(did)

        if not success:
            raise falcon.HTTPError(falcon.HTTP_409,
                                   'Deletion Error',
                                   'Error while attempting to delete the resource.')

        resp.body = json.dumps({"deleted": resource}, ensure_ascii=False)
