import os
import ioflo.app.run

from ioflo.aid import odict
from ioflo.aid.consoling import VERBIAGE_NAMES


def main():
    projectDirpath = os.path.dirname(
        os.path.dirname(
            os.path.abspath(
                os.path.expanduser(__file__)
            )
        )
    )
    floScriptpath = os.path.join(projectDirpath, "didery/flo/main.flo")
    print(floScriptpath)

    verbose = VERBIAGE_NAMES.index("terse")

    ioflo.app.run.run(name="skedder",
                      period=0.125,
                      real=True,
                      retro=True,
                      filepath=floScriptpath,
                      behaviors=['didery.core'],
                      mode='',
                      username='',
                      password='',
                      verbose=verbose,
                      consolepath='',
                      statistics=False,
                      preloads=[
                          ('.main.server.port', odict(value=7000)),
                          ('.main.server.db', odict(value=None))
                      ])


if __name__ == '__main__':
    main()
