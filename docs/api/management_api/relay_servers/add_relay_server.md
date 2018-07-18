# Add Relay Server   
The POST endpoint allows you to add new servers to the broadcast list.  The server uses [RAET](https://github.com/RaetProtocol/raet) to communicate.  The following fields can be used:

__host_address__ - [string] ip address of server. *Required*   
__port__ - [integer] server port to use. *Required*   
__name__ - [string] name for the server. *Required*   
__main__ - [boolean] The main parameter, if True, will allow that RoadStack to accept a vacuous join handshake from another RoadStack.  
__changed__ - [ISO date string]  date string for preventing replay attacks *Required*  

### Request   
http POST localhost:8000/relay host_address="127.0.0.1" port=7541 name="alpha" main=true changed="2000-01-01T00:00:00+00:00"
```
POST /relay HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 77
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9

{
    "changed": "2000-01-01T00:00:00+00:00",
    "host_address": "127.0.0.1",
    "main": true,
    "name": "alpha",
    "port": "7541"
}
```
    
### Response  
```
HTTP/1.1 200 OK
Content-Length: 111
Content-Type: application/json; charset=UTF-8
Date: Tue, 01 May 2018 01:22:31 GMT
Server: Ioflo WSGI Server

{
    "changed": "2000-01-01T00:00:00+00:00",
    "host_address": "127.0.0.1",
    "main": true,
    "name": "alpha",
    "port": "7541",
    "status": "connected",
    "uid": "1"
}
```