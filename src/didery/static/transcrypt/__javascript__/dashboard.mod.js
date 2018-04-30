	__nest__ (
		__all__,
		'dashboard', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var __name__ = 'dashboard';
					var Tab = __class__ ('Tab', [object], {
						__module__: __name__,
						Name: '',
						Data_tab: '',
						Active: false,
						get __init__ () {return __get__ (this, function (self) {
							self._menu_attrs = dict ({'data-tab': self.Data_tab});
							self._tab_attrs = dict ({'data-tab': self.Data_tab});
							self._menu = 'a.item';
							self._tab = 'div.ui.bottom.attached.tab.segment';
							if (self.Active) {
								self._menu += '.active';
								self._tab += '.active';
							}
						});},
						get menu_item () {return __get__ (this, function (self) {
							return m (self._menu, self._menu_attrs, self.Name);
						});},
						get tab_item () {return __get__ (this, function (self) {
							return m (self._tab, self._tab_attrs, self.main_view ());
						});},
						get main_view () {return __get__ (this, function (self) {
							return m ('div', 'hello ' + self.Name);
						});}
					});
					var Tabs = __class__ ('Tabs', [object], {
						__module__: __name__,
						get __init__ () {return __get__ (this, function (self) {
							self.tabs = list ([]);
							jQuery (document).ready ((function __lambda__ () {
								return jQuery ('.menu > a.item').tab ();
							}));
						});},
						get currentTab () {return __get__ (this, function (self) {
							var active = jQuery ('.menu a.item.active');
							var data_tab = active.attr ('data-tab');
							var __iterable0__ = self.tabs;
							for (var __index0__ = 0; __index0__ < len (__iterable0__); __index0__++) {
								var tab = __iterable0__ [__index0__];
								if (tab.Data_tab == data_tab) {
									return tab;
								}
							}
							return null;
						});},
						get view () {return __get__ (this, function (self) {
							var menu_items = list ([]);
							var tab_items = list ([]);
							var __iterable0__ = self.tabs;
							for (var __index0__ = 0; __index0__ < len (__iterable0__); __index0__++) {
								var tab = __iterable0__ [__index0__];
								menu_items.append (tab.menu_item ());
								tab_items.append (tab.tab_item ());
							}
							return m ('div.ui.top.attached.tabular.menu', m ('a.active.item', m ('span.menu-item-text', 'Server Status'), m ('i.chart.bar.icon')), m ('a.item', m ('span.menu-item-text', 'Public Keys'), m ('i.key.icon')), m ('a.item', m ('span.menu-item-text', 'Encrypted Blobs'), m ('i.unlock.alternate.icon')), m ('a.item', m ('span.menu-item-text', 'Relay Servers'), m ('i.server.icon')), m ('a.item', m ('span.menu-item-text', 'Error Logs'), m ('i.exclamation.circle.icon')), m ('div.right.menu', m ('div.item', m ('div#search.ui.transparent.icon.input', m ('input[type=text][placeholder=Search...]'), m ('i.search.link.icon')))));
						});}
					});
					__pragma__ ('<all>')
						__all__.Tab = Tab;
						__all__.Tabs = Tabs;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
