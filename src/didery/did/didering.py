import re

"""
did-reference      = did [ "/" did-path ] [ "#" did-fragment ]
did                = "did:" method ":" specific-idstring
method             = 1*methodchar
methodchar         = %x61-7A / DIGIT
specific-idstring  = idstring *( ":" idstring )
idstring           = 1*idchar
idchar             = ALPHA / DIGIT / "." / "-"
"""


def extractDidParts(did_reference):
    """
    Parses and returns keystr from did
    raises ValueError if fails parsing
    """
    scheme, method, idstring, query, path, fragment = None, None, None, None, None, None

    did_pattern = "(did):([a-z\d]+):([:\w\.\-=]+)(?:\?([\w\-=&]+))?(?:\/([\w\-\/]+))?(?:\#([\w]+))?"
    matches = re.match(did_pattern, did_reference)
    if matches:
        return matches.groups()
    else:
        raise ValueError("Invalid DID value")

    # try:  # correct did format  pre:method:idstring?query/path#fragment
    #     if "?" in did_reference:
    #         did, remainder = did_reference.split("?", 1)
    #         if "/" in remainder:
    #             query, remainder = remainder.split("/", 1)
    #             if "#" in remainder:
    #                 path, fragment = remainder.split("#", 1)
    #             else:
    #                 path = remainder
    #         elif "#" in remainder:
    #             query, fragment = remainder.split("#", 1)
    #         else:
    #             query = remainder
    #     elif "/" in did_reference:
    #         did, remainder = did_reference.split("/", 1)
    #         if "#" in remainder:
    #             path, fragment = remainder.split("#", 1)
    #         else:
    #             path = remainder
    #     elif "#" in did_reference:
    #         did, fragment = did_reference.split("#", 1)
    #     else:
    #         did = did_reference
    #
    #     scheme, method, idstring = did.split(":", 2)
    # except ValueError as ex:
    #     raise ValueError("Invalid DID value")
    #
    # return scheme, method, idstring, query, path, fragment
