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

import dashboard

# ================================================== #
#                  CLASS DEFINITIONS                 #
# ================================================== #

class Router:
    def __init__(self):
        self.tabs = dashboard.Tabs()

    # ============================================== #

    def route(self, root=None):
        if root is None:
            root = document.body
        m.route(root, "/dashboard",
            {
                "/dashboard": {"render": self.tabs.view}
            })

# ================================================== #
#                        EOF                         #
# ================================================== #