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
						Active: true,
						get setup_table () {return __get__ (this, function (self) {
							self.table = tables.ErrorsTable ();
						});}
					});
					__pragma__ ('<use>' +
						'components.tabledtab' +
						'components.tables' +
					'</use>')
					__pragma__ ('<all>')
						__all__.Errors = Errors;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
