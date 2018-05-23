# ================================================== #
#                       TESTER                       #
# ================================================== #
# Author: Brady Hammond                              #
# Created: 05/08/2018                                #
# Last Edited:                                       #
# Last Edited By:                                    #
# ================================================== #
#                      IMPORTS                       #
# ================================================== #

__pragma__ ('alias', 'Global', 'global')

jsdom = require('jsdom')
Global.window = __new__(jsdom.JSDOM()).window
Global.document = window.document
Global.XMLHttpRequest = window.XMLHttpRequest
Global.jQuery = require("jquery")
Global.m = require("mithril")
o = require("mithril/ospec/ospec")

# ================================================== #
#                     FUNCTIONS                      #
# ================================================== #

def test(Cls):
    """
    Runs tests.
    """
    class Wrapper:
        """
        Helper decorator for making test writing easier. Wrap around a
        class to treat the class as though o.spec were called on it. Treats
        any public methods as tests to be run through o(name, method).
        Methods or nested classes starting with an upper case are assumed
        to be nested test groups, and have test() called on them
        automatically. Special o methods (e.g. "beforeEach") are translated
        to the appropriate o call.
        """
        def __init__(self):
            original = Cls()

            def dospec():
                funcs = []

                __pragma__('jsiter')
                for key in original:
                    if key.startswith("_"):
                        continue

                    obj = original[key]

                    if key[0].isupper():
                        test(obj)
                        continue

                    if key.startswith("async"):
                        def makeScope(fun):
                            return lambda done, timeout: fun(done, timeout)
                        obj = makeScope(obj)
                        key = key[len("async"):]

                    if key in ["beforeEach", "BeforeEach"]:
                        o.beforeEach(obj)
                    elif key in ["before", "Before"]:
                        o.before(obj)
                    elif key in ["afterEach", "AfterEach"]:
                        o.afterEach(obj)
                    elif key in ["after", "After"]:
                        o.after(obj)
                    else:
                        funcs.append((key, obj))
                __pragma__('nojsiter')

                for name, func in funcs:
                    o(name, func)

            o.spec(Cls.__name__, dospec)
    Wrapper()
    return Wrapper

# ================================================== #
#                        EOF                         #
# ================================================== #