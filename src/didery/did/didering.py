import re

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
        self.did_reference = did_reference
        self.did = None
        self.scheme = None
        self.method = None
        self.idString = None
        self.pubkey = None
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
        matches = re.match(did_pattern, self.did_reference)
        if matches:
            self.scheme, self.method, self.idString, self.query, self.path, self.fragment = matches.groups()
            self.did = "{}:{}:{}".format(self.scheme, self.method, self.idString)
            self.pubkey = self.idString
        else:
            raise ValueError("Could not parse DID.")

        return self

        # try:  # correct did format  pre:method:idstring?query/path#fragment
        #     if "?" in did_reference:
        #         self.did, remainder = did_reference.split("?", 1)
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
        #         self.did, remainder = did_reference.split("/", 1)
        #         if "#" in remainder:
        #             self.path, self.fragment = remainder.split("#", 1)
        #         else:
        #             self.path = remainder
        #     elif "#" in did_reference:
        #         self.did, self.fragment = did_reference.split("#", 1)
        #     else:
        #         self.did = did_reference
        #
        #     self.scheme, self.method, self.idString = self.did.split(":", 2)
        # except ValueError as ex:
        #     raise ValueError("Invalid DID value")

    def _validate(self):
        if not self.did_reference.startswith("did"):
            raise ValueError("Invalid Scheme Value.")

        self._extractDidParts()


