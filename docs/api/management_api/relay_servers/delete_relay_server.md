# Delete Relay Server    
A relay server can be deleted by sending and HTTP DELETE request with the uid of the relay server.
/relay/{uid} DELETE

### Request   
http DELETE localhost:8000/relay/10
```
DELETE /relay/10 HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 0
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

### Response   
```
HTTP/1.1 200 OK
Content-Length: 113
Content-Type: application/json; charset=UTF-8
Date: Tue, 01 May 2018 01:31:46 GMT
Server: Ioflo WSGI Server

{
    "changed": "2000-01-01T00:00:00+00:00",
    "host_address": "127.0.0.1",
    "main": true,
    "name": "alpha",
    "port": 7541,
    "status": "disconnected",
    "uid": "10"
}
```