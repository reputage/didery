# ================================================== #
#                      ROUTER                        #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 04/26/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

import didery.static.transcrypt.dashboard as dashboard

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class Router:
    """
    Class for routing between urls and pages.
    """
    def __init__(self):
        """
        Initialize Router object. Load navigation tabs.
        """
        self.tabs = dashboard.Manager()

    # ============================================== #

    def route(self, root=None):
        """
        Sets up project routes.

            Parameters:
            root - DOM for root page
        """
        if root is None:
            root = document.body
        m.route(root, "/dashboard",
            {
                "/dashboard": {"render": self.tabs.view}
            })

# ================================================== #
#                        EOF                         #
# ================================================== #