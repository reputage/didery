# ================================================== #
#                     DASHBOARD                      #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 04/26/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

import server

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class Tab:
    """
    Base class for tabs, including menu link and displayed tab itself.
    """
    Name = ""
    Icon = ""
    DataTab = ""
    Active = False

    def __init__(self):
        """
        Initialize Tab object. Load base attributes and markup.
        """
        self._menu_attrs = {"data-tab": self.DataTab}
        self._tab_attrs = {"data-tab": self.DataTab}
        self._menu = "a.item"
        self._tab = "div.ui.bottom.attached.tab.segment"

        if self.Active:
            self._menu += ".active"
            self._tab += ".active"

    # ============================================== #

    def menu_item(self):
        """
        Returns menu item markup for given tab.
        """
        return m(self._menu, self._menu_attrs, self.Name)

    # ============================================== #

    def tab_item(self):
        """
        Returns tab item markup for given tab.
        """
        return m(self._tab, self._tab_attrs, self.main_view())

    # ============================================== #

    def main_view(self):
        """
        Returns main view markup for given tab.
        """
        return m("div", "hello " + self.Name)

# ================================================== #

class TabledTab(Tab):
    """
    Base class for tabs in the dashboard interface. Uses table and details view.
    """
    def __init__(self):
        """
        Initialize TabledTab object.
        """
        super().__init__()
        self.table = None
        self.setup_table()
        self.copiedDetails = ""
        self._detailsId = self.DataTab + "DetailsCodeBlock"
        self._copiedId = self.DataTab + "CopiedCodeBlock"
        self._copyButtonId = self.DataTab + "CopyButton"
        self._clearButtonId = self.DataTab + "ClearButton"

    # ============================================== #

    def setup_table(self):
        """
        Sets up table object.
        """
        self.table = Table([])

    # ============================================== #

    def _copyDetails(self):
        self.copiedDetails = self.table.detailSelected

    # ============================================== #

    def _getRows(self):
        return jQuery("[data-tab='{0}'].tab table > tbody > tr".format(self.DataTab))

    # ============================================== #

    def _getLabel(self):
        return jQuery(".menu a[data-tab='{0}'] .ui.label".format(self.DataTab))

    # ============================================== #

    def _clearCopy(self):
        self.copiedDetails = ""

    # ============================================== #

    def menu_item(self):
        return m(self._menu, self._menu_attrs,
                 m("div.menu-item-text", self.Name),
                 m(self.Icon),
                 m("div.ui.label.small", "{0}/{1}".format(self.table.shown, self.table.total))
                 )

    # ============================================== #

    def main_view(self):
        return m("div",
                 m("div.table-container", m(self.table.view)),
                 m("div.ui.hidden.divider"),
                 m("div.ui.two.cards", {"style": "height: 45%;"},
                   m("div.ui.card",
                     m("div.content.small-header",
                       m("div.header",
                         m("span", "Details"),
                         m("span.ui.mini.right.floated.button", {"onclick": self._copyDetails, "id": self._copyButtonId},
                           "Copy")
                         )
                       ),
                     m("pre.content.code-block", {"id": self._detailsId},
                       self.table.detailSelected
                       )
                     ),
                   m("div.ui.card",
                     m("div.content.small-header",
                       m("div.header",
                         m("span", "Copied"),
                         m("span.ui.mini.right.floated.button", {"onclick": self._clearCopy, "id": self._clearButtonId},
                           "Clear")
                         )
                       ),
                     m("pre.content.code-block", {"id": self._copiedId},
                       self.copiedDetails
                       )
                     )
                   )
                 )

# ================================================== #

class Field:
    """
    A field/column of a table.
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
        """
        return str(data)

    # ============================================== #

    def shorten(self, string):
        """
        Shortens the string to an appropriate length for display.
        """
        return string

    # ============================================== #

    def view(self, data):
        """
        Returns a vnode <td> suitable for display in a table.
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
    """Stripped from beginning of string for displaying."""

    def format(self, string):
        if string.startswith(self.Header):
            string = string[len(self.Header):]

        return super().format(string)

# ================================================== #

class DIDField(IDField):
    Header = "did:dad:"
    Title = "DID"

# ================================================== #

class Table:
    """
    A table, its headers, and its data to be displayed.
    """
    no_results_text = "No results found."

    def __init__(self, fields):
        """
        Initializes the Table object.
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
        Converts the provided json-like object to a user-friendly string.
        """
        def replacer(key, value):
            if key.startswith("_"):
                return
            return value
        return JSON.stringify(obj, replacer, 2)

    # ============================================== #

    def _limitText(self):
        return "Limited to {} results.".format(self.max_size)

    # ============================================== #

    def _selectRow(self, event, obj):
        """
        Deselects any previously selected row and selects the row
        specified in the event.
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
        Refreshes any data from the server and returns a promise which resolves
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
        Clears existing data and uses the provided data instead.
        Adds a "_uid" field to each piece of data, for tracking internally.
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
        if func != self.filter:
            self.filter = func
            self._processData()

    # ============================================== #

    def setSort(self, field):
        """
        Sets our sort to be on the given field.
        If this is the same as our currently-sorting field, then reverses the sort
        on that same field.
        """
        if self.sortField == field:
            self.reversed = not self.reversed
        else:
            self.reversed = False
            self.sortField = field

        self._sortData()

    # ============================================== #

    def _sortData(self):
        if self.sortField is None:
            return

        self._shownData.sort(key=lambda obj: self._getField(obj, self.sortField), reverse=self.reversed)

    # ============================================== #

    def _processData(self):
        """
        Processes our data, determining which items to show and putting them into
        a list that is sorted if necessary.
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
        Gets the info from the object matching the given field.
        """
        return obj[field.name]

    # ============================================== #

    def _makeRow(self, obj):
        """
        Returns an array of <td> vnodes representing a row.
        """
        return [field.view(self._getField(obj, field)) for field in self.fields]

    # ============================================== #

    def _view(self):
        headers = []
        for field in self.fields:
            def makeScope(f):
                return lambda event: self.setSort(f)
            if field == self.sortField:
                if self.reversed:
                    icon = m("i.arrow.down.icon")
                else:
                    icon = m("i.arrow.up.icon")
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

