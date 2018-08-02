####################
didery Documentation
####################

This project is based on the key management ideas from this rebooting the web of trust white paper: `DAD Spec <https://github.com/WebOfTrustInfo/rebooting-the-web-of-trust-spring2018/blob/master/final-documents/DecentralizedAutonomicData.md>`_. The project follows the spec detailed in the white paper and provides a secure store for key rotation histories and one time pad(otp) encrypted private keys. The project also utilizes Decentralized Identifiers(DID) as specified in the `W3C Spec <https://w3c-ccg.github.io/did-spec/>`_ and incorporates the new decentralized autonomic data(dad) method.

The project is built on the open source `ioflo <https://github.com/ioflo>`_ framework.  The command line interface for the server in this project is handled by ioflo and more information about command line options can be found in `ioflo's documentation <https://github.com/ioflo/ioflo_manuals>`_.  The API is built using the falcon api framework and lmdb.  The frontend is built with Transcrypt and mithril.js.

.. toctree::
   :maxdepth: 5
   :caption: Table of Contents
   :glob:
   :titlesonly:

   api/index
   frontend/index
   decentralized_autonomic_data