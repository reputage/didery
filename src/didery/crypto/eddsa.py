from collections import OrderedDict as ODict

import libnacl
import simplejson as json

from didery import didering
from didery.help.helping import key64uToKey, keyToKey64u, makeDid


def verify(sig, msg, vk):
    """
    Returns True if signature sig of message msg is verified with
    verification key vk Otherwise False
    All of sig, msg, vk are bytes
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

    signature and verkey are encoded as unicode base64 url-file strings
    and message is unicode string as would be the case for a json object

    """
    sig = key64uToKey(signature)
    vk = key64uToKey(verkey)
    # msg = message.encode("utf-8")
    return verify(sig, message, vk)


def validateSignedResource(signature, resource, verkey, method="dad"):
    """
    Returns dict of deserialized resource if signature verifies for resource given
    verification key verkey in base64 url safe unicode format
    Otherwise returns None


    signature is base64 url-file safe unicode string signature generated
        by signing bytes version of resource with privated signing key associated with
        public verification key referenced by key indexed signer field in resource

    resource is json encoded unicode string of resource record

    verkey is base64 url-file safe unicode string public verification key referenced
        by signer field in resource. This is looked up in database from signer's
        agent data resource

    method is the method string used to generate dids in the resource
    """

    try:
        try:
            rsrc = json.loads(resource, object_pairs_hook=ODict)
        except ValueError as ex:
            raise didering.ValidationError("Invalid JSON")  # invalid json

        ddid = rsrc["id"]

        try:  # correct did format  pre:method:keystr
            pre, meth, keystr = ddid.split(":")
        except ValueError as ex:
            raise didering.ValidationError("Invalid format did field")

        if pre != "did" or meth != method:
            raise didering.ValidationError("Invalid format did field") # did format bad

        if len(verkey) != 44:
            raise didering.ValidationError("Verkey invalid")  # invalid length for base64 encoded key

        if not verify64u(signature, resource, verkey):
            raise didering.ValidationError("Unverifiable signature")  # signature fails

    except didering.ValidationError:
        raise

    except Exception as ex:  # unknown problem
        raise didering.ValidationError("Unexpected error")

    return rsrc


def signResource(resource, sKey):
    sig = libnacl.crypto_sign(resource, sKey)
    sig = sig[:libnacl.crypto_sign_BYTES]

    return keyToKey64u(sig)


def genDidHistory(seed, changed="2000-01-01T00:00:00+00:00", signer=0, numSigners=3):
    # seed = libnacl.randombytes(libnacl.crypto_sign_SEEDBYTES)
    vk, sk = libnacl.crypto_sign_seed_keypair(seed)

    did = makeDid(vk)
    body = {
        "id": did,
        "changed": changed,
        "signer": signer,
        "signers": []
    }

    for i in range(0, numSigners):
        body['signers'].append(keyToKey64u(vk))

    return vk, sk, did, json.dumps(body, ensure_ascii=False).encode()