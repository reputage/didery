
module.exports = {
    Tab: class T {
        constructor() {
            /*
             * Initialize Tab object. Load base attributes and markup.
             */
            T.Name = "";
            T.Icon = "";
            T.DataTab = "";
            T.Active = false;

            this._menu_attrs = {"data-tab": T.DataTab};
            this._tab_attrs = {"data-tab": T.DataTab};
            this._menu = "a.item";
            this._tab = "div.ui.bottom.attached.tab.segment";

            if (T.Active) {
                this._menu += ".active";
                this._tab += ".active";
            }
        }

        menu_item() {
            /*
             * Returns menu item markup for given tab.
             */
            return m(this._menu, this._menu_attrs, T.Name);
        }

        tab_item() {
            /*
             * Returns tab item markup for given tab.
             */
            return m(this._tab, this._tab_attrs, this.main_view());
        }

        main_view() {
            /*
             * Returns main view markup for given tab.
             */
            return m("div", "hello " + T.Name);
        }
    },
};