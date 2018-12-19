from collections import OrderedDict as ODict

import libnacl
try:
    import simplejson as json
except ImportError:
    import json

from didery import didering
from didery.help.helping import str64uToBytes, bytesToStr64u, makeDid


def verify(sig, msg, vk):
    """
    Returns True if signature sig of message msg is verified with
    verification key vk Otherwise False

    :param sig: utf-8 encoded byte string signature
    :param msg: utf-8 encoded byte string message
    :param vk: utf-8 encoded byte string message
    :return: boolean True if valid False otherwise
    """
    try:
        result = libnacl.crypto_sign_open(sig + msg, vk)
    except Exception as ex:
        return False
    return True if result else False


def verify64u(signature, message, verkey):
    """
    Returns True if signature is valid for message with respect to verification
    key verkey

    :param signature: base64 url-file safe encoded signature string
    :param message: json encoded unicode string of resource record
    :param verkey: base64 url-file safe encoded public key string
    :return: boolean True if valid False otherwise
    """
    sig = str64uToBytes(signature)
    vk = str64uToBytes(verkey)
    # msg = message.encode("utf-8")
    return verify(sig, message.encode(), vk)


def validateSignedResource(signature, resource, verkey):
    """
    Returns dict of deserialized resource if signature verifies for resource given
    verification key verkey in base64 url safe unicode format
    Otherwise raises ValidationError

    :param signature: base64 url-file safe unicode string signature generated
        by signing bytes version of resource with privated signing key associated with
        public verification key referenced by key indexed signer field in resource

    :param resource: json encoded unicode string of resource record

    :param verkey: base64 url-file safe unicode string public verification key referenced
        by signer field in resource. This is looked up in database from signer's
        agent data resource

    :return: dict deserialized json resource
    """

    try:
        try:
            rsrc = json.loads(resource, object_pairs_hook=ODict)
        except ValueError as ex:
            raise didering.ValidationError("Invalid JSON")  # invalid json

        if not verify64u(signature, resource, verkey):
            raise didering.ValidationError("Unverifiable signature")  # signature fails

    except didering.ValidationError:
        raise

    except Exception as ex:  # unknown problem
        raise didering.ValidationError("Unexpected error")

    return rsrc


def signResource(resource, sk):
    """
    Produce a signature for resource

    :param resource: byte string message to be signed
    :param sk: byte string signing key
    :return: base64 url-file safe string
    """
    sig = libnacl.crypto_sign(resource, sk)
    sig = sig[:libnacl.crypto_sign_BYTES]

    return bytesToStr64u(sig)


def signResource64u(resource, sk):
    """

    :param resource: string resource
    :param sk: base64 url-file safe private key
    :return: base64 url-file safe signature string
    """
    resource = resource.encode()
    sk = str64uToBytes(sk)

    return signResource(resource, sk)


def generateByteKeys(seed=None):
    """

    :param seed: optional seed value for libnacl.crypto_sign_seed_keypair()
    :return: byte strings (vk, sk)
    """
    if seed is None:
        seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)

    return libnacl.crypto_sign_seed_keypair(seed)


def generate64uKeys(seed=None):
    """

    :param seed: optional seed value for libnacl.crypto_sign_seed_keypair()
    :return: base64 url-file safe key string (vk, sk)
    """
    vk, sk = generateByteKeys(seed)

    return bytesToStr64u(vk), bytesToStr64u(sk)


def genDidHistory(seed=None, changed="2000-01-01T00:00:00+00:00", signer=0, numSigners=3):
    # seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk = generateByteKeys(seed)

    did = makeDid(vk)
    body = {
        "id": did,
        "changed": changed,
        "signer": signer,
        "signers": []
    }

    for i in range(0, numSigners):
        body['signers'].append(bytesToStr64u(vk))

    return vk, sk, did, json.dumps(body, ensure_ascii=False).encode()
