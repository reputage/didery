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

import components.tabs as tabs

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
        self.tabs = [tabs.Relays(), tabs.Errors()]

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
                   m("a.item.tab",
                     m("span.menu-item-text", "Server Status"),
                     m("i.chart.bar.icon"),
                     m("div.ui.label.small.menu-item-number", "0/0")),
                   m("a.item.tab",
                     m("span.menu-item-text", "Public Keys"),
                     m("i.key.icon"),
                     m("div.ui.label.small.menu-item-number", "0/0")),
                   m("a.item.tab",
                     m("span.menu-item-text", "Encrypted Blobs"),
                     m("i.unlock.alternate.icon"),
                     m("div.ui.label.small.menu-item-number", "0/0")),
                   menu_items,
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