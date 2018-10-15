import os
import argparse
import ioflo.app.run

from ioflo.aid import odict
from ioflo.aid import consoling

from didery import __version__
from didery.db.dbing import DATABASE_DIR_PATH


def parseArgs(version=__version__):
    d = "Runs didery server. "
    d += "Example: app.py --port 8000'\n"
    p = argparse.ArgumentParser(description=d)
    p.add_argument('-V', '--version',
                   action='version',
                   version=version,
                   help="Prints out version of didery script runner.")
    p.add_argument('-v', '--verbose',
                   action='store',
                   default='concise',
                   choices=['0', '1', '2', '3', '4'].extend(consoling.VERBIAGE_NAMES),
                   help="Verbosity level.")
    p.add_argument('-p', '--path',
                   action='store',
                   help="Path to the database folder. Defaults to {}.".format(DATABASE_DIR_PATH))
    p.add_argument('-P', '--port',
                   action='store',
                   default=8080,
                   help="Port number the server should listen on. Default is 8080.")

    args = p.parse_args()

    if args.verbose in consoling.VERBIAGE_NAMES:
        verbosage = consoling.VERBIAGE_NAMES.index(args.verbose)
    else:
        verbosage = int(args.verbose)

    args.verbose = verbosage  # converted value
    return args


def main():
    args = parseArgs(version=__version__)

    projectDirpath = os.path.dirname(
        os.path.dirname(
            os.path.abspath(
                os.path.expanduser(__file__)
            )
        )
    )
    floScriptpath = os.path.join(projectDirpath, "didery/flo/main.flo")

    ioflo.app.run.run(name="skedder",
                      period=0.125,
                      real=True,
                      retro=True,
                      filepath=floScriptpath,
                      behaviors=['didery.core'],
                      mode='',
                      username='',
                      password='',
                      verbose=args.verbose,
                      consolepath='',
                      statistics=False,
                      preloads=[
                          ('.main.server.port', odict(value=args.port)),
                          ('.main.server.db', odict(value=args.path))
                      ])


if __name__ == '__main__':
    main()
