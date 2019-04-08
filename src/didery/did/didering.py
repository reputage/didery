import re
import importlib

"""
did-reference      = did [ "/" did-path ] [ "?" did-query ] [ "#" did-fragment ]
did                = "did:" method ":" specific-idstring
method             = 1*methodchar
methodchar         = %x61-7A / DIGIT
specific-idstring  = idstring *( ":" idstring )
idstring           = 1*idchar
idchar             = ALPHA / DIGIT / "." / "-"
"""

"""
The [ "/" did-path ] [ "?" did-query ] [ "#" did-fragment ] part of the regex below were pulled from RFC3986 Appendix B
found here https://tools.ietf.org/html/rfc3986#appendix-B 
"""
DID_RE = re.compile(r"""^((did):([a-z\d]+):([:\w.\-=]+))([^?#]*)(?:\?([^#]*))?(?:#(.*))?""")


class Did:
    def __init__(self, did_reference):
        self.__did_reference = did_reference
        self.__did = None
        self.scheme = None
        self.method = None
        self.idString = None
        self.vk = None
        self.query = None
        self.path = None
        self.fragment = None

        self._validate()

    def _extractDidParts(self):
        """
        Parses and saves DID parts from self.__did_reference
        raises ValueError if fails parsing
        """
        matches = DID_RE.match(self.__did_reference)
        if matches:
            self.__did, self.scheme, self.method, self.idString, self.path, self.query, self.fragment = matches.groups()
        else:
            raise ValueError("Could not parse DID.")

        return self

    def _validate(self):
        if not self.__did_reference.startswith("did"):
            raise ValueError("Invalid Scheme Value.")

        self._extractDidParts()

    @property
    def did_reference(self):
        reference = ""
        if self.path:
            reference += "{}".format(self.path)

        if self.query:
            reference += "?{}".format(self.query)

        if self.fragment:
            reference += "#{}".format(self.fragment)

        self.__did_reference = "{}{}".format(self.did, reference)

        return self.__did_reference

    @property
    def did(self):
        self.__did = "{}:{}:{}".format(self.scheme, self.method, self.idString)

        return self.__did

    def match_vk(self, vk):
        """
        Validates that the did's id string was derived from vk.
        This function is meant to be overridden by subclasses.

        :param vk: verifcation/public key string

        Returns: boolean returns true if idstring is derived from vk
        """
        return vk == self.idString


def getDIDModel(did_reference):
    """
    Takes a did string and returns a subclass of Did based on the did method or None if no subclass exists.

    :param did_reference: complete did string ie:
        "did:dad:iy67FstqFl_a5e-sni6yAWoj60-1E2RtzmMGjrjHaSY=?color=blue&type=tshirt/customers/1234#test_did"

    Returns: Did subclass or None if no subclass exists for the did method

    """
    scheme, method, idstring = did_reference.split(":", 2)
    method = method.strip()
    package = 'didery.did.methods.' + method
    class_name = method.capitalize()

    try:
        module = importlib.import_module(package)
    except ModuleNotFoundError as er:
        return None
    except Exception as ex:
        # TODO add error logging here
        return None

    try:
        did_class = getattr(module, class_name)
    except AttributeError as er:
        return None
    except Exception as ex:
        # TODO add error logging here
        return None

    return did_class
