# ================================================== #
#                     DASHBOARD                      #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/14/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class Searcher:
    """
    Class to search for a certain string in any dict object.
    """
    def __init__(self):
        """
        Initializes Searcher object.
        """
        self.searchTerm = None
        self.caseSensitive = False

    # ============================================== #

    def setSearch(self, term):
        """
        Sets search term. If term is surrounded by quotes, removes
        them and makes search case sensitive. Otherwise, search is
        not case sensitive.

            Parameters::
            term - Base search string
        """
        self.searchTerm = term or ""
        self.caseSensitive = self.searchTerm.startswith('"') and self.searchTerm.endswith('"')
        if self.caseSensitive:
            self.searchTerm = self.searchTerm[1:-1]
        else:
            self.searchTerm = self.searchTerm.lower()

    # ============================================== #

    def _checkPrimitive(self, item):
        """
        Checks for search term in provided string.
        """
        if isinstance(item, str):
            if not self.caseSensitive:
                item = item.lower()
            return self.searchTerm in item
        return False

    # ============================================== #

    def _checkAny(self, value):
        """
        Checks for search term in any provided dict, list, or primitive type.
        """
        if isinstance(value, dict) or isinstance(value, Object):
            return self.search(value)
        elif isinstance(value, list):
            for item in value:
                if self._checkAny(item):
                    return True
            return False
        else:
            return self._checkPrimitive(value)

    # ============================================== #

    def search(self, obj: dict):
        """
        Returns True if obj recursively contains search term string in any field.
        """
        __pragma__("jsiter")
        for key in obj:
            if key.startswith("_"):
                continue

            value = obj[key]
            if self._checkAny(value):
                return True
        return False
        __pragma__("nojsiter")

# ================================================== #
#                        EOF                         #
# ================================================== #