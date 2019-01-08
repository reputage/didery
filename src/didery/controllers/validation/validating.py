import falcon
import arrow

try:
    import simplejson as json
except ImportError:
    import json

from didery.did.didering import Did
from didery.crypto import factory as cryptoFactory
from didery import didering


class Validator:
    def __init__(self, body, sigs, params, **kwargs):
        """
        :param body: (dict) data items
        :param sigs: (OrderedDict) signatures from request header
        """
        self.body = body
        self.sigs = sigs
        self.params = params

    def validate(self):
        """
        Validates request body, raises Falcon.HTTPError if validation fails.
        """
        pass


class HistoryRequiredFieldsValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

        self.required = ["id", "changed", "signer", "signers"]

    def validate(self):
        for req in self.required:
            if req not in self.body:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Missing Required Field',
                                       'Request must contain {} field.'.format(req))


class HasSignatureValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        if len(self.sigs) == 0:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Empty Signature header.')


class SignersIsListOrArrayValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

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
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        if self.body['id'] == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'id field cannot be empty.')


class ChangedFieldNotEmptyValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        if self.body['changed'] == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'changed field cannot be empty.')


class SignerIsIntValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        try:
            int(self.body['signer'])
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signer field must be a number.')


class ChangedIsISODatetimeValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        try:
            arrow.get(self.body["changed"])
        except arrow.parser.ParserError as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'ISO datetime could not be parsed.')


class NoEmptyKeysValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        for value in self.body['signers']:
            if value == "":
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers keys cannot be empty.')


class SignersNotNoneValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        for key, value in enumerate(self.body['signers']):
            if value is None and self.body['signer'] != key:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers keys cannot be null unless revoking a key.')


class SigExistsValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)
        sig_name = "signer"

        if "sig_name" in kwargs:
            sig_name = kwargs["sig_name"]

        self.sig = self.sigs.get(sig_name)  # str not bytes

    def validate(self):
        if not self.sig:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Signature header missing "signer" tag and signature.')


class DIDFormatValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        try:
            Did(self.body['id'])
        except ValueError as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   "Invalid did format. {}".format(str(ex)))


class ContainsPreRotationValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        if self.body['signer'] + 1 == len(self.body['signers']):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'Missing pre rotated key in "signers" field.')


class ContainsPreRotationOrRevokedValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

        self.preRotationValidator = ContainsPreRotationValidator(body, sigs, params, **kwargs)

    def validate(self):
        # Key revoked no pre-rotation necessary
        if self.body['signers'][self.body["signer"]] is None:
            return

        # Must contain pre-rotation
        self.preRotationValidator.validate()


class SignersKeysNotNoneValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        for value in self.body['signers']:
            if value is None:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers keys cannot be null on inception.')


class SignerIsZeroValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        if int(self.body['signer']) != 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signer field must equal 0 on creation of new rotation history.')


class SignerValueValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        if self.body['signer'] < 1 or self.body['signer'] >= len(self.body['signers']):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   '"signer" cannot reference the first or last key in the "signers" '
                                   'field on PUT requests.')


class SignatureValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)
        self.vk = ""
        self.cryptoValidator = cryptoFactory.signatureValidationFactory(sigs)
        self.signature = ""
        self.raw = b''

        if "vk" in kwargs:
            self.vk = kwargs["vk"]

        if "signature" in kwargs:
            self.signature = kwargs["signature"]

        if "raw" in kwargs:
            self.raw = kwargs["raw"]

    def validate(self):
        try:
            self.cryptoValidator(self.signature, self.raw.decode(), self.vk)
        except didering.ValidationError as ex:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Could not validate the request body and signature. {}.'.format(ex))


class DidHijackingValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

        self.didFormatValidator = DIDFormatValidator(body, sigs, params, **kwargs)

    def validate(self):
        self.didFormatValidator.validate()

        did = Did(self.body['id'])

        if did.pubkey != self.body['signers'][0]:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'The DIDs key must match the first key in the signers field.')


class DidInURLValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        if 'did' not in self.params:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'DID value missing from url.')


class URLDidMatchesIdValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

    def validate(self):
        # Prevent did data from being clobbered
        if self.params['did'] != self.body['id']:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'Url did must match id field did.')


class InceptionSigValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

        self.hasSignature = HasSignatureValidator(self.body, self.sigs, self.params, **kwargs)
        self.sigExists = SigExistsValidator(self.body, self.sigs, self.params, sig_name="signer")
        self.sigIsValid = SignatureValidator(
            body,
            sigs,
            params,
            vk=body["signers"][int(body["signer"])],
            signature=sigs.get("signer"),
            raw=json.dumps(body).encode()
        )

    def validate(self):
        self.hasSignature.validate()
        self.sigExists.validate()
        self.sigIsValid.validate()


class RotationSigValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

        self.hasSignature = HasSignatureValidator(self.body, self.sigs, self.params, **kwargs)
        self.sigExists = SigExistsValidator(self.body, self.sigs, self.params, sig_name="rotation")
        self.signerIsValid = SignatureValidator(
            body,
            sigs,
            params,
            vk=body["signers"][int(body["signer"])-1],
            signature=sigs.get("signer"),
            raw=json.dumps(body).encode()
        )
        self.rotationIsValid = SignatureValidator(
            body,
            sigs,
            params,
            vk=body["signers"][int(body["signer"])],
            signature=sigs.get("rotation"),
            raw=json.dumps(body).encode()
        )

    def validate(self):
        self.hasSignature.validate()
        self.sigExists.validate()
        self.signerIsValid.validate()
        self.rotationIsValid.validate()


class CompositeValidator(Validator):
    def __init__(self, body, sigs, params, **kwargs):
        Validator.__init__(self, body, sigs, params, **kwargs)

        if "validators" in kwargs:
            self.validators = kwargs["validators"]

    def validate(self):
        for validator in self.validators:
            validator.validate()


# TODO remove **kwargs and other vars from init function.
# TODO the init functions don't need to be uniform
