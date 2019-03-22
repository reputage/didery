# Modes
Didery supports three running modes that give different levels of security.  The supported modes are listed below.

* Method
* Promiscuous
* Race

Modes mostly restrict POST and PUT requests scope. and alter the behavior of DELETE requests.

Method Mode
-----------
Only requests containing supported DID methods will be accepted in POST requests.

Promiscuous Mode
----------------
This mode has cascading permissions. If a request contains a supported DID method Didery will default back to 
method mode for that request. Any requests containing unsupported DID methods but contain a valid signature 
will be recorded.

Race Mode
---------
This mode has the same cascading permissions as Promiscuous mode. If a DID method is not supported the 
first person to submit a history with a valid signature will be the only one who can upload/update a history 
for that DID. Hence the name "race".

Switching Modes
---------------
If switching from promiscuous mode to race mode deletion will continue to function the same way it did in 
promiscuous mode.  Anyone who has uploaded a history for a specific DID can delete their personal history.  If a DID 
has multiple histories, because of promiscuous mode, only the owners of the individual histories can delete them in 
promiscuous or race mode.  In method mode only the actual owner of the DID can delete any part of a history.