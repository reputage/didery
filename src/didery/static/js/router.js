const router = {
    route: function(root=null) {
        let view = Manager.view;

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