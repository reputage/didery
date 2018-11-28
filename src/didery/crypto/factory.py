import didery.crypto.ecdsa as ecdsa
import didery.crypto.eddsa as eddsa


def signatureValidationFactory(sigs):
    """
    Identifies the validation function necessary. Defaults to EdDSA.
    :return: a validation function
    """
    kind = sigs.get("name")

    if kind == "ECDSA" or kind == "secp256k1":
        return ecdsa.validateSignedResource
    else:  # Default to EdDSA
        return eddsa.validateSignedResource

