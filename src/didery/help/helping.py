from collections import OrderedDict as ODict
import falcon
import base64
import tempfile
import os
import shutil

try:
    import simplejson as json
except ImportError:
    import json


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


def parseReqBody(req):
    """
    :param req: Falcon Request object
    """
    try:
        raw_json = req.stream.read()
    except Exception as ex:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Request Error',
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


def makeDid(vk, method="dad"):
    """
    Create and return Did from bytes vk.
    vk is 32 byte verifier key from EdDSA (Ed25519) keypair
    """
    # convert verkey to jsonable unicode string of base64 url-file safe
    vk64u = base64.urlsafe_b64encode(vk).decode("utf-8")
    did = "did:{}:{}".format(method, vk64u)
    return did


def extractDidParts(did, method="dad"):
    """
    Parses and returns keystr from did
    raises ValueError if fails parsing
    """
    try:  # correct did format  pre:method:keystr
        pre, meth, keystr = did.split(":")
    except ValueError as ex:
        raise ValueError("Invalid DID value")

    if pre != "did":
        raise ValueError("Invalid DID identifier")

    if meth != method:
        raise ValueError("Invalid DID method")

    return keystr


def parseQString(req, resp, resource, params):
    req.offset = 0
    req.limit = 10

    if req.query_string:
        queries = req.query_string.split('&')
        for query in queries:
            key, val = qStringValidation(query)
            if key == 'offset':
                req.offset = val
            if key == 'limit':
                req.limit = val


def qStringValidation(query):
    keyval = query.split('=')

    if len(keyval) != 2:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Query String',
                               'url query string missing value(s).')

    key = keyval[0]
    val = keyval[1]

    try:
        val = int(val)
    except ValueError as ex:
        raise falcon.HTTPError(falcon.HTTP_400,
                               'Malformed Query String',
                               'url query string value must be a number.')

    return key, val


def setupTmpBaseDir():
    """
    Create temporary directory
    """
    return tempfile.mkdtemp(prefix="didery",  suffix="test", dir="/tmp")


def cleanupTmpBaseDir(baseDirPath):
    """
    Remove temporary root of baseDirPath
    Ascend tree to find temporary root directory
    """
    if os.path.exists(baseDirPath):
        shutil.rmtree(baseDirPath)
