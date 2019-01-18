from didery.controllers.validation import validating as validation
from didery.help import helping


def historyFactory(mode, req, params):
    """
    Build Request Validators

    :param mode: (string) mode that didery is operating in
    :param req: falcon.Request object
    :param params: (dict) URI Template field names
    """
    req.raw = helping.parseReqBody(req)
    validators = []

    if req.method == "POST" or req.method == "post":
        validators = [
            validation.RequiredFieldsValidator(req, params, ["id", "changed", "signer", "signers"]),
            validation.HasSignatureHeaderValidator(req, params),
            validation.ParamsNotAllowedValidator(req, params),
            validation.SignersIsListOrArrayValidator(req, params),
            validation.IdNotEmptyValidator(req, params),
            validation.ChangedFieldNotEmptyValidator(req, params),
            validation.SignerIsIntValidator(req, params),
            validation.ChangedIsISODatetimeValidator(req, params),
            validation.NoEmptyKeysValidator(req, params),
            validation.DIDFormatValidator(req, params),
            validation.SignersNotEmptyValidator(req, params),
            validation.ContainsPreRotationValidator(req, params),
            validation.SignersKeysNotNoneValidator(req, params),
            validation.SignerIsZeroValidator(req, params),
            validation.InceptionSigValidator(req, params),
        ]
    elif req.method == "PUT" or req.method == "put":
        validators = [
            validation.RequiredFieldsValidator(req, params, ["id", "changed", "signer", "signers"]),
            validation.HasSignatureHeaderValidator(req, params),
            validation.SignersIsListOrArrayValidator(req, params),
            validation.IdNotEmptyValidator(req, params),
            validation.ChangedFieldNotEmptyValidator(req, params),
            validation.SignerIsIntValidator(req, params),
            validation.ChangedIsISODatetimeValidator(req, params),
            validation.NoEmptyKeysValidator(req, params),
            validation.DidInURLValidator(req, params),
            validation.MinSignersLengthValidator(req, params, 3),
            validation.SignerValueValidator(req, params),
            validation.ContainsPreRotationOrRevokedValidator(req, params),
            validation.URLDidMatchesIdValidator(req, params),
            validation.SignersNotNoneValidator(req, params),
            validation.DIDFormatValidator(req, params),
            validation.RotationSigValidator(req, params)
        ]
    elif req.method == "DELETE" or req.method == "delete":
        validators = [
            validation.RequiredFieldsValidator(req, params, ["id"]),
            validation.HasSignatureHeaderValidator(req, params),
            validation.DidInURLValidator(req, params),
            validation.IdNotEmptyValidator(req, params),
            validation.URLDidMatchesIdValidator(req, params),
            validation.DeletionSigValidator(req, params),
        ]
    else:
        # TODO add error logging here
        return None

    if mode == "race":
        if req.method == "POST" or req.method == "post":
            validators.append(validation.HistoryDoesntExistValidator(req, params))
    elif mode == "promiscuous":
        pass  # Currently no additional validators
    elif mode == "method":
        if req.method == "POST" or req.method == "post":
            validators.append(validation.DidHijackingValidator(req, params))
            validators.append(validation.HistoryDoesntExistValidator(req, params))

    return validation.CompositeValidator(req, params, validators)


def blobFactory(mode, req, params):
    """
    Build Request Validators

    :param mode: (string) mode that didery is operating in
    :param req: falcon.Request object
    :param params: (dict) URI Template field names
    """
    req.raw = helping.parseReqBody(req)
    validators = []

    if req.method == "POST" or req.method == "post":
        validators = [
            validation.RequiredFieldsValidator(req, params, ["id", "blob", "changed"]),
            validation.HasSignatureHeaderValidator(req, params),
            validation.ParamsNotAllowedValidator(req, params),
            validation.IdNotEmptyValidator(req, params),
            validation.BlobFieldNotEmptyValidator(req, params),
            validation.ChangedFieldNotEmptyValidator(req, params),
            validation.ChangedIsISODatetimeValidator(req, params),
            validation.DIDFormatValidator(req, params),
            validation.DADValidator(req, params),
            validation.BlobSigValidator(req, params),
            validation.BlobDoesntExistValidator(req, params)
        ]
    elif req.method == "PUT" or req.method == "put":
        validators = [
            validation.RequiredFieldsValidator(req, params, ["id", "blob", "changed"]),
            validation.HasSignatureHeaderValidator(req, params),
            validation.IdNotEmptyValidator(req, params),
            validation.BlobFieldNotEmptyValidator(req, params),
            validation.ChangedFieldNotEmptyValidator(req, params),
            validation.ChangedIsISODatetimeValidator(req, params),
            validation.DIDFormatValidator(req, params),
            validation.DADValidator(req, params),
            validation.DidInURLValidator(req, params),
            validation.URLDidMatchesIdValidator(req, params),
            validation.BlobSigValidator(req, params)
        ]
    elif req.method == "DELETE" or req.method == "delete":
        validators = [
            validation.RequiredFieldsValidator(req, params, ["id"]),
            validation.HasSignatureHeaderValidator(req, params),
            validation.DidInURLValidator(req, params),
            validation.IdNotEmptyValidator(req, params),
            validation.URLDidMatchesIdValidator(req, params),
            validation.DIDFormatValidator(req, params),
            validation.DeleteBlobSigValidator(req, params),
        ]
    else:
        # TODO add error logging here
        return None

    return validation.CompositeValidator(req, params, validators)
