	__nest__ (
		__all__,
		'dashboard', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var server = {};
					var __name__ = 'dashboard';
					__nest__ (server, '', __init__ (__world__.server));
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
					var TabledTab = __class__ ('TabledTab', [Tab], {
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
							return m (self._menu, self._menu_attrs, m ('div.menu-item-text', self.Name), m (self.Icon), m ('div.ui.label.small', '{0}/{1}'.format (self.table.shown, self.table.total)));
						});},
						get main_view () {return __get__ (this, function (self) {
							return m ('div', m ('div.table-container', m (self.table.view)), m ('div.ui.hidden.divider'), m ('div.ui.two.cards', dict ({'style': 'height: 45%;'}), m ('div.ui.card', m ('div.content.small-header', m ('div.header', m ('span', 'Details'), m ('span.ui.mini.right.floated.button', dict ({'onclick': self._copyDetails, 'id': self._copyButtonId}), 'Copy'))), m ('pre.content.code-block', dict ({'id': self._detailsId}), self.table.detailSelected)), m ('div.ui.card', m ('div.content.small-header', m ('div.header', m ('span', 'Copied'), m ('span.ui.mini.right.floated.button', dict ({'onclick': self._clearCopy, 'id': self._clearButtonId}), 'Clear'))), m ('pre.content.code-block', dict ({'id': self._copiedId}), self.copiedDetails))));
						});}
					});
					var Field = __class__ ('Field', [object], {
						__module__: __name__,
						Title: null,
						Length: 4,
						get __init__ () {return __get__ (this, function (self, title, length) {
							if (typeof title == 'undefined' || (title != null && title .hasOwnProperty ("__kwargtrans__"))) {;
								var title = null;
							};
							if (typeof length == 'undefined' || (length != null && length .hasOwnProperty ("__kwargtrans__"))) {;
								var length = null;
							};
							if (arguments.length) {
								var __ilastarg0__ = arguments.length - 1;
								if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
									var __allkwargs0__ = arguments [__ilastarg0__--];
									for (var __attrib0__ in __allkwargs0__) {
										switch (__attrib0__) {
											case 'self': var self = __allkwargs0__ [__attrib0__]; break;
											case 'title': var title = __allkwargs0__ [__attrib0__]; break;
											case 'length': var length = __allkwargs0__ [__attrib0__]; break;
										}
									}
								}
							}
							else {
							}
							self.title = self.Title;
							if (title !== null) {
								self.title = title;
							}
							self.mlength = self.Length;
							if (length !== null) {
								self.mlength = length;
							}
							self.py_name = self.title.lower ();
						});},
						get format () {return __get__ (this, function (self, data) {
							return str (data);
						});},
						get shorten () {return __get__ (this, function (self, string) {
							return string;
						});},
						get view () {return __get__ (this, function (self, data) {
							if (data == null) {
								var data = '';
							}
							var formatted = self.format (data);
							return m ('td', dict ({'title': formatted}), self.shorten (formatted));
						});}
					});
					var FillField = __class__ ('FillField', [Field], {
						__module__: __name__,
						Length: 100,
						get view () {return __get__ (this, function (self, data) {
							var node = __super__ (FillField, 'view') (self, data);
							node.attrs ['class'] = 'fill-space';
							return node;
						});}
					});
					var DateField = __class__ ('DateField', [Field], {
						__module__: __name__,
						Length: 12,
						Title: 'Date'
					});
					var EpochField = __class__ ('EpochField', [DateField], {
						__module__: __name__,
						get format () {return __get__ (this, function (self, data) {
							var data = new Date (data / 1000).toISOString ();
							return __super__ (EpochField, 'format') (self, data);
						});}
					});
					var IDField = __class__ ('IDField', [Field], {
						__module__: __name__,
						Length: 4,
						Title: 'UID',
						Header: '',
						get format () {return __get__ (this, function (self, string) {
							if (string.startswith (self.Header)) {
								var string = string.__getslice__ (len (self.Header), null, 1);
							}
							return __super__ (IDField, 'format') (self, string);
						});}
					});
					var DIDField = __class__ ('DIDField', [IDField], {
						__module__: __name__,
						Header: 'did:dad:',
						Title: 'DID'
					});
					var Table = __class__ ('Table', [object], {
						__module__: __name__,
						no_results_text: 'No results found.',
						get __init__ () {return __get__ (this, function (self, fields) {
							self.max_size = 1000;
							self.fields = fields;
							self.data = list ([]);
							self._shownData = list ([]);
							self.view = dict ({'view': self._view});
							self._selected = null;
							self.detailSelected = '';
							self.filter = null;
							self.sortField = null;
							self.py_reversed = false;
							self.total = 0;
							self.shown = 0;
						});},
						get _stringify () {return __get__ (this, function (self, obj) {
							var replacer = function (key, value) {
								if (key.startswith ('_')) {
									return ;
								}
								return value;
							};
							return JSON.stringify (obj, replacer, 2);
						});},
						get _limitText () {return __get__ (this, function (self) {
							return 'Limited to {} results.'.format (self.max_size);
						});},
						get _selectRow () {return __get__ (this, function (self, event, obj) {
							if (self._selected !== null) {
								delete self._selected._selected;
								if (self._selected._uid == obj._uid) {
									self._selected = null;
									self.detailSelected = '';
									return ;
								}
							}
							self._selected = obj;
							obj._selected = true;
							self.detailSelected = self._stringify (obj);
						});},
						get refresh () {return __get__ (this, function (self) {
							self._setData (list ([]));
							var p = new Promise ((function __lambda__ (resolve) {
								return resolve ();
							}));
							return Promise;
						});},
						get py_clear () {return __get__ (this, function (self) {
							self.total = 0;
							server.clearArray (self.data);
						});},
						get _makeDummyData () {return __get__ (this, function (self, count) {
							var data = list ([]);
							for (var i = 0; i < count; i++) {
								var obj = dict ({});
								for (var field of self.fields) {
									obj [field.py_name] = 'test{0} {1}'.format (i, field.py_name);
								}
								data.append (obj);
							}
							return data;
						});},
						get _setData () {return __get__ (this, function (self, data, py_clear) {
							if (typeof py_clear == 'undefined' || (py_clear != null && py_clear .hasOwnProperty ("__kwargtrans__"))) {;
								var py_clear = true;
							};
							if (arguments.length) {
								var __ilastarg0__ = arguments.length - 1;
								if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
									var __allkwargs0__ = arguments [__ilastarg0__--];
									for (var __attrib0__ in __allkwargs0__) {
										switch (__attrib0__) {
											case 'self': var self = __allkwargs0__ [__attrib0__]; break;
											case 'data': var data = __allkwargs0__ [__attrib0__]; break;
											case 'py_clear': var py_clear = __allkwargs0__ [__attrib0__]; break;
										}
									}
								}
							}
							else {
							}
							if (py_clear) {
								self.py_clear ();
							}
							for (var datum of data) {
								datum._uid = self.total;
								self.data.append (datum);
								self.total++;
							}
							self._processData ();
						});},
						get setFilter () {return __get__ (this, function (self, func) {
							if (func != self.filter) {
								self.filter = func;
								self._processData ();
							}
						});},
						get setSort () {return __get__ (this, function (self, field) {
							if (self.sortField == field) {
								self.py_reversed = !(self.py_reversed);
							}
							else {
								self.py_reversed = false;
								self.sortField = field;
							}
							self._sortData ();
						});},
						get _sortData () {return __get__ (this, function (self) {
							if (self.sortField === null) {
								return ;
							}
							self._shownData.py_sort (__kwargtrans__ ({key: (function __lambda__ (obj) {
								return self._getField (obj, self.sortField);
							}), reverse: self.py_reversed}));
						});},
						get _processData () {return __get__ (this, function (self) {
							server.clearArray (self._shownData);
							self.shown = 0;
							for (var obj of self.data) {
								if (self.shown >= self.max_size) {
									break;
								}
								if (self.filter !== null) {
									if (!(self.filter (obj))) {
										continue;
									}
								}
								self._shownData.append (obj);
								self.shown++;
							}
							self._sortData ();
						});},
						get _getField () {return __get__ (this, function (self, obj, field) {
							return obj [field.py_name];
						});},
						get _makeRow () {return __get__ (this, function (self, obj) {
							return (function () {
								var __accu0__ = [];
								for (var field of self.fields) {
									__accu0__.append (field.view (self._getField (obj, field)));
								}
								return __accu0__;
							}) ();
						});},
						get _view () {return __get__ (this, function (self) {
							var headers = list ([]);
							for (var field of self.fields) {
								var makeScope = function (f) {
									return (function __lambda__ (event) {
										return self.setSort (f);
									});
								};
								if (field == self.sortField) {
									if (self.py_reversed) {
										var icon = m ('i.arrow.down.icon');
									}
									else {
										var icon = m ('i.arrow.up.icon');
									}
									var header = m ('th.ui.right.labeled.icon', dict ({'onclick': makeScope (field)}), icon, field.title);
								}
								else {
									var header = m ('th', dict ({'onclick': makeScope (field)}), field.title);
								}
								headers.append (header);
							}
							var rows = list ([]);
							for (var obj of self._shownData) {
								var row = self._makeRow (obj);
								var makeScope = function (o) {
									return (function __lambda__ (event) {
										return self._selectRow (event, o);
									});
								};
								if (obj._selected) {
									rows.append (m ('tr.active', dict ({'onclick': makeScope (obj)}), row));
								}
								else {
									rows.append (m ('tr', dict ({'onclick': makeScope (obj)}), row));
								}
							}
							if (self.shown >= self.max_size) {
								rows.append (m ('tr', m ('td', self._limitText ())));
							}
							if (!(self.shown)) {
								rows.append (m ('tr', m ('td', self.no_results_text)));
							}
							return m ('table', dict ({'class': 'ui selectable celled unstackable single line left aligned table'}), m ('thead', m ('tr', dict ({'class': 'center aligned'}), headers)), m ('tbody', rows));
						});}
					});
					var ErrorsTable = __class__ ('ErrorsTable', [Table], {
						__module__: __name__,
						get __init__ () {return __get__ (this, function (self) {
							var fields = list ([FillField ('Title'), FillField ('Message'), DateField ('Time')]);
							__super__ (ErrorsTable, '__init__') (self, fields);
						});},
						get refresh () {return __get__ (this, function (self) {
							self.py_clear ();
							var errors = server.manager.errors;
							return errors.refreshErrors ().then ((function __lambda__ () {
								return self._setData (errors.errors);
							}));
						});},
						get _getField () {return __get__ (this, function (self, obj, field) {
							if (field.py_name == 'title') {
								return obj.title;
							}
							else if (field.py_name == 'message') {
								return obj.msg;
							}
							else if (field.py_name == 'time') {
								return obj.time;
							}
						});}
					});
					var Errors = __class__ ('Errors', [TabledTab], {
						__module__: __name__,
						Name: 'Errors',
						Icon: 'i.chart.bar.icon',
						DataTab: 'errors',
						Active: true,
						get setup_table () {return __get__ (this, function (self) {
							self.table = ErrorsTable ();
						});}
					});
					var Tabs = __class__ ('Tabs', [object], {
						__module__: __name__,
						get __init__ () {return __get__ (this, function (self) {
							self.tabs = list ([Errors ()]);
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
						get view () {return __get__ (this, function (self) {
							var menu_items = list ([]);
							var tab_items = list ([]);
							for (var tab of self.tabs) {
								menu_items.append (tab.menu_item ());
								tab_items.append (tab.tab_item ());
							}
							return m ('div', m ('div.ui.top.attached.tabular.menu', menu_items, m ('a.item.tab', m ('span.menu-item-text', 'Public Keys'), m ('i.key.icon')), m ('a.item.tab', m ('span.menu-item-text', 'Encrypted Blobs'), m ('i.unlock.alternate.icon')), m ('a.item.tab', m ('span.menu-item-text', 'Relay Servers'), m ('i.server.icon')), m ('a.item.tab', m ('span.menu-item-text', 'Error Logs'), m ('i.exclamation.circle.icon')), m ('div.right.menu', m ('div.item', m ('div#search.ui.transparent.icon.input', m ('input[type=text][placeholder=Search...]'), m ('i.search.link.icon'))))), tab_items);
						});}
					});
					__pragma__ ('<use>' +
						'server' +
					'</use>')
					__pragma__ ('<all>')
						__all__.DIDField = DIDField;
						__all__.DateField = DateField;
						__all__.EpochField = EpochField;
						__all__.Errors = Errors;
						__all__.ErrorsTable = ErrorsTable;
						__all__.Field = Field;
						__all__.FillField = FillField;
						__all__.IDField = IDField;
						__all__.Tab = Tab;
						__all__.Table = Table;
						__all__.TabledTab = TabledTab;
						__all__.Tabs = Tabs;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
