####################
didery Documentation
####################

Cryptographic key management is a challenging problem for the blockchain
community. To address this problem, we have developed a decentralized
key management toolkit called Didery which is designed to manage
decentralized identifiers
`(DIDs) <https://w3c-ccg.github.io/did-spec/>`__.
`DIDs <https://w3c-ccg.github.io/did-spec/>`__, as a `W3C
specification <https://w3c-ccg.github.io/did-spec/>`__, have the
potential to eventually supplant URLs as the main identifier in Web 3.0
applications. Didery implements ideas found in the paper titled
`“Decentralized Autonomic Data (DAD) and the three R's of Key
Management” <https://github.com/WebOfTrustInfo/rebooting-the-web-of-trust-spring2018/blob/master/final-documents/DecentralizedAutonomicData.md>`__
presented at the Rebooting the Web of Trust spring 2018 conference.
Didery will improve the management, security, and user experience of
anyone handling the cryptographic keys associated with
`DIDs <https://w3c-ccg.github.io/did-spec/>`__. The initial release of
Didery provides two main services, a key pre-rotation service and a
one-time pad encrypted storage service. Pre-rotation enables
creation/rotation/revocation of key rotation histories for the key pairs
associated with a root `DID <https://w3c-ccg.github.io/did-spec/>`__.
The service may be run as a rotation history service or as a set of
redundant public servers. It also provides support for one-time pad
encrypted private keys for recovery that works with the associated
`SeedQuest <https://github.com/reputage/seedQuest>`__ 3D key recovery
mnemonic. The Didery toolkit is open-source with
`JavaScript <https://github.com/reputage/didery.js>`__ and
`Python <https://github.com/reputage/didery.py>`__ client SDKs for
interacting with Didery servers. Didery helps simplify key management.

The project is built on the open source
`ioflo <https://github.com/ioflo>`__ framework and also utilizes
`click <http://click.pocoo.org/5/>`__, and
`lmdb <https://lmdb.readthedocs.io/en/release/>`__ on the back end. The
frontend is built with
`Transcrypt <https://www.transcrypt.org/documentation>`__ and
`mithril.js <https://mithril.js.org/>`__.

.. toctree::
   :maxdepth: 5
   :caption: Table of Contents
   :glob:
   :titlesonly:

   getting_started
   api/index
   frontend/index
   decentralized_autonomic_data