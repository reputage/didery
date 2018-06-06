# ================================================== #
#                     TABLED TAB                     #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/08/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

import didery.static.transcrypt.components.tab as tab

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class TabledTab(tab.Tab):
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
                 m("div.ui.label.small.menu-item-number", "{0}/{1}".format(self.table.shown, self.table.total))
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
#                        EOF                         #
# ================================================== #