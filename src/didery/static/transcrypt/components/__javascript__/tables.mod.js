	__nest__ (
		__all__,
		'components.tables', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var server = {};
					var __name__ = 'components.tables';
					__nest__ (server, '', __init__ (__world__.server));
					var field =  __init__ (__world__.components.fields);
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
							var fields = list ([field.FillField ('Title'), field.FillField ('Message'), field.DateField ('Time')]);
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
					var RelaysTable = __class__ ('RelaysTable', [Table], {
						__module__: __name__,
						get __init__ () {return __get__ (this, function (self) {
							var fields = list ([field.FillField ('Host'), field.FillField ('Port'), field.FillField ('Name'), field.FillField ('Main'), field.IDField ('UID'), field.FillField ('Status')]);
							__super__ (RelaysTable, '__init__') (self, fields);
						});},
						get refresh () {return __get__ (this, function (self) {
							self.py_clear ();
							var relays = server.manager.relays;
							return relays.refreshRelays ().then ((function __lambda__ () {
								return self._setData (relays.relays);
							}));
						});},
						get _getField () {return __get__ (this, function (self, obj, field) {
							if (field.py_name == 'host') {
								return obj ['host address'];
							}
							else if (field.py_name == 'port') {
								return obj ['port'];
							}
							else if (field.py_name == 'name') {
								return obj ['name'];
							}
							else if (field.py_name == 'main') {
								return obj ['main'];
							}
							else if (field.py_name == 'uid') {
								return obj ['uid'];
							}
							else if (field.py_name == 'status') {
								return obj ['status'];
							}
						});}
					});
					__pragma__ ('<use>' +
						'components.fields' +
						'server' +
					'</use>')
					__pragma__ ('<all>')
						__all__.ErrorsTable = ErrorsTable;
						__all__.RelaysTable = RelaysTable;
						__all__.Table = Table;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
