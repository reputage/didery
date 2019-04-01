Modes
=====

Didery is meant to be a universal rotation service. It is designed to
work with any DID method, and is built to have high throughput. In order
to attain these goals we implemented different running modes.

| When working with DID's there is an inherent security flaw that
  requires that you validate that the clients public key belongs to the
  DID you've received. The normal method for doing this would be to look
  up the DID Document and compare public keys. Because Didery is meant
  to be a backbone infrastructure piece it needs to be fast and have a
  high throughput.
| If Didery has to look up the DID Document for every request it
  significantly slows down the service.

The only other way to validate a public key is to resolve the idstring
to it's corresponding public key. This requires having and maintaining
an implementation for every DID method. This is problematic because the
DID spec has not been finalized, there is no limit to the number of DID
methods, and the methods are constantly changing.

In order to solve this problem Didery supports multiple running modes
that give different levels of security. The mode Didery will use can be
specified at startup. By default Didery will use Method mode.

-  Method
-  Promiscuous
-  Race

Method Mode
-----------

When Didery runs this mode it will check that incoming POST requests
contain a DID for which Didery has a method resolver. If no resolver
exists the request will be rejected with a http 400 error. If a resolver
exists Didery will validate that the first key in the signers field
matches the key used in the DID's idstring.

Promiscuous Mode
----------------

This mode has cascading permissions. If a POST request contains a
supported DID method Didery will default back to method mode and
validate the idstring and public key for that request. For all other
POST requests if the signature validates a new history will be created.

The purpose of this mode is to allow any DID method to be accepted while
also allowing a consumer of the service to detect if someone has tried
to hack a DID. However there is a limitation to detecting hacking. If
only one history has been uploaded Didery has no way of knowing if a
hacker or the owner uploaded it.

This mode pushes the validation step onto the consumers of the service.
For your service to be secure you will need to validate the public key
and the DID's idstring yourself.

Race Mode
---------

This mode has cascading permissions. If a POST request contains a
supported DID method Didery will default back to method mode and
validate the idstring and public key for that request. If a DID method
is not supported the first person to submit a history with a valid
signature will be the only one who can upload/update a history for that
DID.

Deletion
========

In order to securely delete histories across running modes we had to
implement different behaviors for each mode. It is possible for a server
to be run in one mode for a time and then later be switched to a
different mode. Anyone who has uploaded a history for a specific DID can
delete their personal history. If a DID has multiple histories, because
of promiscuous mode, the owners of the individual histories can delete
them regardless of what mode Didery is currently using.

Method Mode
-----------

The owner of a DID can delete their history as well as any other
histories connected to the DID. When a server has been run in
promiscuous mode and then switched to method mode deletion can take a
different path. If a DELETE request is received and the requester is not
the owner of the DID, but they have a history attached to the DID, only
their history will be deleted. If no history was uploaded by the
requester the request will be denied.

Promiscuous Mode
----------------

Promiscuous mode allows multiple histories per DID. When DELETE requests
are received a history is looked up using the DID and the public key
included in the request. If no history is found an error is returned. If
a history exists signatures are validated against the histories current
signing key. Only histories that contain the key sent in the DELETE
request will be deleted.

Race Mode
---------

The owner of a specific history can delete their history just like in
promiscuous mode. If a server was first run in promiscuous mode and then
switched to race mode, only the owner of a specific history can delete
it.
