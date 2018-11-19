System Requirements
===================

python 3.6 libsodium 1.0.16 Linux or macOS

Installation
============

This project depends on `python
3.6 <https://www.python.org/downloads/>`__. You will need to install it
if you haven't already.

Clone or download the source from the `didery Github
repo <https://github.com/reputage/didery.git>`__ and install from source
with:

::

    $ pip3 install -e /path/to/didery

Or intall through Pypi with:

::

    $ pip3 install didery

Install node and npm on your system. You can find instructions
`here <https://nodejs.org/en/download/>`__. Or if you use Ubuntu run
this command:

::

    $ sudo apt install npm

Then run these commands:

::

    $ cd /path/to/didery/src/didery/static/
    $ npm install
    $ npm run-script transcrypt

A common issue with running the software is that your system doesn't
have libsodium 16 or greater installed. Run these commands and try
again:

Mac

::

    $ brew install libsodium

Linux

::

    $ wget https://download.libsodium.org/libsodium/releases/libsodium-1.0.16.tar.gz  
    $ tar -zxvf libsodium-1.0.16.tar.gz  
    $ cd libsodium-1.0.16  
    $ ./configure  
    $ make && make check  
    $ sudo make install  

Starting The Server
===================

To start up the server simply run the command below

::

    $ didery

After running the command a WSGI compatible
`Valet <https://github.com/ioflo/ioflo/blob/master/ioflo/aio/http/serving.py>`__
server will have been spun up to listen for web requests. The default
port that didery will listen on is 8080.

The cli interface for didery has a couple options that you can see
below.

::

    Usage: didery [OPTIONS]

    Options:
      -p, --port INTEGER RANGE        Port number the server should listen on.
                                      Default is 8080.
      -V, --version                   Return version.
      -v, --verbose [mute|terse|concise|verbose|profuse]
                                      Verbosity level.
      --path DIRECTORY                Path to the database folder. Defaults to
                                      /var/didery/db.
      --help                          Show this message and exit.

You can manage the backend from your browser by going to:

::

    http://localhost:8080

The CLI uses click to build its interface. Unfortunately it doesn't
always work well with other tools like circus because of character
encodings. For this reason there is an alternative entry point into
didery that uses parseArgs for the cli. If you run into character
encoding errors you can try running didery shown below.

::

    $ dideryd

Testing
=======

You will first need to clone the GitHub repo if you installed using the
Pypi wheel. There are two sets of unit tests included in the project.
The first of which tests the didery backend and can be run using the
command:

::

    $ pytest --ignore=src/didery/static/

The second tests the didery frontend and can be run using these
commands:

::

    $ cd /path/to/didery/src/didery/static/
    $ npm run-script prep-tests
    $ npm test

Running these tests prior to hosting the server helps ensure that
everything in your copy of didery is working properly.
