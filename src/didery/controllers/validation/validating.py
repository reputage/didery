import falcon
import arrow

try:
    import simplejson as json
except ImportError:
    import json

from collections import OrderedDict as ODict

from didery.did.didering import Did
from didery.crypto import factory as cryptoFactory
from didery import didering


class Validator:
    def __init__(self, body, sigs, **kwargs):
        """
        :param body: (dict) data items
        :param sigs: (OrderedDict) signatures from request header
        """
        self.body = body
        self.sigs = sigs

    def validate(self):
        """
        Validates request body, raises Falcon.HTTPError if validation fails.
        """
        pass


class HasSignatureValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        if len(self.sigs) == 0:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Empty Signature header.')


class SignersIsListOrArrayValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        try:
            if not isinstance(self.body['signers'], list):
                self.body['signers'] = json.loads(
                    self.body['signers'].replace("'", '"')
                )
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers field must be a list or array.')


class IdNotEmptyValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        if self.body['id'] == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'id field cannot be empty.')


class ChangedFieldNotEmptyValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        if self.body['changed'] == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'changed field cannot be empty.')


class SignerIsIntValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        try:
            int(self.body['signer'])
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signer field must be a number.')


class ChangedIsISODatetimeValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        try:
            arrow.get(self.body["changed"])
        except arrow.parser.ParserError as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'ISO datetime could not be parsed.')


class NoEmptyKeysValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        for value in self.body['signers']:
            if value == "":
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers keys cannot be empty.')


class SignerSigExistsValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        sig = self.sigs.get('signer')  # str not bytes
        if not sig:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Signature header missing "signer" tag and signature.')


class DIDFormatValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        try:
            Did(self.body['id'])
        except ValueError as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   "Invalid did format. {}".format(str(ex)))


class SignersLengthGreaterThanValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)
        self.num_signers = 2

        if "num_signers" in kwargs:
            self.num_signers = kwargs["num_signers"]

    def validate(self):
        if len(self.body['signers']) < self.num_signers:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers field must contain at least the current public key and its first pre-rotation.')


class SignersKeysNotNone(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        for value in self.body['signers']:
            if value is None:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers keys cannot be null on inception.')


class SingerIsZeroValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)

    def validate(self):
        if int(self.body['signer']) != 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signer field must equal 0 on creation of new rotation history.')


class SignatureValidator(Validator):
    def __init__(self, body, sigs, **kwargs):
        Validator.__init__(self, body, sigs, **kwargs)
        self.index = 0
        self.cryptoValidator = cryptoFactory.signatureValidationFactory(sigs)
        self.signature = ""
        self.raw = b''

        if "index" in kwargs:
            self.index = kwargs["index"]

        if "signature" in kwargs:
            self.signature = kwargs["signature"]

        if "raw" in kwargs:
            self.raw = kwargs["raw"]

    def validate(self):
        try:
            self.cryptoValidator(self.signature, self.raw.decode(), self.body['signers'][self.index])
        except didering.ValidationError as ex:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Could not validate the request body and signature. {}.'.format(ex))
