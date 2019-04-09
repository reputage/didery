const router = {
    /*
     * Class for routing between urls and pages.
     */
    route: function(root=null) {
        /*
         * Sets up project routes.
         *
         *  Parameters:
         *      root - DOM for root page
         */
        let view = DashboardManager.view;

        if(root === null) {
            root = document.body;
        }

        m.route(
            root,
            "/dashboard",
            {"/dashboard": {"render": view}}
        );

    }
};