	__nest__ (
		__all__,
		'dashboard', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var __name__ = 'dashboard';
					var tabs =  __init__ (__world__.components.tabs);
					var searcher =  __init__ (__world__.components.searcher);
					var Manager = __class__ ('Manager', [object], {
						__module__: __name__,
						get __init__ () {return __get__ (this, function (self) {
							self.tabs = list ([tabs.History (), tabs.Blobs (), tabs.Relays (), tabs.Errors ()]);
							self._searchId = 'search-input';
							self.searcher = searcher.Searcher ();
							self._refreshing = false;
							self._refreshPromise = null;
							jQuery (document).ready ((function __lambda__ () {
								return jQuery ('.menu > a.item').tab ();
							}));
							self.refresh ();
						});},
						get refresh () {return __get__ (this, function (self) {
							if (self._refreshing) {
								return self._refreshPromise;
							}
							self._refreshing = true;
							var promises = list ([]);
							for (var tab of self.tabs) {
								promises.append (tab.table.refresh ());
							}
							var done = function () {
								self._refreshing = false;
							};
							self._refreshPromise = Promise.all (promises);
							self._refreshPromise.then (done);
							self._refreshPromise.catch (done);
							return self._refreshPromise;
						});},
						get currentTab () {return __get__ (this, function (self) {
							var active = jQuery ('.menu a.item.active');
							var data_tab = active.attr ('data-tab');
							for (var tab of self.tabs) {
								if (tab.DataTab == data_tab) {
									return tab;
								}
							}
							return null;
						});},
						get searchAll () {return __get__ (this, function (self) {
							var text = jQuery ('#' + self._searchId).val ();
							self.searcher.setSearch (text);
							print ('ALL: ' + text);
							for (var tab of self.tabs) {
								tab.table.setFilter (self.searcher.search);
							}
						});},
						get view () {return __get__ (this, function (self) {
							var menu_items = list ([]);
							var tab_items = list ([]);
							for (var tab of self.tabs) {
								menu_items.append (tab.menu_item ());
								tab_items.append (tab.tab_item ());
							}
							return m ('div', m ('div.ui.top.attached.tabular.menu', m ('a.item.tab', m ('span.menu-item-text', 'Server Status'), m ('i.chart.bar.icon'), m ('div.ui.label.small.menu-item-number', '0/0')), menu_items, m ('div.right.menu', m ('div.item', m ('form', dict ({'onsubmit': self.searchAll}), m ('div#search.ui.transparent.icon.input', m ('input[type=text][placeholder=Search...]', dict ({'id': self._searchId})), m ('button.ui.icon.button[type=submit]', m ('i.search.link.icon'))))))), tab_items);
						});}
					});
					__pragma__ ('<use>' +
						'components.searcher' +
						'components.tabs' +
					'</use>')
					__pragma__ ('<all>')
						__all__.Manager = Manager;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
