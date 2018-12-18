import ecdsa.keys as keys
import ecdsa.curves as curves
import pytest

try:
    import simplejson as json
except ImportError:
    import json

from didery.crypto import ecdsa
from didery.help.helping import str64uToBytes, bytesToStr64u
from didery import didering


def testGenerateByteKeys():
    vk, sk = ecdsa.generateByteKeys()
    assert len(vk) == 64
    assert len(sk) == 32

    # check that keys are byte strings
    assert str(vk) != vk
    assert str(sk) != sk


def testGenerate64uKeys():
    vk, sk = ecdsa.generate64uKeys()

    assert len(vk) == 88
    assert len(sk) == 44

    # check that keys are strings
    assert str(vk) == vk
    assert str(sk) == sk


def testSignResource():
    resource = "message"
    vk, sk = ecdsa.generateByteKeys()

    signature = ecdsa.signResource(resource, sk)

    assert str(signature) == signature
    assert len(signature) == 88
    assert len(str64uToBytes(signature)) == 64


def testSignResource64u():
    resource = "message"
    vk, sk = ecdsa.generate64uKeys()

    signature = ecdsa.signResource64u(resource, sk)

    assert str(signature) == signature
    assert len(signature) == 88
    assert len(str64uToBytes(signature)) == 64


def testVerify():
    resource = "message"
    vk, sk = ecdsa.generateByteKeys()
    vk = keys.VerifyingKey.from_string(vk, curves.SECP256k1)
    signature = str64uToBytes(ecdsa.signResource(resource, sk))

    assert ecdsa.verify(signature, resource, vk)


def testVerify64u():
    resource = "message"
    vk, sk = ecdsa.generateByteKeys()
    vk = bytesToStr64u(vk)
    signature = ecdsa.signResource(resource, sk)

    assert ecdsa.verify64u(signature, resource, vk)


def testValidateSignedResourceInvalidJson():
    resource = "message"
    vk, sk = ecdsa.generate64uKeys()
    signature = ecdsa.signResource64u(resource, sk)

    with pytest.raises(didering.ValidationError) as ex:
        ecdsa.validateSignedResource(signature, resource, vk)

        assert ex.value == "Invalid JSON"


def testValidateSignedResourceInvalidSignature():
    resource = '{"1":"test"}'
    vk, sk = ecdsa.generate64uKeys()
    signature = ecdsa.signResource64u(resource, sk)

    with pytest.raises(didering.ValidationError) as ex:
        ecdsa.validateSignedResource(signature, '{"1":"tes"}', vk)

        assert ex.value == "Unverifiable signature"


def testValidateSignedResource():
    resource = '{"1":"test"}'
    vk, sk = ecdsa.generate64uKeys()
    signature = ecdsa.signResource64u(resource, sk)

    # returns parsed json if signature is valid
    parsedResource = ecdsa.validateSignedResource(signature, resource, vk)

    assert parsedResource == json.loads(resource)


def testGenDidHistoryNumSigners():
    numSigners = 2
    vk, sk, did, body = ecdsa.genDidHistory(numSigners=numSigners)

    assert len(json.loads(body.decode())['signers']) == numSigners


def testGenDidHistorySigner():
    signer = 1
    vk, sk, did, body = ecdsa.genDidHistory(signer=signer)

    assert json.loads(body.decode())['signer'] == signer


def testGenDidHistoryChanged():
    changed = "2018-12-01T00:00:00+00:00"
    vk, sk, did, body = ecdsa.genDidHistory(changed=changed)

    assert json.loads(body.decode())['changed'] == changed

