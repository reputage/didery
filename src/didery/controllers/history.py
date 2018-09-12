import falcon
import arrow
import time
try:
    import simplejson as json
except ImportError:
    import json

from collections import OrderedDict
from ..help import helping
from .. import didering
from ..db import dbing as db


def basicValidation(req, resp, resource, params):
    raw = helping.parseReqBody(req)
    body = req.body

    required = ["id", "changed", "signer", "signers"]
    helping.validateRequiredFields(required, body)

    signature = req.get_header("Signature", required=True)
    sigs = helping.parseSignatureHeader(signature)
    req.signatures = sigs

    if len(sigs) == 0:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Empty Signature header.')

    try:
        if not isinstance(body['signers'], list):
            body['signers'] = json.loads(
                body['signers'].replace("'", '"')
            )
    except ValueError:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'signers field must be a list or array.')

    if body['id'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'id field cannot be empty.')

    if body['changed'] == "":
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'changed field cannot be empty.')

    try:
        req.body['signer'] = int(body['signer'])
    except ValueError:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'signer field must be a number.')

    try:
        dt = arrow.get(body["changed"])
    except arrow.parser.ParserError as ex:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'ISO datetime could not be parsed.')

    for value in body['signers']:
        if value == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers keys cannot be empty.')

    return raw, sigs


def validatePost(req, resp, resource, params):
    """
    Validate incoming POST request and prepare
    body of request for processing.
    :param req: Request object
    """
    # server crashes without this if someone adds anything after /history
    if params:
        raise falcon.HTTPError(falcon.HTTP_404)

    raw, sigs = basicValidation(req, resp, resource, params)
    body = req.body

    sig = sigs.get('signer')  # str not bytes
    if not sig:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Signature header missing "signer" tag and signature.')

    try:
        didkey = helping.extractDidParts(body['id'])
    except ValueError as ex:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               "Invalid did format. {}".format(str(ex)))

    if len(body['signers']) < 2:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'signers field must contain at least the current public key and its first pre-rotation.')

    # If it is decided that revocation on inception is allowed we can remove this check
    for value in body['signers']:
        if value is None:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers keys cannot be null on inception.')

    if body['signer'] != 0:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'signer field must equal 0 on creation of new rotation history.')

    index = body['signer']
    try:
        helping.validateSignedResource(sig, raw, body['signers'][index])
    except didering.ValidationError as ex:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Could not validate the request body and signature. {}.'.format(ex))

    # Prevent bad actors from trying to commandeer a DID before its owner posts it
    if didkey != body['signers'][0]:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'The DIDs key must match the first key in the signers field.')


