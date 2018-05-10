	__nest__ (
		__all__,
		'components.fields', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var __name__ = 'components.fields';
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
					__pragma__ ('<all>')
						__all__.DIDField = DIDField;
						__all__.DateField = DateField;
						__all__.EpochField = EpochField;
						__all__.Field = Field;
						__all__.FillField = FillField;
						__all__.IDField = IDField;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
