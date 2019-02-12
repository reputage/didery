import re
import importlib

"""
did-reference      = did [ "?" did-query ] [ "/" did-path ] [ "#" did-fragment ]
did                = "did:" method ":" specific-idstring
method             = 1*methodchar
methodchar         = %x61-7A / DIGIT
specific-idstring  = idstring *( ":" idstring )
idstring           = 1*idchar
idchar             = ALPHA / DIGIT / "." / "-"
"""


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
        Parses and returns keystr from did
        raises ValueError if fails parsing
        """
        did_pattern = "(did):([a-z\d]+):([:\w\.\-=]+)(?:\?([\w\-=&]+))?(?:\/([\w\-\/]+))?(?:\#([\w]+))?"
        matches = re.match(did_pattern, self.__did_reference)
        if matches:
            self.scheme, self.method, self.idString, self.query, self.path, self.fragment = matches.groups()
            self.__did = "{}:{}:{}".format(self.scheme, self.method, self.idString)
        else:
            raise ValueError("Could not parse DID.")

        return self

        # try:  # correct did format  pre:method:idstring?query/path#fragment
        #     if "?" in did_reference:
        #         self.__did, remainder = did_reference.split("?", 1)
        #         if "/" in remainder:
        #             self.query, remainder = remainder.split("/", 1)
        #             if "#" in remainder:
        #                 self.path, self.fragment = remainder.split("#", 1)
        #             else:
        #                 self.path = remainder
        #         elif "#" in remainder:
        #             self.query, self.fragment = remainder.split("#", 1)
        #         else:
        #             self.query = remainder
        #     elif "/" in did_reference:
        #         self.__did, remainder = did_reference.split("/", 1)
        #         if "#" in remainder:
        #             self.path, self.fragment = remainder.split("#", 1)
        #         else:
        #             self.path = remainder
        #     elif "#" in did_reference:
        #         self.__did, self.fragment = did_reference.split("#", 1)
        #     else:
        #         self.__did = did_reference
        #
        #     self.scheme, self.method, self.idString = self.__did.split(":", 2)
        # except ValueError as ex:
        #     raise ValueError("Invalid DID value")

    def _validate(self):
        if not self.__did_reference.startswith("did"):
            raise ValueError("Invalid Scheme Value.")

        self._extractDidParts()

    @property
    def did_reference(self):
        reference = ""
        if self.query:
            reference += "?{}".format(self.query)

        if self.path:
            reference += "/{}".format(self.path)

        if self.fragment:
            reference += "#{}".format(self.fragment)

        self.__did_reference = "{}{}".format(self.did, reference)

        return self.__did_reference

    @property
    def did(self):
        self.__did = "{}:{}:{}".format(self.scheme, self.method, self.idString)

        return self.__did

    def match_vk(self, vk):
        return vk == self.vk


def getDIDModel(did_reference):
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
