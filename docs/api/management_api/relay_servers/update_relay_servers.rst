Update Relay Server
===================

The PUT endpoint allows you to update existing servers in the broadcast
list using the servers uid. The server uses
`RAET <https://github.com/RaetProtocol/raet>`__ to communicate. The
following fields can be used:

| **host\_address** - [string] ip address of server. *Required*
| **port** - [integer] server port to use. *Required*
| **name** - [string] name for the server. *Required*
| **main** - [boolean] The main parameter, if True, will allow that
  RoadStack to accept a vacuous join handshake from another RoadStack.
| **changed** - [ISO date string] date string for preventing replay
  attacks *Required*

Request
~~~~~~~

http PUT localhost:8000/relay/1 host\_address="127.0.0.1" port=7541
name="alpha" main=true changed="2000-01-01T00:00:00+00:00"

::

    PUT /relay/1 HTTP/1.1
    Accept: application/json, */*
    Accept-Encoding: gzip, deflate
    Connection: keep-alive
    Content-Length: 75
    Content-Type: application/json
    Host: localhost:8000
    User-Agent: HTTPie/0.9.9

    {
        "changed": "2000-01-01T00:00:00+00:00",
        "host_address": "127.0.0.1",
        "main": true,
        "name": "alpha",
        "port": 7541,
        "uid": "1"
    }

Response
~~~~~~~~

::

    HTTP/1.1 200 OK
    Content-Length: 109
    Content-Type: application/json; charset=UTF-8
    Date: Tue, 01 May 2018 01:26:19 GMT
    Server: Ioflo WSGI Server

    {
        "changed": "2000-01-01T00:00:00+00:00",
        "host_address": "127.0.0.1",
        "main": true,
        "name": "alpha",
        "port": 7541,
        "status": "connected",
        "uid": "1"
    }
