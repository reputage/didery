let m = require("mithril");


module.exports = {
    Tab: class T {
        constructor() {
            /*
             * Initialize Tab object. Load base attributes and markup.
             */
            this.Name = "";
            this.Icon = "";
            this.DataTab = "";
            this.Active = false;

            this._menu_attrs = {"data-tab": this.DataTab};
            this._tab_attrs = {"data-tab": this.DataTab};
            this._menu = "a.item";
            this._tab = "div.ui.bottom.attached.tab.segment";

            if (this.Active) {
                this._menu += ".active";
                this._tab += ".active";
            }
        }

        menu_item() {
            /*
             * Returns menu item markup for given tab.
             */
            return m(this._menu, this._menu_attrs, this.Name);
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
            return m("div", "hello " + this.Name);
        }
    },
};