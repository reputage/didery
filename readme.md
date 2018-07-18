![didery logo](https://github.com/reputage/didery.js/blob/dev/logo/didery.png)

Background
==========
This project is based on the key management ideas from this rebooting the web of trust white paper: [DAD Spec](https://github.com/WebOfTrustInfo/rebooting-the-web-of-trust-spring2018/blob/master/final-documents/DecentralizedAutonomicData.md). The project follows the spec detailed in the white paper and provides a secure store for key rotation histories and one time pad(otp) encrypted private keys. The project also utilizes Decentralized Identifiers(DID) as specified in the [W3C Spec](https://w3c-ccg.github.io/did-spec/) and incorporates the new decentralized autonomic data(dad) method.  

The project is built on the open source [ioflo](https://github.com/ioflo) framework.  The command line interface for the server in this project is handled by ioflo and more information about command line options can be found in [ioflo's documentation](https://github.com/ioflo/ioflo_manuals).  The API is built using the falcon api framework and lmdb.  The frontend is built with Transcrypt and mithril.js.



Installation
============

This project depends on [python 3.6](https://www.python.org/downloads/).  You will need to install it if you haven't already.

Clone or download the source from the [didery Github repo](https://github.com/reputage/didery.git) and install it:
```
$ pip3 install -e /path/to/didery
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
$ wget https://download.libsodium.org/libsodium/releases/libsodium-1.0.13.tar.gz  
$ tar -zxvf libsodium-1.0.13.tar.gz  
$ cd libsodium-1.0.13  
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

There are two sets of unit tests included in the project. The first of which tests the didery backend and can be run using the command:
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
