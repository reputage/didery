#!/usr/bin/env python
# -*- encoding: utf-8 -*-

"""
Basic setup file to enable pip install
See:
    https://pythonhosted.org/setuptools/
    https://bitbucket.org/pypa/setuptools


$ python setup.py register sdist upload

More secure to use twine to upload
$ pip3 install twine
$ python3 setup.py sdist
$ twine upload dist/toba-0.1.0.tar.gz

"""

from __future__ import generator_stop

import sys
import io
import os
import re

v = sys.version_info
if v < (3, 5):
    msg = "FAIL: Requires Python 3.6 or later, but setup.py was run using {}.{}.{}"
    print(msg.format(v.major, v.minor, v.micro))
    print("NOTE: Installation failed. Run setup.py using python3")
    sys.exit(1)


from glob import glob
from os.path import basename
from os.path import dirname
from os.path import join
from os.path import relpath
from os.path import splitext

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup
from setuptools.command.build_ext import build_ext

try:
    # Allow installing package without any Cython available. This
    # assumes you are going to include the .c files in your sdist.
    import Cython
except ImportError:
    Cython = None


def read(*names, **kwargs):
    return io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ).read()


# Enable code coverage for C code: we can't use CFLAGS=-coverage in tox.ini, since that may mess with compiling
# dependencies (e.g. numpy). Therefore we set SETUPPY_CFLAGS=-coverage in tox.ini and copy it to CFLAGS here (after
# deps have been safely installed).
if 'TOXENV' in os.environ and 'SETUPPY_CFLAGS' in os.environ:
    os.environ['CFLAGS'] = os.environ['SETUPPY_CFLAGS']


class optional_build_ext(build_ext):
    """Allow the building of C extensions to fail."""
    def run(self):
        try:
            build_ext.run(self)
        except Exception as e:
            self._unavailable(e)
            self.extensions = []  # avoid copying missing files (it would fail).

    def _unavailable(self, e):
        print('*' * 80)
        print('''WARNING:

    An optional code optimization (C extension) could not be compiled.

    Optimizations for this package will not be available!
        ''')

        print('CAUSE:')
        print('')
        print('    ' + repr(e))
        print('*' * 80)


setup(
    name='didery',
    version="0.1.2",
    license='Apache2',
    description='DIDery Key Management Server',
    long_description="Redundant persistent backup of key rotation events and otp encrypted private keys.",
    author='Nicholas Telfer, Brady Hammond, Michael Mendoza',
    author_email='nick.telfer@consensys.net',
    url='https://github.com/reputage/didery',
    packages=find_packages('src'),
    package_dir={'': 'src'},
    py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
    package_data={
        'didery': ['static/main.html',
                   'static/css/*.css',
                   'static/fonts/Raleway/*.ttf',
                   'static/node_modules/mithril/mithril.min.js',
                   'static/node_modules/jquery/dist/jquery.min.js',
                   'static/node_modules/semantic-ui/dist/semantic.min.css',
                   'static/node_modules/semantic-ui/dist/semantic.min.js',
                   'static/node_modules/semantic-ui/dist/themes/default/assets/fonts/*.woff2',
                   'static/node_modules/semantic-ui/dist/themes/default/assets/fonts/*.woff',
                   'static/node_modules/semantic-ui/dist/themes/default/assets/fonts/*.ttf',
                   'static/transcrypt/__javascript__/main.js',
                   'flo/*.flo'
                   ]
    },
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Operating System :: Unix',
        'Operating System :: POSIX',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: Implementation :: CPython',
        'Topic :: Utilities',
    ],
    keywords=[
        # eg: 'keyword1', 'keyword2', 'keyword3',
    ],
    install_requires=[
        'click', 'falcon>=1.2', 'ioflo>=1.6.8', 'libnacl>=1.5.1',
        'simplejson>=3.11.1', 'pytest-falcon>=0.4.2', 'arrow>=0.10.0',
        'transcrypt<=3.6.101', 'lmdb',
    ],
    extras_require={
        # eg:
        #   'rst': ['docutils>=0.11'],
        #   ':python_version=="2.6"': ['argparse'],
    },
    setup_requires=[
        'cython',
    ] if Cython else [],
    entry_points={
        'console_scripts': [
            'didery = didery.cli:main',
            'dideryd = didery.app:main',
        ]
    },
    cmdclass={'build_ext': optional_build_ext},
    ext_modules=[
        Extension(
            splitext(relpath(path, 'src').replace(os.sep, '.'))[0],
            sources=[path],
            include_dirs=[dirname(path)]
        )
        for root, _, _ in os.walk('src')
        for path in glob(join(root, '*.pyx' if Cython else '*.c'))
    ],
)
