import falcon
import arrow
import didery.did.didering

try:
    import simplejson as json
except ImportError:
    import json

from didery.crypto import factory as cryptoFactory
from didery import didering
from didery.did.methods.dad import Dad
from didery.did.didering import Did
from didery.help import helping
from didery.db import dbing as db
from didery.models.models import BasicHistoryModel


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


class CompositeValidator(Validator):
    def __init__(self, req, params, validators):
        Validator.__init__(self, req, params)

        self.validators = validators

    def validate(self):
        for validator in self.validators:
            validator.validate()


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
        self.req.history = db.historyDB.getHistory(self.params['did'])

        if self.req.history is None:
            raise falcon.HTTPError(falcon.HTTP_404)


class OTPDeleteIdenticalSigsValidator(Validator):
    # Signatures cannot match the existing data
    # A Hacker can simply do a GET and then resend the data as a DELETE request.
    # If this happened everything would validate and the hacker would delete someones keys
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        sigs = self.req.signatures
        otp = db.otpDB.getOtpBlob(self.params['did'])

        if otp is not None:
            if otp['signatures'] == sigs:
                raise falcon.HTTPError(falcon.HTTP_401,
                                       'Authorization Error',
                                       'Request signatures match existing signatures for {}. '
                                       'Please choose different data to sign.'.format(self.params['did']))


class HistoryDoesntExistValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        did = self.body["id"]
        if db.historyDB.getHistory(did) is not None:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Resource Already Exists',
                                   'Resource with did "{}" already exists. Use PUT request.'.format(did))


class BlobExistsValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        self.req.otp = db.otpDB.getOtpBlob(self.params['did'])

        if self.req.otp is None:
            raise falcon.HTTPError(falcon.HTTP_404)


class BlobDoesntExistValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        did = self.body['id']

        if db.otpDB.getOtpBlob(did) is not None:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Resource Already Exists',
                                   'Resource with did "{}" already exists. Use PUT request.'.format(did))


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


class FieldNotEmptyValidator(Validator):
    def __init__(self, req, params, field):
        Validator.__init__(self, req, params)

        self.field = field

    def validate(self):
        if len(self.body[self.field]) == 0:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   '{} field cannot be empty.'.format(self.field))


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
        except Exception as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'ISO datetime could not be parsed.')


class ChangedLaterThanPreviousValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

        self.request_data = BasicHistoryModel(req.body)
        self.db_data = None

    def validate(self):
        self.db_data = db.historyDB.getHistory(self.params['did'])
        self.db_data.selected = self.request_data.signers[0]
        last_changed = self.db_data.parsedChanged
        new_change = self.request_data.parsedChanged

        if last_changed >= new_change:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   '"changed" field not later than previous update.')


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


class SignersNotChangedValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

        self.request_data = BasicHistoryModel(req.body)
        self.db_data = None

    def validate(self):
        self.db_data = db.historyDB.getHistory(self.params['did'])
        self.db_data.selected = self.request_data.signers[0]

        # validate that previously rotated keys are not changed with this request
        current = self.db_data.signers
        update = self.request_data.signers

        if len(update) <= len(current):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'signers field is missing keys.')

        for key, val in enumerate(current):
            if update[key] != val:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signers field missing previously verified keys.')


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
            didery.did.didering.Did(self.body['id'])
        except ValueError as ex:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   "Invalid did format. {}".format(str(ex)))


class DADValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        did = Dad(self.body['id'])

        if did.method != 'dad':
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   "blob/ endpoint only accepts dad method for DIDs.")


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


class DidMethodExistsValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

        self.didFormatValidator = DIDFormatValidator(req, params)

    def validate(self):
        self.didFormatValidator.validate()
        did_class = didery.did.didering.getDIDModel(self.body['id'])

        if did_class is None:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'Unknown DID method. Could not validate data.')


class DidHijackingValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

        self.didFormatValidator = DIDFormatValidator(req, params)

    def validate(self):
        self.didFormatValidator.validate()
        did_class = didery.did.didering.getDIDModel(self.body['id'])

        did = did_class(self.body['id'])

        if not did.match_vk(self.body['signers'][0]):
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'The first key in the signers field does not belong to this DID.')


class DidInURLValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        if 'did' not in self.params:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'DID value missing from url.')


class URLDidMatchesIdValidator(Validator):
    """
    This validator is to stop a security exploit that allows a hacker
    to place their own DID in the request body but put their targets DID in the
    request url.  Only the Scheme, Method, and Idstring are
    needed to verify the DID's match.
    """
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        # Prevent did data from being clobbered
        if Did(self.params['did']).did != Did(self.body['id']).did:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Validation Error',
                                   'Url did must match id field did.')


class CascadingValidationValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

        self.didFormatValidator = DIDFormatValidator(req, params)
        self.Hijacked = DidHijackingValidator(req, params)

    def validate(self):
        self.didFormatValidator.validate()
        did_class = didery.did.didering.getDIDModel(self.body['id'])

        if did_class is None:
            return

        self.Hijacked.validate()


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


class SignerIncrementValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

        self.request_data = BasicHistoryModel(req.body)
        self.db_data = None

    def validate(self):
        self.db_data = db.historyDB.getHistory(self.params['did'])
        self.db_data.selected = self.request_data.signers[0]

        # without these checks a hacker can skip past the validated signatures and insert their own keys
        if self.db_data.signer + 1 != self.request_data.signer:
            if self.request_data.signers[self.request_data.signer] is not None:
                raise falcon.HTTPError(falcon.HTTP_400,
                                       'Validation Error',
                                       'signer field must be one greater than previous.')
            else:  # This patches a security exploit
                sigs = self.req.signatures
                signerIsValid = SignatureValidator(
                    self.req,
                    self.params,
                    self.db_data.signers[self.db_data.signer],
                    sigs,
                    sigs.get("signer"),
                    "signer"
                )
                rotationIsValid = SignatureValidator(
                    self.req,
                    self.params,
                    self.db_data.signers[self.db_data.signer + 1],
                    sigs,
                    sigs.get("rotation"),
                    "rotation"
                )

                rotationIsValid.validate()
                signerIsValid.validate()


class RotationSigValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        sigs = self.req.signatures
        hasSignature = HasSignatureValidator(self.req, self.params, sigs)
        signerExists = SigExistsValidator(self.req, self.params, sigs, "signer")
        rotationExists = SigExistsValidator(self.req, self.params, sigs, "rotation")
        historyExists = HistoryExistsValidator(self.req, self.params)

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
        historyExists.validate()


class DeletionSigValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        HistoryExistsValidator(self.req, self.params).validate()
        history_to_delete = self.req.history
        history_to_delete.selected = self.req.body["vk"]

        index = int(history_to_delete.signer)
        vk = history_to_delete.signers[index]
        if vk is None:  # Key was revoked use old key
            vk = history_to_delete.signers[index - 1]

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


class BlobSigValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        did = Dad(self.body['id'])
        sigs = self.req.signatures
        hasSignature = HasSignatureValidator(self.req, self.params, sigs)
        sigExists = SigExistsValidator(self.req, self.params, sigs, "signer")
        sigIsValid = SignatureValidator(
            self.req,
            self.params,
            did.vk,
            sigs,
            sigs.get("signer"),
            "signer"
        )

        hasSignature.validate()
        sigExists.validate()
        sigIsValid.validate()


class DeleteBlobSigValidator(Validator):
    def __init__(self, req, params):
        Validator.__init__(self, req, params)

    def validate(self):
        BlobExistsValidator(self.req, self.params).validate()

        did = Dad(self.body['id'])
        sigs = self.req.signatures
        hasSignature = HasSignatureValidator(self.req, self.params, sigs)
        sigExists = SigExistsValidator(self.req, self.params, sigs, "signer")
        sigIsValid = SignatureValidator(
            self.req,
            self.params,
            did.vk,
            sigs,
            sigs.get("signer"),
            "signer"
        )

        hasSignature.validate()
        sigExists.validate()
        sigIsValid.validate()
