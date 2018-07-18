#######################
didery.py Documentation
#######################

This project is based on the key management ideas from this rebooting the web of trust white paper: `DAD Spec <https://github.com/WebOfTrustInfo/rebooting-the-web-of-trust-spring2018/blob/master/final-documents/DecentralizedAutonomicData.md>`_. The project follows the spec detailed in the white paper and provides a secure store for key rotation histories and one time pad(otp) encrypted private keys. The project also utilizes Decentralized Identifiers(DID) as specified in the `W3C Spec <https://w3c-ccg.github.io/did-spec/>`_ and incorporates the new decentralized autonomic data(dad) method.

The project is built on the open source `ioflo <https://github.com/ioflo>`_ framework.  The command line interface for the server in this project is handled by ioflo and more information about command line options can be found in `ioflo's documentation <https://github.com/ioflo/ioflo_manuals>`_.  The API is built using the falcon api framework and lmdb.  The frontend is built with Transcrypt and mithril.js.

Table of Contents
=================

- `API <https://github.com/reputage/didery/tree/dev/docs/api>`_
   - `Management API <https://github.com/reputage/didery/tree/dev/docs/api/management_api>`_
      - `Erorr Logs <https://github.com/reputage/didery/tree/dev/docs/api/management_api/error_logs>`_
         - `Get All Errors <https://github.com/reputage/didery/blob/dev/docs/api/management_api/error_logs/get_all_errors.md>`_
      - `Relay Servers <https://github.com/reputage/didery/tree/dev/docs/api/management_api/relay_servers>`_
         - `Add Relay Server <https://github.com/reputage/didery/blob/dev/docs/api/management_api/relay_servers/add_relay_server.md>`_
      - `Authentication <https://github.com/reputage/didery/blob/dev/docs/api/management_api/authentication.md>`_
      - `Error Types <https://github.com/reputage/didery/blob/dev/docs/api/management_api/error_types.md>`_
   - `Public API <https://github.com/reputage/didery/tree/dev/docs/api/public_api>`_
- `Frontend <https://github.com/reputage/didery.js/blob/master/docs/batch>`_
   - `batchGetHistory <https://github.com/reputage/didery.js/blob/master/docs/batch/batchGetHistory.rst>`_
   - `batchPostHistory <https://github.com/reputage/didery.js/blob/master/docs/batch/batchPostHistory.rst>`_
   - `batchPutHistory <https://github.com/reputage/didery.js/blob/master/docs/batch/batchPutHistory.rst>`_
   - `batchGetBlobs <https://github.com/reputage/didery.js/blob/master/docs/batch/batchGetBlobs.rst>`_
   - `batchPostBlobs <https://github.com/reputage/didery.js/blob/master/docs/batch/batchPostBlobs.rst>`_
   - `batchPutBlobs <https://github.com/reputage/didery.js/blob/master/docs/batch/batchPutBlobs.rst>`_
   - `batchGetRelays <https://github.com/reputage/didery.js/blob/master/docs/batch/batchGetRelays.rst>`_
   - `batchPostRelays <https://github.com/reputage/didery.js/blob/master/docs/batch/batchPostRelays.rst>`_
   - `batchPutRelays <https://github.com/reputage/didery.js/blob/master/docs/batch/batchPutRelays.rst>`_
   - `batchDeleteRelays <https://github.com/reputage/didery.js/blob/master/docs/batch/batchDeleteRelays.rst>`_
   - `batchGetErrors <https://github.com/reputage/didery.js/blob/master/docs/batch/batchGetErrors.rst>`_


