import didery.crypto.eddsa
import didery.crypto.factory as factory

from collections import OrderedDict as ODict

from didery.help import helping as h


def testECDSAFactory():
    sigs = ODict()
    sigs["name"] = "ECDSA"

    validator = factory.signatureValidationFactory(sigs)

    assert validator is not None

    sigs["name"] = "secp256k1"

    validator = factory.signatureValidationFactory(sigs)

    assert validator is not None


def testEdDSAFactory():
    sigs = ODict()
    sigs["name"] = "EdDSA"

    validator = factory.signatureValidationFactory(sigs)

    assert validator is not None

    # test that factory returned EdDSA validator
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    signature = didery.crypto.eddsa.signResource(body, sk)

    valid = validator(signature, body, vk)

    assert valid

    sigs["name"] = "Ed25519"

    validator = factory.signatureValidationFactory(sigs)

    assert validator is not None

    # test that factory returned EdDSA validator
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    signature = didery.crypto.eddsa.signResource(body, sk)

    valid = validator(signature, body, vk)

    assert valid


def testInvalidKind():
    sigs = ODict()
    sigs["name"] = "InvalidSuperCrypto"

    validator = factory.signatureValidationFactory(sigs)

    assert validator is not None

    # test that factory returned default EdDSA validator
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    signature = didery.crypto.eddsa.signResource(body, sk)

    valid = validator(signature, body, vk)

    assert valid


def testEmptyDict():
    sigs = ODict()

    validator = factory.signatureValidationFactory(sigs)

    assert validator is not None

    # test that factory returned default EdDSA validator
    seed = b'\x92[\xcb\xf4\xee5+\xcf\xd4b*%/\xabw8\xd4d\xa2\xf8\xad\xa7U\x19,\xcfS\x12\xa6l\xba"'
    vk, sk, did, body = didery.crypto.eddsa.genDidHistory(seed, signer=0, numSigners=2)
    vk = h.bytesToStr64u(vk)
    signature = didery.crypto.eddsa.signResource(body, sk)

    valid = validator(signature, body, vk)

    assert valid
