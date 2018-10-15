"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -m dideryd` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``didery.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``didery.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import os
import click
import ioflo.app.run

from ioflo.aid import odict
from ioflo.aid.consoling import VERBIAGE_NAMES

from didery import __version__
from didery.db.dbing import DATABASE_DIR_PATH


@click.command()
@click.option(
    '--port',
    '-p',
    multiple=False,
    default=8080,
    type=click.IntRange(1, 65535),
    help='Port number the server should listen on. Default is 8080.'
)
@click.option(
    '--version',
    '-V',
    multiple=False,
    is_flag=True,
    default=False,
    help="Return version."
)
@click.option(
    '--verbose',
    '-v',
    type=click.Choice(VERBIAGE_NAMES),
    default=VERBIAGE_NAMES[2],
    help='Verbosity level.'
)
@click.option(
    '--path',
    multiple=False,
    type=click.Path(file_okay=False, resolve_path=True, writable=True),
    help='Path to the database folder. Defaults to {}.'.format(DATABASE_DIR_PATH)
)
def main(port, version, verbose, path):
    if version:
        click.echo(__version__)
        return

    projectDirpath = os.path.dirname(
        os.path.dirname(
            os.path.abspath(
                os.path.expanduser(__file__)
            )
        )
    )
    floScriptpath = os.path.join(projectDirpath, "didery/flo/main.flo")

    click.echo("MAIN")
    """ Main entry point for ioserve CLI"""

    verbose = VERBIAGE_NAMES.index(verbose)

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
                          ('.main.server.port', odict(value=port)),
                          ('.main.server.db', odict(value=path))
                      ])
