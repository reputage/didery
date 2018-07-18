# Get All Relay Servers

### Request   
http localhost:8000/relay
```
GET /relay HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

### Response  
```
HTTP/1.1 200 OK
Content-Length: 232
Content-Type: application/json; charset=UTF-8
Date: Tue, 01 May 2018 01:29:12 GMT
Server: Ioflo WSGI Server

{
    "1": {
        "changed": "2000-01-01T00:00:00+00:00",
        "host address": "127.0.0.1",
        "main": true,
        "name": "alpha",
        "port": 7541,
        "status": "connected",
        "uid": "1"
    },
    "2": {
        "changed": "2000-01-01T00:00:00+00:00",
        "host address": "127.0.0.1",
        "main": false,
        "name": "beta",
        "port": 7542,
        "status": "connected",
        "uid": "2"
    }
}
```