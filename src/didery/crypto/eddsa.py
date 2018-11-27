from collections import OrderedDict as ODict

import simplejson as json

from didery import didering
from didery.help.helping import verify64u


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