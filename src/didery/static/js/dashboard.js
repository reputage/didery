let tabs = require("./components/tabs");
let search = require("./components/searcher");
let m = require("mithril");
require("jquery-ui-bundle");


let DashboardManager = class Dash {
    constructor() {
        this.tabs = [new tabs.HistoryTab(), new tabs.BlobsTab(), new tabs.RelaysTab(), new tabs.ErrorsTab()];
        this._searchId = "search-input";
        this.searcher = search.searcher;
        this._refreshing = false;
        this._refreshPromise;

        //this is currently not working. Need to figure out why.
        //tabs.js has onclick functions handling the tab change.
        $(document).ready(() => {$('div.tabular.menu').tabs()});

        this.refresh()
    }

    refresh () {
        /*
         * Retrieves server data and populates our tabs and tables.
         */
        if (this._refreshing) {
            return this._refreshPromise;
        }
        this._refreshing = true;

        let promises = [];
        this.tabs.forEach(function (tab, index) {
            promises.push(tab.table.refresh());
        });

        let self = this;
        let done = function () {
            self._refreshing = false;
        };

        this._refreshPromise = Promise.all(promises);
        this._refreshPromise.then(done);
        this._refreshPromise.catch(done);
        return this._refreshPromise
    }

    currentTab () {
        /*
         * Returns current tab.
         */
        let active = $(".menu a.item.active");
        let data_tab = active.attr("data-tab");

        this.tabs.forEach(function (tab, index) {
            if (tab.DataTab === data_tab) {
                return tab
            }
        });

        return null;
    }

    searchAll () {
        /*
         * Initiates searching across all tabs based on current search string.
         */
        let text = $("#" + this._searchId).val();
        this.searcher.setSearch(text);

        let self = this;
        this.tabs.forEach(function (tab, index) {
            tab.table.setFilter(self.searcher.search);
        });
    }

    view () {
        /*
         * Return markup for view
         */
        let menu_items = [];
        let tab_items = [];

        this.tabs.forEach(function (tab, index) {
            menu_items.push(tab.menu_item());
            tab_items.push(tab.tab_item());
        });

        return m("div",
            m("div.ui.top.attached.tabular.menu",
                m("a.item.tab.hide",
                    m("span.menu-item-text", "Server Status"),
                    m("i.chart.bar.icon"),
                    m("div.ui.label.small.menu-item-number", "0/0")),
                menu_items,
                m("div.right.menu",
                    m("div.item",
                        m("form", {"onsubmit": this.searchAll.bind(this)},
                            m("div#search.ui.transparent.icon.input",
                                m("input[type=text][placeholder=Search...]", {"id": this._searchId}),
                                m("button.ui.icon.button[type=submit]",
                                    m("i.search.link.icon"))))))),
            tab_items)
    }
};

module.exports = {
    "DashboardManager": DashboardManager,
};