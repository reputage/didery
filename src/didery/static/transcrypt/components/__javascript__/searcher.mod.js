	__nest__ (
		__all__,
		'components.searcher', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var __name__ = 'components.searcher';
					var Searcher = __class__ ('Searcher', [object], {
						__module__: __name__,
						get __init__ () {return __get__ (this, function (self) {
							self.searchTerm = null;
							self.caseSensitive = false;
						});},
						get setSearch () {return __get__ (this, function (self, term) {
							self.searchTerm = term || '';
							self.caseSensitive = self.searchTerm.startswith ('"') && self.searchTerm.endswith ('"');
							if (self.caseSensitive) {
								self.searchTerm = self.searchTerm.__getslice__ (1, -(1), 1);
							}
							else {
								self.searchTerm = self.searchTerm.lower ();
							}
						});},
						get _checkPrimitive () {return __get__ (this, function (self, item) {
							if (isinstance (item, str)) {
								if (!(self.caseSensitive)) {
									var item = item.lower ();
								}
								return __in__ (self.searchTerm, item);
							}
							return false;
						});},
						get _checkAny () {return __get__ (this, function (self, value) {
							if (isinstance (value, dict) || isinstance (value, Object)) {
								return self.search (value);
							}
							else if (isinstance (value, list)) {
								for (var item of value) {
									if (self._checkAny (item)) {
										return true;
									}
								}
								return false;
							}
							else {
								return self._checkPrimitive (value);
							}
						});},
						get search () {return __get__ (this, function (self, obj) {
							for (var key in obj) {
								if (key.startswith ('_')) {
									continue;
								}
								var value = obj [key];
								if (self._checkAny (value)) {
									return true;
								}
							}
							return false;
						});}
					});
					__pragma__ ('<all>')
						__all__.Searcher = Searcher;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
