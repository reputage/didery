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

import didery.static.transcrypt.components.tabs as tabs
import didery.static.transcrypt.components.searcher as searcher

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class Manager:
    """
    Class for managing all displayed tabs.
    """

    def __init__(self):
        """
        Initialize Tabs object. Load in all tabs and setup
        document level functions.
        """
        self.tabs = [tabs.History(), tabs.Blobs(), tabs.Relays(), tabs.Errors()]
        self._searchId = "search-input"
        self.searcher = searcher.Searcher()
        self._refreshing = False
        self._refreshPromise = None

        jQuery(document).ready(lambda: jQuery('.menu > a.item').tab())

        self.refresh()

    # ============================================== #

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

    # ============================================== #

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

    # ============================================== #

    def searchAll(self):
        """
        Initiates searching across all tabs based on current search string.
        """
        text = jQuery("#" + self._searchId).val()
        self.searcher.setSearch(text)

        for tab in self.tabs:
            tab.table.setFilter(self.searcher.search)

    # ============================================== #

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
                   m("a.item.tab.hide",
                     m("span.menu-item-text", "Server Status"),
                     m("i.chart.bar.icon"),
                     m("div.ui.label.small.menu-item-number", "0/0")),
                   menu_items,
                   m("div.right.menu",
                     m("div.item",
                       m("form", {"onsubmit": self.searchAll},
                         m("div#search.ui.transparent.icon.input",
                           m("input[type=text][placeholder=Search...]", {"id": self._searchId}),
                           m("button.ui.icon.button[type=submit]",
                             m("i.search.link.icon"))))))),
                 tab_items)

# ================================================== #
#                        EOF                         #
# ================================================== #