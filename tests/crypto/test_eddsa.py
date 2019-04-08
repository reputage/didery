import pytest

try:
    import simplejson as json
except ImportError:
    import json

from didery.crypto import eddsa
from didery.help.helping import str64uToBytes
from didery import didering


def testGenerateByteKeys():
    vk, sk = eddsa.generateByteKeys()
    assert len(vk) == 32
    assert len(sk) == 64

    # check that keys are byte strings
    assert str(vk) != vk
    assert str(sk) != sk


def testGenerate64uKeys():
    vk, sk = eddsa.generate64uKeys()

    assert len(vk) == 44
    assert len(sk) == 88

    # check that keys are strings
    assert str(vk) == vk
    assert str(sk) == sk


def testSignResource():
    resource = b"message"
    vk, sk = eddsa.generateByteKeys()

    signature = eddsa.signResource(resource, sk)

    assert str(signature) == signature
    assert len(signature) == 88
    assert len(str64uToBytes(signature)) == 64


def testSignResource64u():
    resource = "message"
    vk, sk = eddsa.generate64uKeys()

    signature = eddsa.signResource64u(resource, sk)

    assert str(signature) == signature
    assert len(signature) == 88
    assert len(str64uToBytes(signature)) == 64


def testVerify():
    resource = b"message"
    vk, sk = eddsa.generateByteKeys()
    signature = str64uToBytes(eddsa.signResource(resource, sk))

    assert eddsa.verify(signature, resource, vk)


def testVerify64u():
    resource = "message"
    vk, sk = eddsa.generate64uKeys()
    signature = eddsa.signResource64u(resource, sk)

    assert eddsa.verify64u(signature, resource, vk)


def testValidateSignedResourceInvalidJson():
    resource = "message"
    vk, sk = eddsa.generate64uKeys()
    signature = eddsa.signResource64u(resource, sk)

    with pytest.raises(didering.ValidationError) as ex:
        eddsa.validateSignedResource(signature, resource, vk)

        assert ex.value == "Invalid JSON"


def testValidateSignedResourceInvalidSignature():
    resource = '{"1":"test"}'
    vk, sk = eddsa.generate64uKeys()
    signature = eddsa.signResource64u(resource, sk)

    with pytest.raises(didering.ValidationError) as ex:
        eddsa.validateSignedResource(signature, b'{"1":"tes"}', vk)

        assert ex.value == "Unverifiable signature"


def testValidateSignedResource():
    resource = '{"1":"test"}'
    vk, sk = eddsa.generate64uKeys()
    signature = eddsa.signResource64u(resource, sk)

    # returns parsed json if signature is valid
    parsedResource = eddsa.validateSignedResource(signature, resource, vk)

    assert parsedResource == json.loads(resource)


def testGenDidHistoryNumSigners():
    numSigners = 2
    vk, sk, did, body = eddsa.genDidHistory(numSigners=numSigners)

    assert len(json.loads(body.decode())['signers']) == numSigners


def testGenDidHistorySigner():
    signer = 1
    vk, sk, did, body = eddsa.genDidHistory(signer=signer)

    assert json.loads(body.decode())['signer'] == signer


def testGenDidHistoryChanged():
    changed = "2018-12-01T00:00:00+00:00"
    vk, sk, did, body = eddsa.genDidHistory(changed=changed)

    assert json.loads(body.decode())['changed'] == changed

