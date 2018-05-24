# ================================================== #
#                  TEST COMPONENTS                   #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/21/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

import didery.static.transcrypt.components.searcher as searcher
import didery.static.transcrypt.components.tables as tables
import didery.static.transcrypt.components.tabs as tabs
import didery.static.transcrypt.router as router
from tester import test

o = require("mithril/ospec/ospec")
sinon = require("sinon")

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

@test
class Searcher:
    """
    Class for testing searcher.
    """
    class CaseSensitive:
        """
        Class for testing search case sensitivity.
        """
        def beforeEach(self):
            """
            Sets up searcher.
            """
            self.searcher = searcher.Searcher()

        # ========================================== #

        def setSearch(self):
            """
            Tests case sensitivity.
            """
            self.searcher.setSearch('"SensITive"')
            o(self.searcher.searchTerm).equals("SensITive")("Checking search term.")
            o(self.searcher.caseSensitive).equals(True)("Checking case sensitivity.")

        # ========================================== #

        def searchBasic(self):
            """
            Tests basic search.
            """
            self.searcher.setSearch('"Foo"')

            o(self.searcher.search({
                "bar": "foo"
            })).equals(False)("Checking first basic search.")
            o(self.searcher.search({
                "foo": "bar"
            })).equals(False)("Checking second basic search.")
            o(self.searcher.search({
                "Foo": "bar"
            })).equals(False)("Checking third basic search.")
            o(self.searcher.search({
                "Bar": "Foo"
            })).equals(True)("Checking fourth basic search.")

        # ========================================== #

        def searchNested(self):
            """
            Tests nested search.
            """
            self.searcher.setSearch('"Foo"')

            o(self.searcher.search({
                "bar": {
                    "bar": "foo"
                }
            })).equals(False)("Checking first nested search.")
            o(self.searcher.search({
                "bar": {
                    "bar": "Foo"
                }
            })).equals(True)("Checking second nested search.")

        # ========================================== #

        def searchList(self):
            """
            Tests list search.
            """
            self.searcher.setSearch('"Foo"')

            o(self.searcher.search({
                "foo": [0, 1, "foo", 3]
            })).equals(False)("Checking first list search.")
            o(self.searcher.search({
                "foo": [0, 1, "Foo", 3]
            })).equals(True)("Checking second list search.")

        # ========================================== #

        def searchListNested(self):
            """
            Tests nested list search.
            """
            self.searcher.setSearch('"Foo"')

            o(self.searcher.search({
                "bar": [0, 1, {
                    "bar": "foo"
                }, [3, "foo", 5], 6]
            })).equals(False)("Checking first nested list search.")
            o(self.searcher.search({
                "bar": [0, 1, {
                    "bar": "foo"
                }, [3, "Foo", 5], 6]
            })).equals(True)("Checking second nested list search.")
            o(self.searcher.search({
                "bar": [0, 1, {
                    "bar": "Foo"
                }, [3, "foo", 5], 6]
            })).equals(True)("Checking third nested list search.")

        # ========================================== #

        def searchInnerString(self):
            """
            Tests inner string search.
            """
            self.searcher.setSearch('"Foo"')

            o(self.searcher.search({
                "foo": "blah Fblahooblah blah"
            })).equals(False)("Checking first inner string search.")
            o(self.searcher.search({
                "foo": "blah blahFooblah blah"
            })).equals(True)("Checking second inner string search.")

    # ============================================== #

    class CaseInsensitive:
        """
        Class for testing search case sensitivity.
        """
        def beforeEach(self):
            """
            Sets up searcher.
            """
            self.searcher = searcher.Searcher()

        # ========================================== #

        def setSearch(self):
            """
            Tests case sensitivity.
            """
            self.searcher.setSearch("InSensItive")
            o(self.searcher.searchTerm).equals("insensitive")("Checking search term.")
            o(self.searcher.caseSensitive).equals(False)("Checking case sensitivity.")

        # ========================================== #

        def searchBasic(self):
            """
            Tests basic search.
            """
            self.searcher.setSearch('Foo')

            o(self.searcher.search({
                "bar": "foo"
            })).equals(True)("Checking first basic search.")
            o(self.searcher.search({
                "foo": "bar"
            })).equals(False)("Checking second basic search.")
            o(self.searcher.search({
                "Foo": "bar"
            })).equals(False)("Checking third basic search.")
            o(self.searcher.search({
                "Bar": "Foo"
            })).equals(True)("Checking fourth basic search.")

        # ========================================== #

        def searchNested(self):
            """
            Tests nested search.
            """
            self.searcher.setSearch('foo')

            o(self.searcher.search({
                "bar": {
                    "bar": "bar"
                }
            })).equals(False)("Checking first nested search.")
            o(self.searcher.search({
                "bar": {
                    "bar": "Foo"
                }
            })).equals(True)("Checking second nested search.")

        # ========================================== #

        def searchList(self):
            """
            Tests list search.
            """
            self.searcher.setSearch('foo')

            o(self.searcher.search({
                "foo": [0, 1, "bar", 3]
            })).equals(False)("Checking first list search.")
            o(self.searcher.search({
                "foo": [0, 1, "Foo", 3]
            })).equals(True)("Checking second list search.")

        # ========================================== #

        def searchInnerString(self):
            """
            Tests inner string search.
            """
            self.searcher.setSearch('foo')

            o(self.searcher.search({
                "foo": "blah Fblahooblah blah"
            })).equals(False)("Checking first inner string search.")
            o(self.searcher.search({
                "foo": "blah blahFooblah blah"
            })).equals(True)("Checking second inner string search.")

        # ========================================== #

        def searchListNested(self):
            """
            Tests nested list search.
            """
            self.searcher.setSearch('foo')

            o(self.searcher.search({
                "bar": [0, 1, {
                    "bar": "boo"
                }, [3, "boo", 5], 6]
            })).equals(False)("Checking first nested list search.")
            o(self.searcher.search({
                "bar": [0, 1, {
                    "bar": "Foo"
                }, [3, "boo", 5], 6]
            })).equals(True)("Checking second nested list search.")
            o(self.searcher.search({
                "bar": [0, 1, {
                    "bar": "boo"
                }, [3, "Foo", 5], 6]
            })).equals(True)("Checking third nested list search.")

