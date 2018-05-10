# ================================================== #
#                        TABS                        #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/08/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

import components.tabledtab as tabledtab
import components.tables as tables

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class Errors(tabledtab.TabledTab):
    """
    Class for errors tab.
    """
    Name = "Errors"
    Icon = "i.exclamation.circle.icon"
    DataTab = "errors"
    Active = True

    def setup_table(self):
        """
        Sets up errors table.
        """
        self.table = tables.ErrorsTable()

# ================================================== #
#                        EOF                         #
# ================================================== #