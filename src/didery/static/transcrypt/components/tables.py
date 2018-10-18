# ================================================== #
#                       TABLES                       #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/08/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

import didery.static.transcrypt.server as server
import didery.static.transcrypt.components.fields as field

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class Table:
    """
    Class for table, headers, and display data..
    """
    no_results_text = "No results found."

    def __init__(self, fields):
        """
        Initializes Table object.

            Parameters:
            fields - Table fields objects
        """
        self.max_size = 1000
        self.fields = fields
        self.data = []
        self._shownData = []
        self.view = {
            "view": self._view
        }

        self._selected = None
        self.detailSelected = ""

        self.filter = None
        self.sortField = None
        self.reversed = False

        self.total = 0
        self.shown = 0

    # ============================================== #

    def _stringify(self, obj):
        """
        Converts provided json-like object to user-friendly string.

            Parameters:
            obj - JSON like object
        """
        def replacer(key, value):
            if key.startswith("_"):
                return
            return value
        return JSON.stringify(obj, replacer, 2)

    # ============================================== #

    def _limitText(self):
        """
        Limits displayed results.
        """
        return "Limited to {} results.".format(self.max_size)

    # ============================================== #

    def _selectRow(self, event, obj):
        """
        Deselects any previously selected row and selects row
        specified in event.

            Parameters:
            event - Specified event
            obj - Row data object
        """
        if self._selected is not None:
            del self._selected._selected

            if self._selected._uid == obj._uid:
                self._selected = None
                self.detailSelected = ""
                return

        self._selected = obj
        obj._selected = True
        self.detailSelected = self._stringify(obj)

    # ============================================== #

    def refresh(self):
        """
        Refreshes data from server and returns a promise that resolves
        when finished.
        """
        self._setData([])
        p = __new__(Promise(lambda resolve: resolve()))
        return Promise

    # ============================================== #

    def clear(self):
        """
        Removes memory of all current data.
        """
        self.total = 0
        server.clearArray(self.data)

    # ============================================== #

    def _makeDummyData(self, count):
        """
        Creates test data.

            Parameters:
            count - Integer
        """
        data = []
        for i in range(count):
            obj = {}
            for field in self.fields:
                obj[field.name] = "test{0} {1}".format(i, field.name)
            data.append(obj)
        return data

    # ============================================== #

    __pragma__("kwargs")
    def _setData(self, data, clear=True):
        """
        Clears existing data and uses provided data instead.
        Adds "_uid" field to each piece of data, for internal tracking.

            Parameters:
            data - Input data
            clear - Boolean
        """
        if clear:
            self.clear()
        for datum in data:
            datum._uid = self.total
            self.data.append(datum)
            self.total += 1
        self._processData()
    __pragma__("nokwargs")

    # ============================================== #

    def setFilter(self, func):
        """
        Sets table filter function.

            Parameters:
            func - Filter function
        """
        if func != self.filter:
            self.filter = func
            self._processData()

    # ============================================== #

    def setSort(self, field):
        """
        Sets sort on given field. If same as currently-sorted field,
        reverse sort on said field.

            Parameters:
            field - Field to sort by
        """
        if self.sortField == field:
            self.reversed = not self.reversed
        else:
            self.reversed = False
            self.sortField = field

        self._sortData()

    # ============================================== #

    def _sortData(self):
        """
        Sorts table data.
        """
        if self.sortField is None:
            return

        self._shownData.sort(key=lambda obj: self._getField(obj, self.sortField), reverse=self.reversed)

    # ============================================== #

    def _processData(self):
        """
        Processes data, determines which items to show, and
        puts items into sorted list.
        """
        server.clearArray(self._shownData)

        self.shown = 0
        for obj in self.data:
            if self.shown >= self.max_size:
                break
            if self.filter is not None:
                if not self.filter(obj):
                    continue

            self._shownData.append(obj)
            self.shown += 1

        self._sortData()

    # ============================================== #

    def _getField(self, obj, field):
        """
        Gets info from object matching given field.

            Parameters:
            obj - Data object
            field - Field/Key
        """
        return obj[field.name]

    # ============================================== #

    def _makeRow(self, obj):
        """
        Returns array of <td> vnodes representing a row.

            Parameters:
            obj - Data object
        """
        return [field.view(self._getField(obj, field)) for field in self.fields]

    # ============================================== #

    def _view(self):
        """
        Returns table markup.
        """
        headers = []
        for field in self.fields:
            def makeScope(f):
                return lambda event: self.setSort(f)
            if field == self.sortField:
                if self.reversed:
                    icon = m("i.angle.down.icon")
                else:
                    icon = m("i.angle.up.icon")
                header = m("th.ui.right.labeled.icon", {"onclick": makeScope(field)},
                           icon,
                           field.title)
            else:
                header = m("th", {"onclick": makeScope(field)}, field.title)

            headers.append(header)

        rows = []
        for obj in self._shownData:
            row = self._makeRow(obj)

            def makeScope(o):
                return lambda event: self._selectRow(event, o)
            if obj._selected:
                rows.append(m("tr.active", {"onclick": makeScope(obj)}, row))
            else:
                rows.append(m("tr", {"onclick": makeScope(obj)}, row))

        if self.shown >= self.max_size:
            rows.append(m("tr", m("td", self._limitText())))

        if not self.shown:
            rows.append(m("tr", m("td", self.no_results_text)))

        return m("table", {"class": "ui selectable celled unstackable single line left aligned table"},
                 m("thead",
                   m("tr", {"class": "center aligned"}, headers)
                   ),
                 m("tbody",
                   rows
                   )
                 )

