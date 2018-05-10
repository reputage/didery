from collections import OrderedDict as ODict
import falcon
import libnacl
import base64

try:
    import simplejson as json
except ImportError:
    import json

from .. import didering


def parseSignatureHeader(signature):
    """
    Returns ODict of fields and values parsed from signature
    which is the value portion of a Signature header

    Signature header has format:

        Signature: headervalue

    Headervalue:
        tag = "signature"

    or

        tag = "signature"; tag = "signature"  ...

    where tag is the name of a field in the body of the request whose value
    is a DID from which the public key for the signature can be obtained
    If the same tag appears multiple times then only the last occurrence is returned

    each signature value is a doubly quoted string that contains the actual signature
    in Base64 url safe format. By default the signatures are EdDSA (Ed25519)
    which are 88 characters long (with two trailing pad bytes) that represent
    64 byte EdDSA signatures

    An option tag name = "kind" with values "EdDSA"  "Ed25519" may be present
    that specifies the type of signature. All signatures within the header
    must be of the same kind.

    The two tag fields currently supported are "did" and "signer"


    """
    sigs = ODict()
    if signature:
        clauses = signature.split(";")
        for clause in clauses:
            clause = clause.strip()
            if not clause:
                continue
            try:
                tag, value = clause.split("=", maxsplit=1)
            except ValueError as ex:
                continue
            tag = tag.strip()
            if not tag:
                continue
            value = value.strip()
            if not value.startswith('"') or not value.endswith('"') or len(value) < 3:
                continue
            value = value[1:-1]
            value = value.strip()
            sigs[tag] = value

    return sigs


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


def parseReqBody(req):
    """
    :param req: Falcon Request object
    """
    try:
        raw_json = req.stream.read()
    except Exception as ex:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Error',
                               'Error reading request body.')

    try:
        result_json = json.loads(raw_json, encoding='utf-8')
    except ValueError:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed JSON',
                               'Could not decode the request body. The '
                               'JSON was incorrect.')

    req.body = result_json
    return raw_json


def validateRequiredFields(required, resource):
    """
    Validate that all required fields are present in resource
    :param required: list of required fields
    :param resource: dict to be checked
    """
    for req in required:
        if req not in resource:
            raise falcon.HTTPError(falcon.HTTP_400,
                                   'Missing Required Field',
                                   'Request must contain {} field.'.format(req))


def keyToKey64u(key):
    """
    Convert and return bytes key to unicode base64 url-file safe version
    """
    return base64.urlsafe_b64encode(key).decode("utf-8")


def key64uToKey(key64u):
    """
    Convert and return unicode base64 url-file safe key64u to bytes key
    """
    return base64.urlsafe_b64decode(key64u.encode("utf-8"))


def signResource(resource, sKey):
    sig = libnacl.crypto_sign(resource, sKey)
    sig = sig[:libnacl.crypto_sign_BYTES]

    return keyToKey64u(sig)


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


def extractDidParts(did, method="dad"):
    """
    Parses and returns keystr from did
    raises ValueError if fails parsing
    """
    try:  # correct did format  pre:method:keystr
        pre, meth, keystr = did.split(":")
    except ValueError as ex:
        raise ValueError("Malformed DID value")

    if pre != "did":
        raise ValueError("Invalid DID identifier")

    if meth != method:
        raise ValueError("Invalid DID method")

    return keystr
