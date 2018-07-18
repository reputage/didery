# Get All Errors

### Request    
http localhost:8000/errors
```
GET /errors HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

### Response   
```
HTTP/1.1 200 OK
Content-Length: 311
Content-Type: application/json; charset=UTF-8
Date: Tue, 01 May 2018 01:33:05 GMT
Server: Ioflo WSGI Server

{
    "data": [
        {
            "msg": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= had an invalid rotation signature.",
            "time": "2000-01-01T00:00:00+00:00",
            "title": "Invalid Signature."
        },
        {
            "msg": "Could not establish a connection with relay servers.",
            "time": "2000-01-01T11:00:00+00:00",
            "title": "Relay Unreachable."
        }
    ]
}
```