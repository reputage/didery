"""
Module that contains the command line app.

Why does this file exist, and why not put this in __main__?

  You might be tempted to import things from __main__ later, but that will cause
  problems: the code will get executed twice:

  - When you run `python -mbluepea` python will execute
    ``__main__.py`` as a script. That means there won't be any
    ``bluepea.__main__`` in ``sys.modules``.
  - When you import __main__ it will get executed again (as a module) because
    there's no ``bluepea.__main__`` in ``sys.modules``.

  Also see (1) from http://click.pocoo.org/5/setuptools/#setuptools-integration
"""
import click
import ioflo.app.run

from ioflo.aid import odict
from ioflo.aid.consoling import VERBIAGE_NAMES


@click.command()
@click.option(
    '--port',
    '-p',
    multiple=False,
    default=8080,
    type=click.IntRange(1, 65535),
    help='port number the server should listen on'
)
@click.option(
    '--verbose',
    '-v',
    type=click.Choice(VERBIAGE_NAMES),
    default=VERBIAGE_NAMES[2],
    help='verbosity level'
)
def main(port, verbose):
    click.echo("MAIN")
    """ Main entry point for ioserve CLI"""

    verbose = VERBIAGE_NAMES.index(verbose)

    ioflo.app.run.run(  name="skedder",
                        period=0.125,
                        real=True,
                        retro=True,
                        filepath='src/didery/flo/main.flo',
                        behaviors=['didery.core'],
                        mode='',
                        username='',
                        password='',
                        verbose=verbose,
                        consolepath='',
                        statistics=False,
                        preloads=[('.main.server.port', odict(value=port))])
