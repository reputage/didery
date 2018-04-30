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
    Name = ""
    Data_tab = ""
    Active = False

    def __init__(self):
        self._menu_attrs = {"data-tab": self.Data_tab}
        self._tab_attrs = {"data-tab": self.Data_tab}
        self._menu = "a.item"
        self._tab = "div.ui.bottom.attached.tab.segment"

        if self.Active:
            self._menu += ".active"
            self._tab += ".active"

    # ============================================== #

    def menu_item(self):
        return m(self._menu, self._menu_attrs, self.Name)

    # ============================================== #

    def tab_item(self):
        return m(self._tab, self._tab_attrs, self.main_view())

    # ============================================== #

    def main_view(self):
        return m("div", "hello " + self.Name)

# ================================================== #
#                        EOF                         #
# ================================================== #