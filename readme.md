Requests
========

## Signature Header

didery service requests or responses may require a custom *Signature* header that provides one or more signatures of the request/response body text.

The format of the custom Signature header follows the conventions of [RFC 7230](https://tools.ietf.org/html/rfc7230)

Signature header has format:

```http
Signature: headervalue

Headervalue:
  tag = "signature"
or
  tag = "signature"; tag = "signature"  ...
  
where tag is replaced with a unique string for each signature value
```

An example is shown below where one *tag* is the string *signer* and the other *tag* is the string *current*.

```http
Signature: signer="Y5xTb0_jTzZYrf5SSEK2f3LSLwIwhOX7GEj6YfRWmGViKAesa08UkNWukUkPGuKuu-EAH5U-sdFPPboBAsjRBw=="; current="Xhh6WWGJGgjU5V-e57gj4HcJ87LLOhQr2Sqg5VToTSg-SI1W3A8lgISxOjAI5pa2qnonyz3tpGvC2cmf1VTpBg=="
```


Where tag is the name of a field in the body of the request whose value
is a DID from which the public key for the signature can be obtained.
If the same tag appears multiple times then only the last occurrence is used.

Each signature value is a doubly quoted string ```""``` that contains the actual signature
in Base64 url safe format. By default the signatures are 64 byte EdDSA (Ed25519) signatures that have been encoded into BASE64 url-file safe format. The encoded signatures are 88 characters in length and include two trailing pad characters ```=```.

An optional *tag* name = *kind* with values *EdDSA* or *Ed25519* may be present.
The *kind* tag field value specifies the type of signature. All signatures within the header
must be of the same kind.

The two tag field values currently supported are *did* and *signer*.

The bluepea python library has a helper function,

```python
parseSignatureHeader(signature)
```

in the

```python
bluepea.help.helping
```

that parses *Signature* header values and returns a python dictionary keyed by tags and whose values are the signatures provided in the header.


Example valid *Signature* headers are shown below:

```http
Signature: did="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="

```

```http
Signature: signer="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="; 

```

```http
Signature: signer="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="; did="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="

```

```http
Signature: signer="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="; did="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="; kind="EdDSA"

```

## Replay Attack Prevention

Although all resource write requests are signed by the client and therefore can not be created by anyone other than the Keeper of the associated private key, a malicious network device could record and resend prior requests in a different order (replay attack) and thereby change the state of the database. To prevent replay attacks on requests that change data resources a client needs to authenticate in a time sensitive manner with the server.  A simple way to do this is for the client to update the *changed* date time stamp field in the resource in a monotonically increasing manner. This way any replayed but stale write requests can be detected and refused by the Server. In other words the server will deny write requests whose *changed* field date time stamp is not later than the the *changed* field value of the pre-existing resource to be updated.

API
===

## Endpoint URL Summary

The API consists of several ReST endpoints grouped according to the type of data resource that is being manipulated by the API. Each resource has HTTP verbs that do the manipulation.

/history  POST   [api](#add-rotation-history)             
/history/{did} GET [api](#get-rotation-history)        
/history GET [api](#get-all-rotation-histories)    

/blob POST [api](#add-otp-encrypted-key)    
/blob/{did} GET [api](#get-encrypted-key)   
/blob GET [api](#get-all-encrypted-keys)

/relay POST [api](#add-relay-server)    
/relay/{uid} PUT [api](#update-relay-server)    
/relay GET [api](#get-all-relay-servers)    
/relay/{uid} DELETE [api](#delete-relay-server) 

/errors GET [api](#get-all-errors)  

## Key Rotation History
This endpoint is meant for storing the rotation history of public keys for a particular did.  It stores the entire rotation history and a signature from both the current private key and the pre rotated private key.
#### Add Rotation History
The POST endpoint can be used for adding new rotation histories.  Each request should include the following fields:

__id__ - [string] decentralized identifier [(DID)](https://w3c-ccg.github.io/did-spec/)  *Required*  
__changed__ - [string] date changed. Mitigates replay attacks *Required*     
__signer__ - [integer] 0 based index into signers field *Required*    
__signers__ - [list/array] list of all public keys. Must contain at least two keys. *Required*      


#####Request
http POST localhost:8000/history id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" changed="2000-01-01T00:00:00+00:00" signer=2 signers="['Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=', 'Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=', 'dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=', '3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA=']"
```
POST /history HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 324
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9
    
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
    "changed" : "2000-01-01T00:00:00+00:00",
    "signer": 2,
    "signers": 
    [
        "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
        "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
    ]
}
```

#####Response
```
HTTP/1.1 200 OK
Content-Length: 535
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:03:01 GMT
Server: Ioflo WSGI Server

{
    "history": {
        "changed": "2000-01-01T00:00:00+00:00",
        "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "signer": "2",
        "signers": [
            "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
            "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
            "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
            "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
        ]
    },
    "signatures": [
        "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
        "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
    ]
}
```
	
#### Get Rotation History

#####Request
http localhost:8000/history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=
```
GET /history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9

```

#####Response
```
HTTP/1.1 200 OK
Content-Length: 533
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:11:20 GMT
Server: Ioflo WSGI Server

    
{
    "history":
    {
        "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "changed" : "2000-01-01T00:00:00+00:00",
        "signer": 2,
        "signers": 
        [
            "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
            "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
            "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
            "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
        ]
    },
    "signatures":
    [
        "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
        "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
    ]
}
```

#### Get All Rotation Histories

#####Request
http localhost:8000/history
```
GET /history HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

#####Response
```
HTTP/1.1 200 OK
Content-Length: 1032
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:20:39 GMT
Server: Ioflo WSGI Server
    
{
    "data": [{
        "history":
        {
            "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
            "changed" : "2000-01-01T00:00:00+00:00",
            "signer": 2,
            "signers": 
            [
                "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                "3syVH2woCpOvPF0SD9Z0bu_OxNe2ZgxKjTQ961LlMnA="
            ]
        },
        "signatures":
        [
            "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
            "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
        ]
    },
    {
        "history":
        {
            "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
            "changed" : "2000-01-01T00:00:00+00:00",
            "signer": 1,
            "signers": 
            [
                "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
            ]
        },
        "signatures":
        [
            "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw==",
            "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
        ]
    }]
}
```

## OTP Encrypted Private Key Store
This endpoint stores one time pad(otp) encrypted private keys for later recovery if a key is lost. The DID and the encrypted text blob are the only parameters.

#### Add OTP Encrypted Key
The POST endpoint can be used for storing new otp encrypted blobs. Each request should include the following fields:

__id__ - [string] decentralized identifier [(DID)](https://w3c-ccg.github.io/did-spec/) *Required*    
__blob__ - [string] otp encrypted private keys *Required*    

#####Request
http POST localhost:8000/blob id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" blob="AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
```
POST /blob HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 246
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9
    
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
}
```

#####Response
```
HTTP/1.1 200 OK
Content-Length: 246
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:27:27 GMT
Server: Ioflo WSGI Server
    
{
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
}

```

#### Get Encrypted Key

#####Request
http localhost:8000/blob/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=
```
GET /blob/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

#####Response
```
HTTP/1.1 200 OK
Content-Length: 246
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:30:04 GMT
Server: Ioflo WSGI Server
    
{
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
}
```

#### Get All Encrypted Keys

#####Request
http localhost:8000/blob
```
GET /blob HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

#####Response
```
HTTP/1.1 200 OK
Content-Length: 506
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:32:04 GMT
Server: Ioflo WSGI Server
    
{
    "data": [
        {
            "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
            "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
        },
        {
            "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
            "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
        }
    ]
}
```
	
## Relay Servers
This endpoint is just for managing the back end.  This allows you to tell the server to broadcast updates to other trusted servers.

#### Add Relay Server
The POST endpoint allows you to add new servers to the broadcast list.  The server uses [RAET](https://github.com/RaetProtocol/raet) to communicate.  The following fields can be used:

__host_address__ - [string] ip address of server. *Required*   
__port__ - [integer] server port to use. *Required*   
__name__ - [string] name for the server. *Required*   
__main__ - [boolean] The main parameter, if True, will allow that RoadStack to accept a vacuous join handshake from another RoadStack.

#####Request
http POST localhost:8000/relay host_address="127.0.0.1" port=7541 name="alpha" main=true
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
    "host_address": "127.0.0.1",
    "main": true,
    "name": "alpha",
    "port": "7541"
}
```
    
#####Response
```
HTTP/1.1 200 OK
Content-Length: 111
Content-Type: application/json; charset=UTF-8
Date: Tue, 01 May 2018 01:22:31 GMT
Server: Ioflo WSGI Server

{
    "host_address": "127.0.0.1",
    "main": true,
    "name": "alpha",
    "port": "7541",
    "status": "connected",
    "uid": "1"
}
```

#### Update Relay Server

#####Request
http PUT localhost:8000/relay/1 host_address="127.0.0.1" port=7541 name="alpha" main=true
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
    "host_address": "127.0.0.1",
    "main": true,
    "name": "alpha",
    "port": 7541
}
```

#####Response
```
HTTP/1.1 200 OK
Content-Length: 109
Content-Type: application/json; charset=UTF-8
Date: Tue, 01 May 2018 01:26:19 GMT
Server: Ioflo WSGI Server

{
    "host_address": "127.0.0.1",
    "main": true,
    "name": "alpha",
    "port": 7541,
    "status": "connected",
    "uid": "1"
}
```

#### Get All Relay Servers

#####Request
http localhost:8000/relay
```
GET /relay HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

#####Response
```
HTTP/1.1 200 OK
Content-Length: 232
Content-Type: application/json; charset=UTF-8
Date: Tue, 01 May 2018 01:29:12 GMT
Server: Ioflo WSGI Server

{
    "1": {
        "host address": "127.0.0.1",
        "main": true,
        "name": "alpha",
        "port": 7541,
        "status": "connected",
        "uid": "1"
    },
    "2": {
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

#####Request
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

#####Response
```
HTTP/1.1 200 OK
Content-Length: 113
Content-Type: application/json; charset=UTF-8
Date: Tue, 01 May 2018 01:31:46 GMT
Server: Ioflo WSGI Server

{
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

#####Request
http localhost:8000/errors
```
GET /errors HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

#####Response
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