# ================================================== #

class ErrorsTable(Table):
    """
    Class for errors table.
    """
    def __init__(self):
        """
        Initializes ErrorsTable object. Sets up error table fields.
        """
        fields = [
            field.FillField("Title"),
            field.FillField("Message"),
            field.DateField("Time")
        ]
        super().__init__(fields)

    # ============================================== #

    def refresh(self):
        """
        Refreshes table data.
        """
        self.clear()
        errors = server.manager.errors
        return errors.refreshErrors().then(lambda: self._setData(errors.errors))

    # ============================================== #

    def _getField(self, obj, field):
        """
        Extracts data from json-like object.

            Parameters:
            obj - Data object
            field - Field/Key
        """
        if field.name == "title":
            return obj.title
        elif field.name == "message":
            return obj.msg
        elif field.name == "time":
            return obj.time

# ================================================== #

class RelaysTable(Table):
    """
    Class for relays table.
    """
    def __init__(self):
        """
        Initializes RelaysTable object. Sets up relays table fields.
        """
        fields = [
            field.FillField("Host"),
            field.FillField("Port"),
            field.FillField("Name"),
            field.FillField("Main"),
            field.IDField("UID"),
            field.FillField("Status")
        ]
        super().__init__(fields)

    # ============================================== #

    def refresh(self):
        """
        Refreshes table data.
        """
        self.clear()
        relays = server.manager.relays
        return relays.refreshRelays().then(lambda: self._setData(relays.relays))

    # ============================================== #

    def _getField(self, obj, field):
        """
        Extracts data from json-like object.

            Parameters:
            obj - Data object
            field - Field/Key
        """
        if field.name == "host":
            return obj["host_address"]
        elif field.name == "port":
            return obj["port"]
        elif field.name == "name":
            return obj["name"]
        elif field.name == "main":
            return obj["main"]
        elif field.name == "uid":
            return obj["uid"]
        elif field.name == "status":
            return obj["status"]

# ================================================== #

class BlobsTable(Table):
    """
    Class for blobs table.
    """
    def __init__(self):
        """
        Initializes BlobsTable object. Sets up blobs table fields.
        """
        fields = [
            field.DIDField("DID"),
            field.FillField("Blob")
        ]
        super().__init__(fields)

    # ============================================== #

    def refresh(self):
        """
        Refreshes table data.
        """
        self.clear()
        blobs = server.manager.otpBlobs
        return blobs.refreshBlobs().then(lambda: self._setData(blobs.blobs))

    # ============================================== #

    def _getField(self, obj, field):
        """
        Extracts data from json-like object.

            Parameters:
            obj - Data object
            field - Field/Key
        """

        if field.name == "did":
            return obj.otp_data.id
        elif field.name == "blob":
            return obj.otp_data.blob

# ================================================== #

class HistoryTable(Table):
    """
    Class for history table.
    """
    def __init__(self):
        """
        Initializes HistoryTable object. Sets up history table fields.
        """
        fields = [
            field.DIDField("DID"),
            field.DateField("Changed"),
            field.FillField("Signer"),
            field.FillField("Signers"),
            field.FillField("Signatures")
        ]
        super().__init__(fields)

    # ============================================== #

    def refresh(self):
        """
        Refreshes table data.
        """
        self.clear()
        history = server.manager.history
        return history.refreshHistory().then(lambda: self._setData(history.history))

    # ============================================== #

    def _getField(self, obj, field):
        """
        Extracts data from json-like object.

            Parameters:
            obj - Data object
            field - Field/Key
        """

        if field.name == "did":
            return obj.history.id
        elif field.name == "changed":
            return obj.history.changed
        elif field.name == "signer":
            return obj.history.signer
        elif field.name == "signers":
            signers = ""
            for signer in obj.history.signers:
                signers += signer + ", "
            signers = signers[:-2]
            return signers
        elif field.name == "signatures":
            signatures = ""
            for key, value in dict(obj.signatures).items():
                signatures += value + ", "
            signatures = signatures[:-2]
            return signatures

# ================================================== #
#                        EOF                         #
# ================================================== #
