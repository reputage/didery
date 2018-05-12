	__nest__ (
		__all__,
		'server', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var __name__ = 'server';
					var DEFAULT_INTERVAL = 1000;
					var request = function (path) {
						var kwargs = dict ();
						if (arguments.length) {
							var __ilastarg0__ = arguments.length - 1;
							if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
								var __allkwargs0__ = arguments [__ilastarg0__--];
								for (var __attrib0__ in __allkwargs0__) {
									switch (__attrib0__) {
										case 'path': var path = __allkwargs0__ [__attrib0__]; break;
										default: kwargs [__attrib0__] = __allkwargs0__ [__attrib0__];
									}
								}
								delete kwargs.__kwargtrans__;
							}
						}
						else {
						}
						path += '?';
						for (var [key, value] of kwargs.py_items ()) {
							path += ((key + '=') + str (value)) + '&';
						}
						var path = path.__getslice__ (0, -(1), 1);
						return m.request (path);
					};
					var onlyOne = function (func, interval) {
						if (typeof interval == 'undefined' || (interval != null && interval .hasOwnProperty ("__kwargtrans__"))) {;
							var interval = 1000;
						};
						if (arguments.length) {
							var __ilastarg0__ = arguments.length - 1;
							if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
								var __allkwargs0__ = arguments [__ilastarg0__--];
								for (var __attrib0__ in __allkwargs0__) {
									switch (__attrib0__) {
										case 'func': var func = __allkwargs0__ [__attrib0__]; break;
										case 'interval': var interval = __allkwargs0__ [__attrib0__]; break;
									}
								}
							}
						}
						else {
						}
						var scope = dict ({'promise': null, 'lastCalled': 0});
						var wrap = function () {
							if (arguments.length) {
								var __ilastarg0__ = arguments.length - 1;
								if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
									var __allkwargs0__ = arguments [__ilastarg0__--];
									for (var __attrib0__ in __allkwargs0__) {
									}
								}
							}
							else {
							}
							var now = new Date ();
							if (scope.promise != null && now - scope.lastCalled < interval) {
								return scope.promise;
							}
							scope.lastCalled = now;
							var f = function (resolve, reject) {
								if (arguments.length) {
									var __ilastarg0__ = arguments.length - 1;
									if (arguments [__ilastarg0__] && arguments [__ilastarg0__].hasOwnProperty ("__kwargtrans__")) {
										var __allkwargs0__ = arguments [__ilastarg0__--];
										for (var __attrib0__ in __allkwargs0__) {
											switch (__attrib0__) {
												case 'resolve': var resolve = __allkwargs0__ [__attrib0__]; break;
												case 'reject': var reject = __allkwargs0__ [__attrib0__]; break;
											}
										}
									}
								}
								else {
								}
								var p = func ();
								p.then (resolve);
								p.catch (reject);
							};
							scope.promise = new Promise (f);
							return scope.promise;
						};
						return wrap;
					};
					var clearArray = function (a) {
						while (len (a)) {
							a.py_pop ();
						}
					};
					var Manager = __class__ ('Manager', [object], {
						__module__: __name__,
						get __init__ () {return __get__ (this, function (self) {
							self.errors = Errors ();
							self.history = History ();
							self.otpBlobs = OTPBlobs ();
							self.relays = Relays ();
						});}
					});
					var Errors = __class__ ('Errors', [object], {
						__module__: __name__,
						Refresh_Interval: DEFAULT_INTERVAL,
						get __init__ () {return __get__ (this, function (self) {
							self.errors = list ([]);
							self.refreshErrors = onlyOne (self._refreshErrors, __kwargtrans__ ({interval: self.Refresh_Interval}));
						});},
						get _refreshErrors () {return __get__ (this, function (self) {
							clearArray (self.errors);
							return request ('/errors').then (self._parseAll);
						});},
						get _parseAll () {return __get__ (this, function (self, data) {
							for (var error of data ['data']) {
								self.errors.append (error);
							}
						});}
					});
					var History = __class__ ('History', [object], {
						__module__: __name__,
						Refresh_Interval: DEFAULT_INTERVAL,
						get __init__ () {return __get__ (this, function (self) {
							self.history = list ([]);
							self.refreshHistory = onlyOne (self._refreshHistory, __kwargtrans__ ({interval: self.Refresh_Interval}));
						});},
						get _refreshHistory () {return __get__ (this, function (self) {
							clearArray (self.history);
							return request ('/history').then (self._parseAll);
						});},
						get _parseAll () {return __get__ (this, function (self, data) {
							for (var history of data ['data']) {
								self.history.append (history);
							}
						});}
					});
					var OTPBlobs = __class__ ('OTPBlobs', [object], {
						__module__: __name__,
						Refresh_Interval: DEFAULT_INTERVAL,
						get __init__ () {return __get__ (this, function (self) {
							self.blobs = list ([]);
							self.refreshBlobs = onlyOne (self._refreshBlobs, __kwargtrans__ ({interval: self.Refresh_Interval}));
						});},
						get _refreshBlobs () {return __get__ (this, function (self) {
							clearArray (self.blobs);
							return request ('/relay').then (self._parseAll);
						});},
						get _parseAll () {return __get__ (this, function (self, data) {
							for (var blob of data ['data']) {
								self.blobs.append (blob);
							}
						});}
					});
					var Relays = __class__ ('Relays', [object], {
						__module__: __name__,
						Refresh_Interval: DEFAULT_INTERVAL,
						get __init__ () {return __get__ (this, function (self) {
							self.relays = list ([]);
							self.refreshRelays = onlyOne (self._refreshRelays, __kwargtrans__ ({interval: self.Refresh_Interval}));
						});},
						get _refreshRelays () {return __get__ (this, function (self) {
							clearArray (self.relays);
							return request ('/relay').then (self._parseAll);
						});},
						get _parseAll () {return __get__ (this, function (self, data) {
							for (var relay of dict (data).py_items ()) {
								self.relays.append (relay [1]);
							}
						});}
					});
					var manager = Manager ();
					__pragma__ ('<all>')
						__all__.DEFAULT_INTERVAL = DEFAULT_INTERVAL;
						__all__.Errors = Errors;
						__all__.History = History;
						__all__.Manager = Manager;
						__all__.OTPBlobs = OTPBlobs;
						__all__.Relays = Relays;
						__all__.__name__ = __name__;
						__all__.clearArray = clearArray;
						__all__.manager = manager;
						__all__.onlyOne = onlyOne;
						__all__.request = request;
					__pragma__ ('</all>')
				}
			}
		}
	);
