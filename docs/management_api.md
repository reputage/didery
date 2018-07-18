## Authentication
Requests are authenticated using HTTP Basic Auth. Provide your API key as the basic auth username. You do not need to provide a password.

Alternatively you can also pass your API key as a bearer token in an Authorization header.

## Errors
The API returns standard HTTP success or error status codes. If an error occurs, extra information about what went wrong will be encoded in the response as JSON. The various HTTP status codes we might return are listed below.

### HTTP Status codes
| Code | Title                 | Description                            |
|------|-----------------------|----------------------------------------|
| 200  | OK                    | The request was successful.            |
| 201  | Created               | The resource was successfully created. |
| 400  | Bad Request           | Bad request                            |
| 401  | Unauthorized          | Signature(s) verification failed.      |
| 404  | Not found             | The resource does not exist.           |
| 50X  | Internal Server Error | An error occurred with our API.        |

### Error Types
All errors are returned in the form of JSON with a title and optional description.
   
| Type                    | Description                                                 |   
|-------------------------|-------------------------------------------------------------|   
| Missing Required Field  | Error reading request body.                                 |   
| Request Error           | Could not decode the request body. The JSON was incorrect.  |   
| Malformed Query String  | Problem with the url query string.                          |   
| Validation Error        | Error validating the request body or request header values. |   
| Resource Already Exists | Resource cannot be created twice.                           |   

## Relay Servers    
This endpoint is just for managing the back end.  This allows you to tell the server to broadcast updates to other trusted servers.

#### Add Relay Server   
The POST endpoint allows you to add new servers to the broadcast list.  The server uses [RAET](https://github.com/RaetProtocol/raet) to communicate.  The following fields can be used:

__host_address__ - [string] ip address of server. *Required*   
__port__ - [integer] server port to use. *Required*   
__name__ - [string] name for the server. *Required*   
__main__ - [boolean] The main parameter, if True, will allow that RoadStack to accept a vacuous join handshake from another RoadStack.  
__changed__ - [ISO date string]  date string for preventing replay attacks *Required*  

##### Request   
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
    
##### Response  
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

#### Update Relay Server
The PUT endpoint allows you to update existing servers in the broadcast list using the servers uid.  The server uses [RAET](https://github.com/RaetProtocol/raet) to communicate.  The following fields can be used:

__host_address__ - [string] ip address of server. *Required*   
__port__ - [integer] server port to use. *Required*   
__name__ - [string] name for the server. *Required*   
__main__ - [boolean] The main parameter, if True, will allow that RoadStack to accept a vacuous join handshake from another RoadStack.  
__changed__ - [ISO date string]  date string for preventing replay attacks *Required*  


##### Request   
http PUT localhost:8000/relay/1 host_address="127.0.0.1" port=7541 name="alpha" main=true changed="2000-01-01T00:00:00+00:00"
```
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
```

##### Response  
```
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
```

#### Get All Relay Servers

##### Request   
http localhost:8000/relay
```
GET /relay HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

##### Response  
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

#### Delete Relay Server    
A relay server can be deleted by sending and HTTP DELETE request with the uid of the relay server.
/relay/{uid} DELETE

##### Request   
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

##### Response   
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

## Error Logs   
Provides a snapshot of errors encountered on the server

#### Get All Errors

##### Request    
http localhost:8000/errors
```
GET /errors HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

##### Response   
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