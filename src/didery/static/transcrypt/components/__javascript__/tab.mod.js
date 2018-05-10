	__nest__ (
		__all__,
		'components.tab', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var __name__ = 'components.tab';
					var Tab = __class__ ('Tab', [object], {
						__module__: __name__,
						Name: '',
						Icon: '',
						DataTab: '',
						Active: false,
						get __init__ () {return __get__ (this, function (self) {
							self._menu_attrs = dict ({'data-tab': self.DataTab});
							self._tab_attrs = dict ({'data-tab': self.DataTab});
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
					__pragma__ ('<all>')
						__all__.Tab = Tab;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