class ErrorsTable(Table):
    def __init__(self):
        fields = [
            FillField("Title"),
            FillField("Message"),
            DateField("Time")
        ]
        super().__init__(fields)

    def refresh(self):
        self.clear()
        errors = server.manager.errors
        return errors.refreshErrors().then(lambda: self._setData(errors.errors))

    def _getField(self, obj, field):
        if field.name == "title":
            return obj.title
        elif field.name == "message":
            return obj.msg
        elif field.name == "time":
            return obj.time

class Errors(TabledTab):
    Name = "Errors"
    Icon = "i.chart.bar.icon"
    DataTab = "errors"
    Active = True

    def setup_table(self):
        self.table = ErrorsTable()

# ================================================== #

class Tabs:
    """
    Class for managing all displayed tabs.
    """

    def __init__(self):
        """
        Initialize Tabs object. Load in all tabs and setup
        document level functions.
        """
        self.tabs = [Errors()]

        self._refreshing = False
        self._refreshPromise = None

        jQuery(document).ready(lambda: jQuery('.menu > a.item').tab())

        self.refresh()

    def refresh(self):
        """
        Retrieves server data and populates our tabs and tables.
        """
        if self._refreshing:
            return self._refreshPromise
        self._refreshing = True

        promises = []
        for tab in self.tabs:
            promises.append(tab.table.refresh())

        def done():
            self._refreshing = False

        self._refreshPromise = Promise.all(promises)
        self._refreshPromise.then(done)
        self._refreshPromise.catch(done)
        return self._refreshPromise

    def currentTab(self):
        """
        Returns current tab.
        """
        active = jQuery(".menu a.item.active")
        data_tab = active.attr("data-tab")
        for tab in self.tabs:
            if tab.DataTab == data_tab:
                return tab
        return None

    def view(self):
        """
        Returns markup for view.
        """
        menu_items = []
        tab_items = []
        for tab in self.tabs:
            menu_items.append(tab.menu_item())
            tab_items.append(tab.tab_item())

        return m("div",
                 m("div.ui.top.attached.tabular.menu",
                   menu_items,
                   m("a.item.tab",
                     m("span.menu-item-text", "Public Keys"),
                     m("i.key.icon")),
                   m("a.item.tab",
                     m("span.menu-item-text", "Encrypted Blobs"),
                     m("i.unlock.alternate.icon")),
                   m("a.item.tab",
                     m("span.menu-item-text", "Relay Servers"),
                     m("i.server.icon")),
                   m("a.item.tab",
                     m("span.menu-item-text", "Error Logs"),
                     m("i.exclamation.circle.icon")),
                   m("div.right.menu",
                     m("div.item",
                       m("div#search.ui.transparent.icon.input",
                         m("input[type=text][placeholder=Search...]"),
                         m("i.search.link.icon"))))
                   ),
                 tab_items,

                 )


        """m("div",
                 m("div.ui.top.attached.tabular.menu",
                   m("a.active.item.tab",
                     m("span.menu-item-text", "Server Status"),
                     m("i.chart.bar.icon")),
                   m("a.item.tab",
                     m("span.menu-item-text", "Public Keys"),
                     m("i.key.icon")),
                   m("a.item.tab",
                     m("span.menu-item-text", "Encrypted Blobs"),
                     m("i.unlock.alternate.icon")),
                   m("a.item.tab",
                     m("span.menu-item-text", "Relay Servers"),
                     m("i.server.icon")),
                   m("a.item.tab",
                     m("span.menu-item-text", "Error Logs"),
                     m("i.exclamation.circle.icon")),
                   m("div.right.menu",
                     m("div.item",
                       m("div#search.ui.transparent.icon.input",
                         m("input[type=text][placeholder=Search...]"),
                           m("i.search.link.icon"))))),
                 m("div.ui.bottom.attached.segment",
                   m("p", "Content Will be visible here.")))"""

# ================================================== #
#                        EOF                         #
# ================================================== #