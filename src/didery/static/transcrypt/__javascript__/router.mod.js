	__nest__ (
		__all__,
		'router', {
			__all__: {
				__inited__: false,
				__init__: function (__all__) {
					var dashboard = {};
					var __name__ = 'router';
					__nest__ (dashboard, '', __init__ (__world__.dashboard));
					var Router = __class__ ('Router', [object], {
						__module__: __name__,
						get __init__ () {return __get__ (this, function (self) {
							self.tabs = dashboard.Tabs ();
						});},
						get route () {return __get__ (this, function (self, root) {
							if (typeof root == 'undefined' || (root != null && root .hasOwnProperty ("__kwargtrans__"))) {;
								var root = null;
							};
							if (root === null) {
								var root = document.body;
							}
							m.route (root, '/dashboard', dict ({'/dashboard': dict ({'render': self.tabs.view})}));
						});}
					});
					__pragma__ ('<use>' +
						'dashboard' +
					'</use>')
					__pragma__ ('<all>')
						__all__.Router = Router;
						__all__.__name__ = __name__;
					__pragma__ ('</all>')
				}
			}
		}
	);
