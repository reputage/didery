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

            this._menu_attrs = {"data-tab": this.DataTab, "onclick":this._changeTab.bind(this)};
            this._tab_attrs = {"data-tab": this.DataTab};
            this._menu = "a.item";
            this._tab = "div.ui.bottom.attached.tab.segment";

            if (this.Active) {
                this._menu += ".active";
                this._tab += ".active";
            }
        }

        _changeTab(event) {
            /*
             * Changes the displayed tab
             */
            let active_tab = $(".menu a.item.active");
            let active_name = active_tab.attr('data-tab');
            let active_table = $(`div[data-tab='${active_name}']`);
            active_tab.removeClass('active');
            active_table.removeClass('active');
            active_tab.trigger("cssClassChange");

            let clicked_tab = $(event.currentTarget);
            let clicked_name = clicked_tab.attr('data-tab');
            let clicked_table = $(`div[data-tab='${clicked_name}']`);
            clicked_tab.addClass('active');
            clicked_table.addClass('active');
            this.Active = true;
        }

        _removeActive(event) {
            if(!$(event.currentTarget).hasClass('active') && this.Active){
                this.Active = false;
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