	__nest__ (
		__all__,
		'components.tabledtab', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var __name__ = 'components.tabledtab';
					var tab =  __init__ (__world__.components.tab);
					var TabledTab = __class__ ('TabledTab', [tab.Tab], {
						__module__: __name__,
						get __init__ () {return __get__ (this, function (self) {
							__super__ (TabledTab, '__init__') (self);
							self.table = null;
							self.setup_table ();
							self.copiedDetails = '';
							self._detailsId = self.DataTab + 'DetailsCodeBlock';
							self._copiedId = self.DataTab + 'CopiedCodeBlock';
							self._copyButtonId = self.DataTab + 'CopyButton';
							self._clearButtonId = self.DataTab + 'ClearButton';
						});},
						get setup_table () {return __get__ (this, function (self) {
							self.table = Table (list ([]));
						});},
						get _copyDetails () {return __get__ (this, function (self) {
							self.copiedDetails = self.table.detailSelected;
						});},
						get _getRows () {return __get__ (this, function (self) {
							return jQuery ("[data-tab='{0}'].tab table > tbody > tr".format (self.DataTab));
						});},
						get _getLabel () {return __get__ (this, function (self) {
							return jQuery (".menu a[data-tab='{0}'] .ui.label".format (self.DataTab));
						});},
						get _clearCopy () {return __get__ (this, function (self) {
							self.copiedDetails = '';
						});},
						get menu_item () {return __get__ (this, function (self) {
							return m (self._menu, self._menu_attrs, m ('div.menu-item-text', self.Name), m (self.Icon), m ('div.ui.label.small.menu-item-number', '{0}/{1}'.format (self.table.shown, self.table.total)));
						});},
						get main_view () {return __get__ (this, function (self) {
							return m ('div', m ('div.table-container', m (self.table.view)), m ('div.ui.hidden.divider'), m ('div.ui.two.cards', dict ({'style': 'height: 45%;'}), m ('div.ui.card', m ('div.content.small-header', m ('div.header', m ('span', 'Details'), m ('span.ui.mini.right.floated.button', dict ({'onclick': self._copyDetails, 'id': self._copyButtonId}), 'Copy'))), m ('pre.content.code-block', dict ({'id': self._detailsId}), self.table.detailSelected)), m ('div.ui.card', m ('div.content.small-header', m ('div.header', m ('span', 'Copied'), m ('span.ui.mini.right.floated.button', dict ({'onclick': self._clearCopy, 'id': self._clearButtonId}), 'Clear'))), m ('pre.content.code-block', dict ({'id': self._copiedId}), self.copiedDetails))));
						});}
					});
					__pragma__ ('<use>' +
						'components.tab' +
					'</use>')
					__pragma__ ('<all>')
						__all__.TabledTab = TabledTab;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
