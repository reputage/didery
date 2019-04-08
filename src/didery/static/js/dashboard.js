Manager = {
    tabs: [tabs.History(), tabs.Blobs(), tabs.Relays(), tabs.Errors()],
    _searchId: "search-input",
    searcher: searcher.Searcher(),
    _refreshing: false,
    _refreshPromise: null,

    refresh: function () {

    },

    currentTab: function () {

    },

    searchAll: function (){

    },

    view: function () {
        // Return markup for view
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