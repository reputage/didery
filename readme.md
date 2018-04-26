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

#### Add Rotation History

```json
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
	
#### Get Rotation History

```json
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

```json
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

#### Add OTP Encrypted Key

```json
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
}    
```

#### Get Encrypted Key

```json
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
}
```

#### Get All Encrypted Keys

```json
{
    "data": [{
        "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
    },
    {
        "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
        "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw"
    }]
}
```
	
## Relay Servers

#### Add Relay Server
POST
```json
{
    "host_address": "127.0.0.1",
    "port": 7541,
    "name": "alpha",
    "main": true,
    "auto": true
}
```

#### Update Relay Server
PUT
```json
{
    "host_address": "127.0.0.1",
    "port": 7541,
    "name": "alpha",
    "main": true,
    "auto": true
}
```

#### Get All Relay Servers
GET
```json
{
    "1": {
        "host_address": "127.0.0.1",
        "port": 7541,
        "name": "alpha",
        "main": true,
        "uid": "1",
        "auto": true,
        "status": "connected",
    },
    "2": {
        "host_address": "127.0.0.1",
        "port": 7542,
        "name": "beta",
        "main": false,
        "uid": "2",
        "auto": true,
        "status": "connected",
    }
}
```

#### Delete Relay Server
A relay server can be deleted by sending and HTTP DELETE request with the uid of the relay server.
/relay/{uid} DELETE

## Error Logs

#### Get All Errors

```json
{
  "data": [
      {
          "title": "Invalid Signature.",
          "msg": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= had an invalid rotation signature.",
          "time": "2000-01-01T00:00:00+00:00"
      },
      {
          "title": "Relay Unreachable.",
          "msg": "Could not establish a connection with relay servers.",
          "time": "2000-01-01T11:00:00+00:00"
      }
  ]
}
```
