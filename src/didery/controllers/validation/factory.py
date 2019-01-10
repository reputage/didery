from didery.controllers.validation import validating as validation
from didery.help import helping


def historyFactory(method, mode, req, params):
    """
    Build Request Validators

    :param method: (string) Request method
    :param mode: (string) mode that didery is operating in
    :param req: falcon.Request object
    :param params: (dict) URI Template field names
    """
    req.raw = helping.parseReqBody(req)
    if method == "POST" or method == "post":
        validators = [
            validation.HistoryRequiredFieldsValidator(req, params),
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
            validation.DidHijackingValidator(req, params)
        ]
        return validation.CompositeValidator(req, params, validators)
    elif method == "PUT" or method == "put":
        validators = [
            validation.HistoryRequiredFieldsValidator(req, params),
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
        return validation.CompositeValidator(req, params, validators)
        pass
    elif method == "DELETE" or method == "delete":
        pass
