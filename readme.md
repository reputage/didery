![didery logo](https://github.com/reputage/didery.js/blob/dev/logo/didery.png)

[![Documentation Status](https://readthedocs.org/projects/didery/badge/?version=latest)](https://didery.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/reputage/didery.svg?branch=master)](https://travis-ci.org/reputage/didery)


Background
==========
Cryptographic key management is a challenging problem for the blockchain community. To address this problem, we have developed a decentralized key management toolkit called Didery which is designed to manage decentralized identifiers [(DIDs)](https://w3c-ccg.github.io/did-spec/). [DIDs](https://w3c-ccg.github.io/did-spec/), as a [W3C specification](https://w3c-ccg.github.io/did-spec/), have the potential to eventually supplant URLs as the main identifier in Web 3.0 applications. Didery implements ideas found in the paper titled [“Decentralized Autonomic Data (DAD) and the three R's of Key Management”](https://github.com/WebOfTrustInfo/rebooting-the-web-of-trust-spring2018/blob/master/final-documents/DecentralizedAutonomicData.md) presented at the Rebooting the Web of Trust spring 2018 conference. Didery will improve the management, security, and user experience of anyone handling the cryptographic keys associated with [DIDs](https://w3c-ccg.github.io/did-spec/). The initial release of Didery provides two main services, a key pre-rotation service and a one-time pad encrypted storage service. Pre-rotation enables creation/rotation/revocation of key rotation histories for the key pairs associated with a root [DID](https://w3c-ccg.github.io/did-spec/). The service may be run as a rotation history service or as a set of redundant public servers. It also provides support for one-time pad encrypted private keys for recovery that works with the associated [SeedQuest](https://github.com/reputage/seedQuest) 3D key recovery mnemonic. The Didery toolkit is open-source with [JavaScript](https://github.com/reputage/didery.js) and [Python](https://github.com/reputage/didery.py) client SDKs for interacting with Didery servers. Didery helps simplify key management. 

The project is built on the open source [ioflo](https://github.com/ioflo) framework and also utilizes [click](http://click.pocoo.org/5/), and [lmdb](https://lmdb.readthedocs.io/en/release/) on the back end.  The frontend is built with [Transcrypt](https://www.transcrypt.org/documentation) and [mithril.js](https://mithril.js.org/).



Installation
============

This project depends on [python 3.6](https://www.python.org/downloads/).  You will need to install it if you haven't already.

Clone or download the source from the [didery Github repo](https://github.com/reputage/didery.git) and install from source with:
```
$ pip3 install -e /path/to/didery
```
Or intall through Pypi with:
```
$ pip3 install didery
```

Install node and npm on your system.  You can find instructions [here](https://nodejs.org/en/download/). Or if you use Ubuntu run this command:
```
$ sudo apt install npm
```
Then run these commands:
```
$ cd /path/to/didery/src/didery/static/
$ npm install
$ npm run-script transcrypt
```

A common issue with running the software is that your system doesn't have libsodium 13 or greater installed. Run these commands and try again:

Mac
```
$ brew install libsodium
```  
Linux
```
$ wget https://download.libsodium.org/libsodium/releases/libsodium-1.0.16.tar.gz  
$ tar -zxvf libsodium-1.0.16.tar.gz  
$ cd libsodium-1.0.16  
$ ./configure  
$ make && make check  
$ sudo make install  
```

Starting The Server
==================
To start up the server simply run the command below

```
$ dideryd
```
After running the command a WSGI compatible [Valet](https://github.com/ioflo/ioflo/blob/master/ioflo/aio/http/serving.py) server will have been spun up to listen for web requests.  The default port that didery will listen on is 8080.

The cli interface for didery has a couple options that you can see below.

```
Usage: dideryd [OPTIONS]

Options:
  -p, --port INTEGER RANGE        port number the server should listen on
  -v, --verbose [mute|terse|concise|verbose|profuse]
                                  verbosity level
  --help                          Show this message and exit.

```

You can manage the backend from your browser by going to:
```
http://localhost:8080
```

Testing
=======
You will first need to clone the GitHub repo if you installed using the Pypi wheel. There are two sets of unit tests included in the project. The first of which tests the didery backend and can be run using the command:
```
$ pytest --ignore=src/didery/static/
```
The second tests the didery frontend and can be run using these commands:
```
$ cd /path/to/didery/src/didery/static/
$ npm run-script prep-tests
$ npm test
```
Running these tests prior to hosting the server helps ensure that everything in your copy of didery is working properly.


Documentation
===
You can read the REST API documentation in the [wiki](https://github.com/reputage/didery/wiki) and the frontend documentation in the [docs](https://github.com/reputage/didery/tree/master/docs) folder.
