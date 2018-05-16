	__nest__ (
		__all__,
		'components.tabs', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var __name__ = 'components.tabs';
					var tabledtab =  __init__ (__world__.components.tabledtab);
					var tables =  __init__ (__world__.components.tables);
					var Errors = __class__ ('Errors', [tabledtab.TabledTab], {
						__module__: __name__,
						Name: 'Errors',
						Icon: 'i.exclamation.circle.icon',
						DataTab: 'errors',
						Active: false,
						get setup_table () {return __get__ (this, function (self) {
							self.table = tables.ErrorsTable ();
						});}
					});
					var Relays = __class__ ('Relays', [tabledtab.TabledTab], {
						__module__: __name__,
						Name: 'Relays',
						Icon: 'i.server.icon',
						DataTab: 'relays',
						Active: false,
						get setup_table () {return __get__ (this, function (self) {
							self.table = tables.RelaysTable ();
						});}
					});
					var Blobs = __class__ ('Blobs', [tabledtab.TabledTab], {
						__module__: __name__,
						Name: 'Encrypted Blobs',
						Icon: 'i.unlock.alternate.icon',
						DataTab: 'blobs',
						Active: false,
						get setup_table () {return __get__ (this, function (self) {
							self.table = tables.BlobsTable ();
						});}
					});
					var History = __class__ ('History', [tabledtab.TabledTab], {
						__module__: __name__,
						Name: 'Public Keys',
						Icon: 'i.key.icon',
						DataTab: 'history',
						Active: true,
						get setup_table () {return __get__ (this, function (self) {
							self.table = tables.HistoryTable ();
						});}
					});
					__pragma__ ('<use>' +
						'components.tabledtab' +
						'components.tables' +
					'</use>')
					__pragma__ ('<all>')
						__all__.Blobs = Blobs;
						__all__.Errors = Errors;
						__all__.History = History;
						__all__.Relays = Relays;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
