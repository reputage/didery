# ================================================== #
#                       FIELDS                       #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/08/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class Field:
    """
    Class for table field/columns.
    """
    Title = None
    Length = 4

    __pragma__("kwargs")
    def __init__(self, title=None, length=None):
        """
        Initialize Field object. Set title and length.
        """
        self.title = self.Title
        if title is not None:
            self.title = title

        self.mlength = self.Length
        if length is not None:
            self.mlength = length

        self.name = self.title.lower()

    __pragma__("nokwargs")

    # ============================================== #

    def format(self, data):
        """
        Formats the data to a string matching the expected view for this field.

            Parameters:
            data - Data object to be formatted
        """
        return str(data)

    # ============================================== #

    def shorten(self, string):
        """
        Shortens the string to an appropriate length for display.

            Parameters:
            string - String to be shortened
        """
        return string

    # ============================================== #

    def view(self, data):
        """
        Returns a vnode <td> suitable for display in a table.

            Parameters:
            data - Data object
        """
        if data == None:
            data = ""
        formatted = self.format(data)
        return m("td", {"title": formatted}, self.shorten(formatted))

# ================================================== #

class FillField(Field):
    """
    Field that should "use remaining space" for display.
    """
    Length = 100

    def view(self, data):
        node = super().view(data)
        node.attrs["class"] = "fill-space"
        return node

# ================================================== #

class DateField(Field):
    """
    Field for displaying dates.
    """
    Length = 12
    Title = "Date"

# ================================================== #

class EpochField(DateField):
    """
    Field for displaying time since the epoch.
    """
    def format(self, data):
        # Make format match that of other typical dates from server
        data = __new__(Date(data / 1000)).toISOString()
        return super().format(data)

# ================================================== #

class IDField(Field):
    """
    Field for displaying ids.
    """
    Length = 4
    Title = "UID"
    Header = ""

    def format(self, string):
        if string.startswith(self.Header):
            string = string[len(self.Header):]

        return super().format(string)

# ================================================== #

class DIDField(IDField):
    """
    Field for displaying dids.
    """
    Header = "did:dad:"
    Title = "DID"

# ================================================== #
#                        EOF                         #
# ================================================== #