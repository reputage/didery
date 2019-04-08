import ecdsa.curves
import ecdsa.util
import ecdsa.keys
import ecdsa.ellipticcurve

from hashlib import sha3_256
from fastecdsa.keys import gen_keypair
from fastecdsa import curve as fast_curve
from fastecdsa.ecdsa import verify as fast_verify
from fastecdsa.ecdsa import sign as fast_sign
from fastecdsa.point import Point as fPoint
from collections import OrderedDict as ODict

try:
    import simplejson as json
except ImportError:
    import json

from ..help.helping import str64uToBytes, bytesToStr64u, makeDid
from didery import didering


def verify(sig, msg, vk):
    """
    Returns True if signature sig of message msg is verified with
    verification key vk Otherwise False

    :param sig: byte string representation of signature
    :param msg: byte string representation of message
    :param vk: ecdsa.keys.VerifyingKey instance
    :return: boolean
    """
    try:
        order = ecdsa.curves.SECP256k1.order
        r, s = ecdsa.util.sigdecode_string(sig, order)
        x = vk.pubkey.point.x()
        y = vk.pubkey.point.y()
        point = fPoint(x, y, fast_curve.secp256k1)  # fastecdsa public key
        result = fast_verify((r, s), msg.decode(), point, fast_curve.secp256k1, hashfunc=sha3_256)
    except Exception as ex:
        return False
    return True if result else False


def verify64u(signature, message, verkey):
    """
    Returns True if signature is valid for message with respect to verification
    key verkey

    :param signature: base64 url-file safe string signature
    :param message: utf-8 string
    :param verkey: base64 url-file safe string verification key
    :return: boolean

    """
    sig = str64uToBytes(signature)
    bytes_vk = str64uToBytes(verkey)
    vk = ecdsa.keys.VerifyingKey.from_string(bytes_vk, ecdsa.curves.SECP256k1)

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

    :param resource: byte string resource
    :param sk: byte string private key
    :return: base64 url-file safe encoded signature
    """
    pyec_sk = ecdsa.keys.SigningKey.from_string(sk, ecdsa.curves.SECP256k1, hashfunc=sha3_256)
    d = pyec_sk.privkey.secret_multiplier
    r, s = fast_sign(resource.decode(), d, fast_curve.secp256k1, sha3_256)
    signature = ecdsa.util.sigencode_string(r, s, ecdsa.curves.SECP256k1.order)

    return bytesToStr64u(signature)


def signResource64u(resource, sk):
    """

    :param resource: string resource
    :param sk: base64 url-file safe encoded private key
    :return: base64 url-file safe encoded signature
    """
    sk = str64uToBytes(sk)

    return signResource(resource.encode(), sk)


def generateByteKeys():
    priv_key, pub_key = gen_keypair(fast_curve.secp256k1)
    curve = ecdsa.curves.SECP256k1.curve
    order = ecdsa.curves.SECP256k1.order
    pyec_point = ecdsa.ellipticcurve.Point(curve, pub_key.x, pub_key.y, order)
    pyec_publicKey = ecdsa.keys.VerifyingKey.from_public_point(pyec_point, ecdsa.curves.SECP256k1)
    pyec_privateKey = ecdsa.keys.SigningKey.from_secret_exponent(priv_key, ecdsa.curves.SECP256k1)
    vk = pyec_publicKey.to_string()
    sk = pyec_privateKey.to_string()

    return vk, sk


def generate64uKeys():
    vk, sk = generateByteKeys()

    return bytesToStr64u(vk), bytesToStr64u(sk)


def genDidHistory(changed="2000-01-01T00:00:00+00:00", signer=0, numSigners=3):
    """

    :param changed: string time
    :param signer: int "signer" index
    :param numSigners: int number of public keys to include in "signers" field
    :return: byte string vk, byte string sk, string did, byte string encoded json object
    """
    vk, sk = generateByteKeys()

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
