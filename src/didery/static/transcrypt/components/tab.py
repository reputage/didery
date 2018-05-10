# ================================================== #
#                         TAB                        #
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
#                        EOF                         #
# ================================================== #