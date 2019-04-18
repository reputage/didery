let m = require("mithril");
let Dashboard = require("./dashboard");
let DashboardManager = new Dashboard.DashboardManager();

module.exports = {
    Router: class Route {
        /*
         * Class for routing between urls and pages.
         */
        static route(root=null) {
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
                {"/dashboard": {"render": view.bind(DashboardManager)}}
            );

        }
    }
};