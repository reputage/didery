![didery logo](https://github.com/reputage/didery.js/blob/dev/logo/didery.png)

[![Documentation Status](https://readthedocs.org/projects/didery/badge/?version=latest)](https://didery.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://travis-ci.org/reputage/didery.svg?branch=master)](https://travis-ci.org/reputage/didery)


Background
==========
Cryptographic key management is a challenging problem for the blockchain community. To address this problem, we have developed a decentralized key management toolkit called Didery which is designed to manage decentralized identifiers [(DIDs)](https://w3c-ccg.github.io/did-spec/). [DIDs](https://w3c-ccg.github.io/did-spec/), as a [W3C specification](https://w3c-ccg.github.io/did-spec/), have the potential to eventually supplant URLs as the main identifier in Web 3.0 applications. Didery implements ideas found in the paper titled [“Decentralized Autonomic Data (DAD) and the three R's of Key Management”](https://github.com/WebOfTrustInfo/rebooting-the-web-of-trust-spring2018/blob/master/final-documents/DecentralizedAutonomicData.md) presented at the Rebooting the Web of Trust spring 2018 conference. Didery will improve the management, security, and user experience of anyone handling the cryptographic keys associated with [DIDs](https://w3c-ccg.github.io/did-spec/). The initial release of Didery provides two main services, a key pre-rotation service and a one-time pad encrypted storage service. Pre-rotation enables creation/rotation/revocation of key rotation histories for the key pairs associated with a root [DID](https://w3c-ccg.github.io/did-spec/). The service may be run as a rotation history service or as a set of redundant public servers. It also provides support for one-time pad encrypted private keys for recovery that works with the associated [SeedQuest](https://github.com/reputage/seedQuest) 3D key recovery mnemonic. The Didery toolkit is open-source with [JavaScript](https://github.com/reputage/didery.js) and [Python](https://github.com/reputage/didery.py) client SDKs for interacting with Didery servers. Didery helps simplify key management. 

The project is built on the open source [ioflo](https://github.com/ioflo) framework and also utilizes [click](http://click.pocoo.org/5/), and [lmdb](https://lmdb.readthedocs.io/en/release/) on the back end.  The frontend is built with [Transcrypt](https://www.transcrypt.org/documentation) and [mithril.js](https://mithril.js.org/).

How Didery Works
================
Didery offers two completely separate but complementary services.  The first is a store of key rotation histories and the second is a store for encrypted data.

All information uploaded to didery requires a decentralized identifier(DID) and a signature to ensure data provenance.

### Rotation Histories
The key rotation store utilizes pre-rotation to solve the secure rotation problem. Pre-rotation requires that you declare ahead of time what public key you will rotate to.  Didery provides a protocol for pre-rotation and a public store of rotation histories.  

The pre-rotation protocol works as follows:

#### Key Pair Inception
1. Generate key pair (current key pair)
2. Generate a second key pair (pre-rotated key pair)
3. Create a rotation history that contains the two public keys above
4. Sign the rotation history data with only the current private key
5. Upload the rotation history and signature to Didery 

```
POST /history HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 324
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9
Signature: signer="AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg=="
    
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
    "changed": "2000-01-01T00:00:00+00:00",
    "signer": 0,
    "signers": 
    [
        "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148="
    ]
}
```

#### Rotation Event
1. Generate a new key pair (new pre-rotated key pair)
2. Add newly generated public key to the history
3. Sign the history data with the current and pre-rotated key pairs
4. Upload the rotation history and signature to Didery
```
PUT /history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 324
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9
Signature: signer="AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg=="; rotation="o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
    
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
    "changed": "2000-01-01T00:00:00+00:00",
    "signer": 1,
    "signers": 
    [
        "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
    ]
}
```

### Encrypted Data Store
The encrypted data store is meant to be used in conjunction with SeedQuest and One Time Pads(OTP). However, the service only requires that uploaded data include a DID and a signature.  You are free to upload data that is not encrypted, or encrypted with another method other than OTP.  

Keep in mind that any data uploaded to this store will be publicly available for anyone to view.  For this reason we chose to use OTP’s because they offer perfect security meaning they can only be cracked via brute force.

### Decentralized Redundant Immutable Data
The didery service is designed to be a decentralized redundant immutable data store. In practice this means that the service can be run by anyone and works best with multiple instances.

We offer a Javascript and a Python SDK that handles broadcasting updates and polling data from a group of trusted servers.  This gives an added level of redundancy and security to the service, but if you choose you can use a single server.

How To Use Didery
=================
Didery is meant to be a back end service for you to publicly store your rotation histories and so others can verify what key you are using.  Your service should send updates to Didery using the protocol outlined [here](#how-didery-works) and [here](https://github.com/reputage/didery/blob/master/docs/api/public_api/public_api.md#key-rotation-history).

You will need to point anyone you’re communicating with to the didery instances you use and trust. The DID Document(DDO) provides a solution for this. You can add a service endpoint section to your DDO that includes all the Didery instances you trust. This will allow those you are communicating with to verify that the key pair you signed with belongs to you.


System Requirements
===================
python 3.6  
libsodium 1.0.16  
Linux or macOS  

Development Dependencies
========================
git  
npm  
wheel  

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

A common issue with running the software is that your system doesn't have libsodium 16 or greater installed. Run these commands and try again:

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
$ didery
```
After running the command a WSGI compatible [Valet](https://github.com/ioflo/ioflo/blob/master/ioflo/aio/http/serving.py) server will have been spun up to listen for web requests.  The default port that didery will listen on is 8080.

The cli interface for didery has a couple options that you can see below.

```
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

```

You can manage the backend from your browser by going to:
```
http://localhost:8080
```

The CLI uses click to build its interface.  Unfortunately it doesn't always work well with other tools like circus because of character encodings. For this reason there is an alternative entry point into didery that uses parseArgs for the cli.  If you run into character encoding errors you can try running didery as shown below.
```
$ dideryd
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
=============
You can read the REST API documentation in the [wiki](https://github.com/reputage/didery/wiki) and the frontend documentation in the [docs](https://github.com/reputage/didery/tree/master/docs) folder.

One Time Pad Cryptography
=========================
Didery’s encrypted data store, in conjunction with [SeedQuest](https://github.com/reputage/seedQuest), uses One Time Pads(OTP) and signatures to encrypt private keys. Didery is storing encrypted private keys in an open and pubic database, because of this the encryption must be of the highest strength. OTPs have perfect security providing a strong enough encryption for storing private keys publicly. OTPs are not used in modern day cryptography only because of the secret sharing problem.  In our use case you are the only user of the secret so there is no sharing problem. This makes OTPs perfect for our service.
  

SeedQuest uses a cryptographically secure pseudo-random number generator(CSPRNG) from [libsodium](https://libsodium.gitbook.io/doc/) to generate a 128 bit seed. The seed is stretched to the size of the data to create the one time pad. The pad is then XOR'd with the data to encrypt it. Finally the data is signed to make it tamper proof. Didery will only allow new data to be added to the public store if the signature validates.

