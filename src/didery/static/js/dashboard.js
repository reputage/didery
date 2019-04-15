DashboardManager = {
    tabs: [HistoryTab, BlobsTab, RelaysTab, ErrorsTab],
    _searchId: "search-input",
    searcher: searcher,
    _refreshing: false,
    _refreshPromise: null,

    refresh: function () {
        /*
         * Retrieves server data and populates our tabs and tables.
         */
        if(this._refreshing) {
            return this._refreshPromise;
        }
        this._refreshing = true;

        let promises = [];
        this.tabs.forEach(function(tab, index) {
            promises.append(tab.table.refresh());
        });

        let self = this;
        let done = function () {
            self._refreshing = false;
        };

        this._refreshPromise = Promise.all(promises);
        this._refreshPromise.then(done);
        this._refreshPromise.catch(done);
        return this._refreshPromise
    },

    currentTab: function () {
        /*
         * Returns current tab.
         */
        let active = $(".menu a.item.active");
        let data_tab = active.attr("data-tab");

        this.tabs.forEach(function (tab, index) {
            if(tab.DataTab === data_tab){
                return tab
            }
        });

        return null;
    },

    searchAll: function (){
        /*
         * Initiates searching across all tabs based on current search string.
         */
        let text = $("#" + this._searchId).val();
        this.searcher.setSearch(text);

        let self = this;
        this.tabs.forEach(function(tab, index) {
            tab.table.setFilter(self.searcher.search);
        });
    },

    view: function () {
        /*
         * Return markup for view
         */
        let menu_items = [];
        let tab_items = [];
        this.tabs.forEach(function (tab, index) {
            menu_items.append(tab.menu_item());
            tab_items.append(tab.tab_item());
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
                       m("form", {"onsubmit": this.searchAll},
                         m("div#search.ui.transparent.icon.input",
                           m("input[type=text][placeholder=Search...]", {"id": this._searchId}),
                           m("button.ui.icon.button[type=submit]",
                             m("i.search.link.icon"))))))),
                 tab_items)
    }
};