# ================================================== #

@test
class TabledTab:
    """
    Class for testing tabs and tab content.
    """
    _Errors_Data = [{
                    "title": "Invalid Signature.",
                    "msg": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= had an invalid rotation signature.",
                    "time": "2000-01-01T00:00:00+00:00"
                },
                {
                    "title": "Relay Unreachable.",
                    "msg": "Could not establish a connection with relay servers.",
                    "time": "2000-01-01T11:00:00+00:00"
                }]
    _History_Data = [{
                "history":
                {
                    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                    "changed" : "2001-01-01T00:00:00+00:00",
                    "signer": 2,
                    "signers":
                    [
                        "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                        "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
                    ]
                },
                "signatures":
                [
                    "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
                ]
            }, {
                "history":
                {
                    "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                    "changed" : "2000-01-01T00:00:00+00:00",
                    "signer": 1,
                    "signers":
                    [
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
                    ]
                },
                "signatures":
                [
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw==",
                    "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
                ]
            }]
    _Blobs_Data = [{
                "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
            },
            {
                "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
            }]
    _Relays_Data = [{
                "host address": "127.0.0.1",
                "port": 7541,
                "name": "alpha",
                "main": True,
                "uid": "1",
                "status": "connected"
            },
            {
                "host address": "127.0.0.1",
                "port": 7542,
                "name": "beta",
                "main": False,
                "uid": "2",
                "status": "connected"
            }]

    def before(self):
        """
        Sets up fake server.
        """
        self._testServer = sinon.createFakeServer()
        self._testServer.respondWith("[]")
        self._testServer.respondImmediately = True
        window.XMLHttpRequest = XMLHttpRequest

    # ============================================== #

    def after(self):
        """
        Resets fake server.
        """
        self._testServer.restore()

    # ============================================== #

    def asyncBeforeEach(self, done):
        """
        Sets up tabs and pages.

            Parameters:
            done - Automatically included promise done function
        """
        r = router.Router()
        r.route()
        self.tabs = r.tabs
        setTimeout(done)

    # ============================================== #

    def startup(self):
        """
        Tests tab number and order.
        """
        self.tabs.searchAll()
        o(self.tabs.searcher.searchTerm).equals("")("Checking default search string.")
        o(len(self.tabs.tabs)).equals(4)("Checking tab number.")

        current = self.tabs.currentTab()
        o(current.DataTab).equals(self.tabs.tabs[0].DataTab)("Checking first tab.")
        o(type(current)).equals(tabs.History)("Checking tab order.")

        o(self.tabs.tabs[1].DataTab).equals(tabs.Blobs.DataTab)("Checking second tab.")
        o(self.tabs.tabs[2].DataTab).equals(tabs.Relays.DataTab)("Checking third tab.")
        o(self.tabs.tabs[3].DataTab).equals(tabs.Errors.DataTab)("Checking fourth tab.")

    # ============================================== #

    def _setData(self, callback):
        """
        Sets tab data.

            Parameters:
            callback - Callback function
        """
        self.tabs.currentTab().table._setData(self._History_Data)
        self._redraw(callback)

    # ============================================== #

    def _redraw(self, callback):
        """
        Redraws document.

            Parameters:
            callback - Callback function
        """
        m.redraw()
        setTimeout(callback, 50)

    # ============================================== #

    def _clickRow(self, row, callback):
        """
        Clicks row.

            Parameters:
            row - Row index
            callback - Callback function
        """
        self.tabs.tabs[0]._getRows()[row].click()
        self._redraw(callback)

    # ============================================== #

    def _clickId(self, id, callback):
        """
        Clicks element with given id.

            Parameters:
            id - Element id
            callback - Callback function
        """
        jQuery("#" + id).click()
        self._redraw(callback)

    # ============================================== #

    def _tableIsEmpty(self, rows):
        """
        Tests if table is empty.

            Parameters:
            rows - Table rows
        """
        o(rows.length).equals(1)("Checking row length.")
        td = rows.find("td")
        o(td.length).equals(1)("Checking td length.")
        o(td.text()).equals(tables.Table.no_results_text)("Checking table content.")

    # ============================================== #

    def asyncBasicSearch(self, done, timeout):
        """
        Tests basic search.

            Parameters:
            done - Automatically included promise done function
            timeout - Automatically included timeout
        """
        timeout(200)

        jQuery("#" + self.tabs._searchId).val("did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=")
        self.tabs.searchAll()
        o(self.tabs.searcher.searchTerm).equals("did:dad:qt27fthwonzsa88vrtkep6h-4ha8tr54shon1vwl6fe=")("Checking search query.")

        def f1():
            history = self.tabs.tabs[0]
            o(history._getRows().length).equals(1)("Checking visible rows.")
            o(history._getLabel().text()).equals("1/2")("Checking label text.")

            relays = self.tabs.tabs[2]
            self._tableIsEmpty(relays._getRows())
            o(relays._getLabel().text()).equals("0/2")("Checking label text.")

            def f2():
                self._tableIsEmpty(history._getRows())
                o(history._getLabel().text()).equals("0/2")("Checking label text.")

                o(relays._getRows().length).equals(1)("Checking visible rows.")
                o(relays._getLabel().text()).equals("1/2")("Checking label text.")
                done()

            jQuery("#" + self.tabs._searchId).val("alpha")
            self.tabs.searchAll()

            self._redraw(f2)

        def relaysData():
            self.tabs.tabs[2].table._setData(self._Relays_Data)
            self._redraw(f1)

        self.tabs.tabs[0].table._setData(self._History_Data)
        self._redraw(relaysData)

    # ============================================== #

    def tableSort(self):
        """
        Tests table sorting.
        """
        a = {"id": "a", "blob": ""}
        a3 = {"id": "a", "blob": "3"}
        a1 = {"id": "a", "blob": "1"}
        b4 = {"id": "b", "blob": "4"}
        d2 = {"id": "d", "blob": "2"}
        c5 = {"id": "c", "blob": "5"}
        data = [a3, a, a1, b4, d2, c5]

        blobs = self.tabs.tabs[1]
        blobs.table._setData(data)

        field = blobs.table.fields[0]
        o(field.title).equals("DID")("Checking field header.")
        blobs.table.setSort(field)
        o(blobs.table._shownData).deepEquals([a3, a, a1, b4, c5, d2])("Checking row order.")

        blobs.table.setSort(field)
        o(blobs.table._shownData).deepEquals([d2, c5, b4, a1, a, a3])("Checking row order.")

        field = blobs.table.fields[1]
        o(field.title).equals("Blob")("Checking field header.")
        blobs.table.setSort(field)
        o(blobs.table._shownData).deepEquals([a, a1, d2, a3, b4, c5])("Checking row order.")

        blobs.table.setSort(field)
        o(blobs.table._shownData).deepEquals([c5, b4, a3, d2, a1, a])("Checking row order.")

    # ============================================== #

    def asyncSelectRows(self, done, timeout):
        """
        Tests row selection.

            Parameters:
            done - Automatically included promise done function
            timeout - Automatically included timeout
        """
        timeout(200)

        def f1():
            def f2():
                tab = self.tabs.currentTab()
                expected = tab.table._stringify(self._History_Data[0])
                actual = jQuery("#" + tab._detailsId).text()
                o(actual).equals(expected)("Checking selected row.")
                o(jQuery("#" + tab._copiedId).text()).equals("")("Checking copied data.")

                def f3():
                    expected = tab.table._stringify(self._History_Data[1])
                    actual = jQuery("#" + tab._detailsId).text()
                    o(actual).equals(expected)("Checking selected row.")
                    o(jQuery("#" + tab._copiedId).text()).equals("")("Checking copied data.")
                    done()

                self._clickRow(1, f3)

            self._clickRow(0, f2)

        self._setData(f1)

    # ============================================== #

    def asyncDetailsCopy(self, done, timeout):
        """
        Tests detail copy.

            Parameters:
            done - Automatically included promise done function
            timeout - Automatically included timeout
        """
        timeout(400)

        def f1():
            def f2():
                tab = self.tabs.currentTab()

                def f3():
                    expected = tab.table._stringify(self._History_Data[0])
                    o(jQuery("#" + tab._detailsId).text()).equals(expected)("Checking selected row.")
                    o(jQuery("#" + tab._copiedId).text()).equals(expected)("Checking copied data.")

                    def f4():
                        o(jQuery("#" + tab._detailsId).text()).equals(expected)("Checking selected row.")
                        o(jQuery("#" + tab._copiedId).text()).equals("")("Checking copied data.")
                        done()

                    self._clickId(tab._clearButtonId, f4)

                self._clickId(tab._copyButtonId, f3)

            self._clickRow(0, f2)

        self._setData(f1)

    # ============================================== #

    def asyncRowLimit(self, done):
        """
        Tests limiting rows.

            Parameters:
            done - Automatically included promise done function
        """
        table = self.tabs.currentTab().table

        def f1():
            history = self.tabs.tabs[0]
            rows = history._getRows()
            o(rows.length).equals(table.max_size + 1)("Checking number of rows.")
            o(rows.last().find("td").text()).equals(table._limitText())("Check last row.")
            o(history._getLabel().text()).equals("{0}/{1}".format(table.max_size, table.total))("Check label format.")
            done()

        table.max_size = 50
        temp = table._makeDummyData(table.max_size * 2)

        data = []
        for entry in temp:
            new = {"history":
                    {
                       "id": entry["did"],
                        "changed": entry["changed"],
                        "signer": entry["signer"],
                        "signers": entry["signers"]
                    },
                   "signatures": entry["signatures"]
                  }
            data.append(new)

        table._setData(data)
        self._redraw(f1)

# ================================================== #
#                        EOF                         #
# ================================================== #