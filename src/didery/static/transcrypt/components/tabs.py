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

class Relays(tabledtab.TabledTab):
    """
    Class for relays tab.
    """
    Name = "Relays"
    Icon = "i.server.icon"
    DataTab = "relays"
    Active = False

    def setup_table(self):
        """
        Sets up relays table.
        """
        self.table = tables.RelaysTable()

# ================================================== #

class Blobs(tabledtab.TabledTab):
    """
   Class for encrypted blobs tab.
    """
    Name = "Encrypted Blobs"
    Icon = "i.unlock.alternate.icon"
    DataTab = "blobs"
    Active = False

    def setup_table(self):
        """
        Sets up blob table.
        """
        self.table = tables.BlobsTable()

# ================================================== #

# ================================================== #
#                        EOF                         #
# ================================================== #