import didery.controllers.validation.validating as validation


def historyFactory(method, req, params):
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
            validation.ContainsPreRotationValidator(req, params),
            validation.SignersKeysNotNoneValidator(req, params),
            validation.SignerIsZeroValidator(req, params),
            validation.InceptionSigValidator(req, params),
            validation.DidHijackingValidator(req, params)
        ]
        return validation.CompositeValidator(req, params, validators)
    elif method == "PUT" or method == "put":
        pass
    elif method == "DELETE" or method == "delete":
        pass
