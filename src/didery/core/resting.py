import falcon

from ioflo.aid import getConsole
from ioflo.aid import odict
from ioflo.aio.http import Valet
from ioflo.base import doify

from didery import routing
from didery.db import dbing

console = getConsole()

"""
Usage pattern

frame server
    do didery server open at enter
    do didery server service
    do didery server close at exit
"""


@doify('DideryServerOpen', ioinits=odict(
                                        valet="",
                                        test="",
                                        port=odict(ival=8080),
                                        db=odict(ival=""),
                                        ))
def dideryServerOpen(self):
    """
    Setup and open a rest server

    Ioinit attributes
        valet is Valet instance (wsgi server)
        port is server port

    Context: enter

    Example:
        do didery server open at enter
    """
    port = int(self.port.value)
    dbing.setupDbEnv(self.db.value, self.port.value)

    app = falcon.API(middleware=[routing.CORSMiddleware()])
    routing.loadEndPoints(app, store=self.store)

    self.valet.value = Valet(
                            port=port,
                            bufsize=131072,
                            wlog=None,
                            store=self.store,
                            app=app,
                            timeout=0.5,
                            )

    console.terse("IP Address {}\n".format(self.valet.value.servant.ha))

    result = self.valet.value.servant.reopen()

    if not result:
        console.terse("Error opening server '{0}' at '{1}'\n".format(
            self.valet.name,
            self.valet.value.servant.ha))
        return

    console.concise("Opened server '{0}' at '{1}'\n".format(
        self.valet.name,
        self.valet.value.servant.ha, ))


@doify('DideryServerService', ioinits=odict(valet=""))
def dideryServerService(self):
    """
    Service server given by valet

    Ioinit attributes:
        valet is a Valet instance

    Context: recur

    Example:
        do didery server service
    """
    if self.valet.value:
        self.valet.value.serviceAll()


@doify('DideryServerClose', ioinits=odict(valet="",))
def dideryServerClose(self):
    """
    Close server in valet

    Ioinit attributes:
        valet is a Valet instance

    Context: exit

    Example:
        do didery server close at exit
    """
    if self.valet.value:
        self.valet.value.servant.closeAll()

        console.concise("Closed server '{0}' at '{1}'\n".format(
                            self.valet.name,
                            self.valet.value.servant.eha))
