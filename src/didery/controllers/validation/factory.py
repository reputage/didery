import didery.controllers.validation.validating as validation


def historyFactory(method, body, sigs, params):
    if method == "POST" or method == "post":
        validators = [
            validation.HistoryRequiredFieldsValidator(body, sigs, params),
            validation.SignersIsListOrArrayValidator(body, sigs, params),
            validation.IdNotEmptyValidator(body, sigs, params),
            validation.ChangedFieldNotEmptyValidator(body, sigs, params),
            validation.SignerIsIntValidator(body, sigs, params),
            validation.ChangedIsISODatetimeValidator(body, sigs, params),
            validation.NoEmptyKeysValidator(body, sigs, params),
            validation.DIDFormatValidator(body, sigs, params),
            validation.ContainsPreRotationValidator(body, sigs, params),
            validation.SignersKeysNotNoneValidator(body, sigs, params),
            validation.SignerIsZeroValidator(body, sigs, params),
            validation.InceptionSigValidator(body, sigs, params),
            validation.DidHijackingValidator(body, sigs, params)
        ]
        return validation.CompositeValidator(body, sigs, params, validators=validators)
    elif method == "PUT" or method == "put":
        pass
    elif method == "DELETE" or method == "delete":
        pass
