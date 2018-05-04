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

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class Tab:
    """
    Base class for tabs, including menu link and displayed tab itself.
    """
    Name = ""
    Data_tab = ""
    Active = False

    def __init__(self):
        """
        Initialize Tab object. Load base attributes and markup.
        """
        self._menu_attrs = {"data-tab": self.Data_tab}
        self._tab_attrs = {"data-tab": self.Data_tab}
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

class Tabs:
    """
    Class for managing all displayed tabs.
    """

    def __init__(self):
        """
        Initialize Tabs object. Load in all tabs and setup
        document level functions.
        """
        self.tabs = []

        jQuery(document).ready(lambda: jQuery('.menu > a.item').tab())

    def currentTab(self):
        """
        Returns current tab.
        """
        active = jQuery(".menu a.item.active")
        data_tab = active.attr("data-tab")
        for tab in self.tabs:
            if tab.Data_tab == data_tab:
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
                   m("p", "Content Will be visible here.")))

# ================================================== #
#                        EOF                         #
# ================================================== #