def validatePut(req, resp, resource, params):
    if 'did' not in params:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'DID value missing from url.')

    raw, sigs = basicValidation(req, resp, resource, params)
    body = req.body

    signer = sigs.get('signer')  # str not bytes
    if not signer:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Signature header missing signature for "signer".')

    rotation = sigs.get('rotation')  # str not bytes
    if not rotation:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Signature header missing signature for "rotation".')

    if len(body['signers']) < 3:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'PUT endpoint is for rotation events. Must contain at least the original key, a '
                               'current signing key, and a pre-rotated key.')

    if body['signer'] < 1 or body['signer'] >= len(body['signers']):
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               '"signer" cannot reference the first or last key in the "signers" '
                               'field on PUT requests.')

    if body['signer'] + 1 == len(body['signers']) and body['signers'][body["signer"]] is not None:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'Missing pre rotated key in the signers field.')

    # Prevent did data from being clobbered
    if params['did'] != body['id']:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Validation Error',
                               'Url did must match id field did.')

    for key, value in enumerate(body['signers']):
        if value is None and body['signer'] != key:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers keys cannot be null unless revoking a key.')

    if body["signers"][body["signer"]] is None:
        index = body['signer'] - 1
    else:
        index = body['signer']

    try:
        helping.validateSignedResource(rotation, raw, body['signers'][index])
    except didering.ValidationError as ex:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Could not validate the request signature for rotation field. {}.'.format(ex))

    try:
        helping.validateSignedResource(signer, raw, body['signers'][index-1])
    except didering.ValidationError as ex:
        raise falcon.HTTPError(falcon.HTTP_401,
                               'Authorization Error',
                               'Could not validate the request signature for signer field. {}.'.format(ex))


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

    history = db.getHistory(params['did'])
    req.history = history
    if history is None:
        raise falcon.HTTPError(falcon.HTTP_404)

    index = history['history']['signer']
    vk = history['history']['signers'][index]

    if vk is not None:
        try:
            helping.validateSignedResource(signer, raw, vk)
        except didering.ValidationError as ex:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Could not validate the request signature for signer field. {}.'.format(ex))

    else:
        try:
            helping.validateSignedResource(signer, raw, history['history']['signers'][index - 1])
        except didering.ValidationError as ex:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Could not validate the request signature for signer field. {}.'.format(ex))


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
    @falcon.before(helping.parseQString)
    def on_get(self, req, resp, did=None):
        """
        Handle and respond to incoming GET request.
        :param req: Request object
        :param resp: Response object
        :param did: string
            URL parameter specifying a rotation history
        """
        offset = req.offset
        limit = req.limit

        count = db.historyCount()

        if did is not None:
            body = db.getHistory(did)
            if body is None:
                raise falcon.HTTPError(falcon.HTTP_404)
        else:
            if offset >= count:
                resp.body = json.dumps({}, ensure_ascii=False)
                return

            body = db.getAllHistories(offset, limit)

            resp.append_header('X-Total-Count', count)

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
        sigs = req.signatures
        did = result_json['id']

        if db.getHistory(did) is not None:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Resource Already Exists',
                                   'Resource with did "{}" already exists. Use PUT request.'.format(result_json['id']))

        # TODO: review signature validation for any holes
        response_json = db.saveHistory(did, result_json, sigs)
        db.saveEvent(did, result_json, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)
        resp.status = falcon.HTTP_201

    """
    For manual testing of the endpoint:
        http PUT localhost:8000/history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" changed="2000-01-01T00:00:00+00:00" signer=2 signers="['Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=', 'Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=', 'dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=', '3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=']"
    """
    @falcon.before(validatePut)
    def on_put(self, req, resp, did):
        """
            Handle and respond to incoming PUT request.
            :param req: Request object
            :param resp: Response object
            :param did: decentralized identifier
        """
        result_json = req.body
        sigs = req.signatures

        resource = db.getHistory(did)

        if resource is None:
            raise falcon.HTTPError(falcon.HTTP_404)

        # make sure time in changed field is greater than existing changed field
        last_changed = arrow.get(resource['history']['changed'])
        new_change = arrow.get(result_json['changed'])

        if last_changed >= new_change:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   '"changed" field not later than previous update.')

        # validate that previously rotated keys are not changed with this request
        current = resource['history']['signers']
        update = result_json['signers']

        if len(update) <= len(current):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers field is missing keys.')

        for key, val in enumerate(current):
            if update[key] != val:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers field missing previously verified keys.')

        # without these checks a hacker can skip past the validated signatures and insert their own keys
        if resource['history']['signer'] + 1 != result_json['signer']:
            if result_json['signers'][result_json['signer']] is not None:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signer field must be one greater than previous.')

        # TODO: review signature validation for any holes
        response_json = db.saveHistory(did, result_json, sigs)
        db.saveEvent(did, result_json, sigs)

        resp.body = json.dumps(response_json, ensure_ascii=False)

    @falcon.before(validateDelete)
    def on_delete(self, req, resp, did):
        """
            Handle and respond to incoming PUT request.
            :param req: Request object
            :param resp: Response object
            :param did: decentralized identifier
        """
        resource = req.history

        success = db.deleteHistory(did)
        db.deleteEvent(did)

        if not success:
            raise falcon.HTTPError(falcon.HTTP_500,
                                   'Deletion Error',
                                   'Error while attempting to delete the resource.')

        resp.body = json.dumps({"deleted": resource}, ensure_ascii=False)


class HistoryStream:
    def __init__(self, store=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store
        self.id = 0
        self.history = None

    def historyGenerator(self, did=None):
        if did is None:
            count = db.historyCount()
            if self.history == count:
                time.sleep(2)
            else:
                self.history = count
                history = db.getAllHistories(limit=self.history)
                temp = []
                for entry in history['data']:
                    temp.append(json.loads(entry.decode('utf-8')))

                history = {"data": temp}
                yield bytes("\nid:" + str(self.id) + "\nevent:message\ndata:" + str(history) + "\n\n", "ascii")
                self.id += 1
                time.sleep(2)

        else:
            value = db.getHistory(did)
            if value is None:
                raise falcon.HTTPError(falcon.HTTP_404)

            if self.history == value:
                time.sleep(2)
            else:
                self.history = value
                print(self.history)
                yield bytes("\nid:" + str(self.id) + "\nevent:message\ndata:" + str(self.history) + "\n\n", "ascii")
                self.id += 1
                time.sleep(2)

    def on_get(self, req, resp, did=None):
        resp.status = falcon.HTTP_200
        resp.content_type = "text/event-stream"
        resp.stream = self.historyGenerator(did)
