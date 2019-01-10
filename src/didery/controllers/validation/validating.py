import falcon
import arrow

try:
    import simplejson as json
except ImportError:
    import json

from didery.did.didering import Did
from didery.crypto import factory as cryptoFactory
from didery import didering
from didery.help import helping
from didery.db import dbing as db


class Validator:
    def __init__(self, req, params):
        """
        :param req: (falcon.Request) Request object
        :param params: (dict) URI Template field names
        """
        self.req = req
        self.raw = req.raw
        self.body = req.body
        self.params = params

    def validate(self):
        """
        Validates request body, raises Falcon.HTTPError if validation fails.
        """
        pass


class RequiredFieldsValidator(Validator):
    def __init__(self, req, params, required):
        Validator.__init__(self, req, params)

        self.requiredFields = required

    def validate(self):
        for required in self.requiredFields:
            if required not in self.body:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Missing Required Field',
                                       'Request must contain {} field.'.format(required))


class HasSignatureHeaderValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)
    
    def validate(self):
        header = self.req.get_header("Signature", required=True)
        self.req.signatures = helping.parseSignatureHeader(header)


class ParamsNotAllowedValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        # server crashes without this if someone adds anything after /history on POST requests
        if self.params:
            raise falcon.HTTPError(falcon.HTTP_404)


class HasSignatureValidator(Validator):
    def __init__(self, req, params, sigs):
        Validator.__init__(self, req, params)

        self.sigs = sigs

    def validate(self):
        if len(self.sigs) == 0:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Empty Signature header.')


class HistoryExistsValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        self.req.history = db.getHistory(self.params['did'])

        if self.req.history is None:
            raise falcon.HTTPError(falcon.HTTP_404)


class SignersIsListOrArrayValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

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
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        if self.body['id'] == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'id field cannot be empty.')


class ChangedFieldNotEmptyValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        if self.body['changed'] == "":
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'changed field cannot be empty.')


class SignerIsIntValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        try:
            int(self.body['signer'])
        except ValueError:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signer field must be a number.')


class ChangedIsISODatetimeValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        try:
            arrow.get(self.body["changed"])
        except arrow.parser.ParserError as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'ISO datetime could not be parsed.')


class NoEmptyKeysValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        for value in self.body['signers']:
            if value == "":
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers keys cannot be empty.')


class SignersNotNoneValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        for key, value in enumerate(self.body['signers']):
            if value is None and self.body['signer'] != key:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers keys cannot be null unless revoking a key.')


class SigExistsValidator(Validator):
    def __init__(self, req, params, sigs, sig_name):
        Validator.__init__(self, req, params)

        self.sig_name = sig_name
        self.sig = sigs.get(sig_name)  # str not bytes

    def validate(self):
        if not self.sig:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Signature header missing signature for "' + self.sig_name + '".')


class DIDFormatValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        try:
            Did(self.body['id'])
        except ValueError as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   "Invalid did format. {}".format(str(ex)))


class MinSignersLengthValidator(Validator):
    def __init__(self, req, params, minLength):
        Validator.__init__(self, req, params)
        self.minLength = minLength

    def validate(self):
        if len(self.body['signers']) < self.minLength:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers field missing keys.')


class ContainsPreRotationValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        if self.body['signer'] + 1 == len(self.body['signers']):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'Missing pre rotated key in "signers" field.')


class ContainsPreRotationOrRevokedValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

        self.preRotationValidator = ContainsPreRotationValidator(req, params)

    def validate(self):
        # Key revoked no pre-rotation necessary
        if self.body['signers'][self.body["signer"]] is None:
            return

        # Must contain pre-rotation
        self.preRotationValidator.validate()


class SignersKeysNotNoneValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        for value in self.body['signers']:
            if value is None:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers keys cannot be null on inception.')


class SignersNotEmptyValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        if len(self.body["signers"]) == 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers field cannot be empty.')


class SignerIsZeroValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        if int(self.body['signer']) != 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signer field must equal 0 on creation of new rotation history.')


class SignerValueValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        if self.body['signer'] < 1 or self.body['signer'] >= len(self.body['signers']):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   '"signer" cannot reference the first or last key in the "signers" '
                                   'field on PUT requests.')


class SignatureValidator(Validator):
    def __init__(self, req, params, vk, sigs, signature, sigName):
        Validator.__init__(self, req, params)
        self.vk = vk
        self.cryptoValidator = cryptoFactory.signatureValidationFactory(sigs)
        self.signature = signature
        self.sigName = sigName

    def validate(self):
        try:
            self.cryptoValidator(self.signature, self.raw.decode(), self.vk)
        except didering.ValidationError as ex:
            raise falcon.HTTPError(falcon.HTTP_401,
                                   'Authorization Error',
                                   'Could not validate the request signature for ' + self.sigName + ' field. {}.'.format(ex))


class DidHijackingValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

        self.didFormatValidator = DIDFormatValidator(req, params)

    def validate(self):
        self.didFormatValidator.validate()

        did = Did(self.body['id'])

        if did.pubkey != self.body['signers'][0]:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'The DIDs key must match the first key in the signers field.')


class DidInURLValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        if 'did' not in self.params:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'DID value missing from url.')


class URLDidMatchesIdValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        # Prevent did data from being clobbered
        if self.params['did'] != self.body['id']:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'Url did must match id field did.')


class InceptionSigValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        sigs = self.req.signatures
        hasSignature = HasSignatureValidator(self.req, self.params, sigs)
        sigExists = SigExistsValidator(self.req, self.params, sigs, "signer")
        sigIsValid = SignatureValidator(
            self.req,
            self.params,
            self.body["signers"][int(self.body["signer"])],
            sigs,
            sigs.get("signer"),
            "signer"
        )

        hasSignature.validate()
        sigExists.validate()
        sigIsValid.validate()


class RotationSigValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        sigs = self.req.signatures
        hasSignature = HasSignatureValidator(self.req, self.params, sigs)
        signerExists = SigExistsValidator(self.req, self.params, sigs, "signer")
        rotationExists = SigExistsValidator(self.req, self.params, sigs, "rotation")

        if self.body["signers"][int(self.body["signer"])] is None:
            index = self.body['signer'] - 1
        else:
            index = self.body['signer']

        signerIsValid = SignatureValidator(
            self.req,
            self.params,
            self.body["signers"][index - 1],
            sigs,
            sigs.get("signer"),
            "signer"
        )
        rotationIsValid = SignatureValidator(
            self.req,
            self.params,
            self.body["signers"][index],
            sigs,
            sigs.get("rotation"),
            "rotation"
        )

        hasSignature.validate()
        signerExists.validate()
        rotationExists.validate()
        rotationIsValid.validate()
        signerIsValid.validate()


class DeletionSigValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        HistoryExistsValidator(self.req, self.params).validate()

        index = int(self.req.history['history']['signer'])
        vk = self.req.history['history']['signers'][index]
        if vk is None:  # Key was revoked use old key
            vk = self.req.history['history']['signers'][index - 1]

        sigs = self.req.signatures

        hasSignature = HasSignatureValidator(self.req, self.params, sigs)
        sigExists = SigExistsValidator(self.req, self.params, sigs, "signer")
        sigIsValid = SignatureValidator(
            self.req,
            self.params,
            vk,
            sigs,
            sigs.get("signer"),
            "signer"
        )

        hasSignature.validate()
        sigExists.validate()
        sigIsValid.validate()


class CompositeValidator(Validator):
    def __init__(self, req, params, validators):
        Validator.__init__(self, req, params)

        self.validators = validators

    def validate(self):
        for validator in self.validators:
            validator.validate()
