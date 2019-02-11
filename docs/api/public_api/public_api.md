# Signature Header

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

An example is shown below where one *tag* is the string *signer* and the other *tag* is the string *rotation*.

```http
Signature: signer="Y5xTb0_jTzZYrf5SSEK2f3LSLwIwhOX7GEj6YfRWmGViKAesa08UkNWukUkPGuKuu-EAH5U-sdFPPboBAsjRBw=="; rotation="Xhh6WWGJGgjU5V-e57gj4HcJ87LLOhQr2Sqg5VToTSg-SI1W3A8lgISxOjAI5pa2qnonyz3tpGvC2cmf1VTpBg=="
```


Where tag is the name of a field in the body of the request whose value
is a DID from which the public key for the signature can be obtained.
If the same tag appears multiple times then only the last occurrence is used.

Each signature value is a doubly quoted string ```""``` that contains the actual signature
in Base64 url safe format. By default the signatures are 64 byte EdDSA (Ed25519) signatures that have been encoded into BASE64 url-file safe format. The encoded signatures are 88 characters in length and include two trailing pad characters ```=```.

The two tag field values currently supported are *signer* and *rotation*.

The didery python library has a helper function,

```python
parseSignatureHeader(signature)
```

in the

```python
didery.help.helping
```

that parses *Signature* header values and returns a python dictionary keyed by tags and whose values are the signatures provided in the header.


Example valid *Signature* headers are shown below:
```http
Signature: signer="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="; 

```

```http
Signature: signer="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="; rotation="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="

```

# Signature Schemes
An optional *tag* name = *scheme*. The *scheme* tag field value specifies the type of signature. All signatures within the header
must be of the same scheme. Currently the only supported signature type is *EdDSA(Ed25519)*. In the future we plan to also support *ECDSA(secp256k1)*. 

#### Scheme Values
```
EdDSA
Ed25519
```

```http
Signature: name="EdDSA"; signer="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="; rotation="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="
```

```http
Signature: name="Ed25519"; signer="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="; rotation="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="
```

# Key Revocation
For simplicity didery handles key revocation by rotating to the null key.  This is done by sending a rotation request to the didery server and setting the new pre rotated key to null. The "signer" index needs to point to the null key. As shown below the index jumps from 0 to 2 so that anyone who comes along later and verifies your keys with didery will see that you don't have a current valid key.

##### Existing Data
Suppose the didery servers already have this data.
```
[
    {
        "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "changed": "2000-01-01T00:00:00+00:00",
        "signer": 0,
        "signers": 
        [
            "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
            "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148="
        ]
    }
]
```
##### Rotation Event Data
In order to revoke a key a PUT request would be sent with data that looked something like this:
```
[
    {
        "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "changed": "2000-01-01T00:00:01+00:00",
        "signer": 2,
        "signers": 
        [
            "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
            "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
            null
        ]
    }
]
```
### Signatures
Accompanying the PUT request should be a normal signature header as if you were rotating to the pre-rotated key "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=".
```http
Signature: signer="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="; rotation="B0Qc72RP5IOodsQRQ_s4MKMNe0PIAqwjKsBl4b6lK9co2XPZHLmzQFHWzjA2PvxWso09cEkEHIeet5pjFhLUDg=="
```


# Replay Attack Prevention 
Although all resource write requests are signed by the client and therefore can not be created by anyone other than the Keeper of the associated private key, a malicious network device could record and resend prior requests in a different order (replay attack) and thereby change the state of the database. To prevent replay attacks on requests that change data resources a client needs to authenticate in a time sensitive manner with the server.  A simple way to do this is for the client to update the *changed* date time stamp field in the resource in a monotonically increasing manner. This way any replayed but stale write requests can be detected and refused by the Server. In other words the server will deny write requests whose *changed* field date time stamp is not later than the the *changed* field value of the pre-existing resource to be updated.

# Errors
The API returns standard HTTP success or error status codes. If an error occurs, extra information about what went wrong will be encoded in the response as JSON. The various HTTP status codes we might return are listed below.

### HTTP Status codes
| Code | Title                 | Description                                             |
|------|-----------------------|---------------------------------------------------------|
| 200  | OK                    | The request was successful.                             |
| 201  | Created               | The resource was successfully created.                  |
| 400  | Bad Request           | Bad request                                             |
| 401  | Unauthorized          | Signature(s) verification failed.                       |
| 404  | Not found             | The resource does not exist.                            |
| 409  | Resource Conflict     | State of the resource doesn't permit request.           |
| 50X  | Internal Server Error | An error occurred with our API.                         |

### Error Types
All errors are returned in the form of JSON with a title and optional description.
   
| Type                    | Description                                                 |   
|-------------------------|-------------------------------------------------------------|   
| Missing Required Field  | Error reading request body.                                 |   
| Request Error           | Could not decode the request body. The JSON was incorrect.  |   
| Malformed Query String  | Problem with the url query string.                          |   
| Validation Error        | Error validating the request body or request header values. |   
| Authorization Error     | Error validating request signatures.                        |   
| Resource Already Exists | Resource cannot be created twice.                           |
| Deletion Error          | Error while attempting to delete the resource.              |   

# Key Rotation History 
This endpoint is meant for storing the rotation history of public keys for a particular did.  It stores the entire rotation history and a signature from both the current private key and the pre rotated private key.  

# Add Rotation History (POST)   
The POST endpoint can be used for adding new rotation histories.  There can be only one inception event per did.  All updates must be sent through the PUT endpoint.  Each request should have a Signature field in its header with the following format: signer=["signature"]. The signer tag contains the signature from the private key corresponding to the public key at position 0 in the signers field. Each request should also include the following fields:

__id__ - [string] decentralized identifier [(DID)](https://w3c-ccg.github.io/did-spec/)  *Required*  
__changed__ - [string] date changed. Mitigates replay attacks *Required*     
__signer__ - [integer] 0 based index into signers field. Must be 0 on POST requests *Required*    
__signers__ - [list/array] list of all public keys. Must contain at least two keys. *Required*      


##### Request    
http POST localhost:8000/history id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" changed="2000-01-01T00:00:00+00:00" signer=0 signers="['Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=', 'Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=']"
```
POST /history HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 324
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9
Signature: signer="AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg=="
    
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
    "changed": "2000-01-01T00:00:00+00:00",
    "signer": 0,
    "signers": 
    [
        "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148="
    ]
}
```

##### Response   
```
HTTP/1.1 200 OK
Content-Length: 535
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:03:01 GMT
Server: Ioflo WSGI Server

[
    {
        "history": {
            "changed": "2000-01-01T00:00:00+00:00",
            "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
            "signer": "0",
            "signers": [
                "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148="
            ]
        },
        "signatures": [
            "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg=="
        ]
    }
]
```

# Rotation Event (PUT)
The PUT endpoint is used for validating and storing rotation events.  The resource must already exist or a 404 error will be returned. Previously used public keys in the rotation history cannot be changed only new pre-rotated keys can be added through this endpoint. Each request should have a Signature field in its header with the following format: signer=["signature"]; rotation=["signature"].  The signer tag should contain the signature of the old public/private key pair and the rotation tag should contain the signature of the new public/private key pair. Each request should also include the following fields:

__id__ - [string] decentralized identifier [(DID)](https://w3c-ccg.github.io/did-spec/)  *Required*  
__changed__ - [string] date changed. Mitigates replay attacks *Required*     
__signer__ - [integer] 0 based index into signers field. PUT requests signer field will always be 1 or greater *Required*    
__signers__ - [list/array] list of all public keys. Must contain at least two keys. *Required*      


##### Request    
http PUT localhost:8000/history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" changed="2000-01-01T00:00:00+00:00" signer=1 signers="['Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=', 'Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=', 'dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=']"
```
PUT /history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 324
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9
Signature: signer="AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg=="; rotation="o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
    
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
    "changed": "2000-01-01T00:00:00+00:00",
    "signer": 1,
    "signers": 
    [
        "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
        "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
        "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
    ]
}
```

##### Response  
```
HTTP/1.1 200 OK
Content-Length: 535
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:03:01 GMT
Server: Ioflo WSGI Server

[
    {
        "history": {
            "changed": "2000-01-01T00:00:00+00:00",
            "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
            "signer": "1",
            "signers": [
                "Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                "Xq5YqaL6L48pf0fu7IUhL0JRaU2_RxFP0AL43wYn148=",
                "dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
            ]
        },
        "signatures":
        [
            "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
            "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
        ]
    }
]
```
	
# Get Rotation History (GET)

##### Request   
http localhost:8000/history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=
```
GET /history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9

```

##### Response
```
HTTP/1.1 200 OK
Content-Length: 533
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:11:20 GMT
Server: Ioflo WSGI Server

[
    {
        "history":
        {
            "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
            "changed": "2000-01-01T00:00:00+00:00",
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
]
```

# Get All Rotation Histories (GET)

##### Request   
http localhost:8000/history
```
GET /history HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

##### Response  
```
HTTP/1.1 200 OK
Content-Length: 1032
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:20:39 GMT
Server: Ioflo WSGI Server
    
{
    "data": [
        [
            {
                "history":
                {
                    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                    "changed": "2000-01-01T00:00:00+00:00",
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
        ],
        [
            {
                "history":
                {
                    "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY=",
                    "changed": "2000-01-01T00:00:00+00:00",
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
            }
        ]
    ]
}
```

# Delete Rotation History (DELETE)
To comply with GDPR a delete history option is provided.  In order to prevent bad actors from deleting the database a signature using the current signing key pair is required to delete the history. Each request must include the histories did in the body.

__id__ - [string] decentralized identifier [(DID)](https://w3c-ccg.github.io/did-spec/) *Required*

##### Request   
```
DELETE /history/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 246
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9
    
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
}
```

##### Response   
```
HTTP/1.1 200 OK
Content-Length: 246
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:27:27 GMT
Server: Ioflo WSGI Server
    
{
    "deleted": [ 
        {
            "history": {
                "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=",
                "changed": "2000-01-01T00:00:00+00:00",
                "signer": 2,
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
    ]
}

```

# OTP Encrypted Private Key Store  
This endpoint stores one time pad(otp) encrypted private keys for later recovery if a key is lost. The resources are identified by their [(DID)](https://w3c-ccg.github.io/did-spec/).  The endpoint requires a signature in the header of POST and PUT requests for verification purposes.  The signature should be created by the private key that corresponds to the did in the request.  The endpoint will use the public key stored in the did to verify the signature.

# Add OTP Encrypted Key (POST)
The POST endpoint can be used for storing new otp encrypted blobs. Each request should include the following fields:

__id__ - [string] decentralized identifier [(DID)](https://w3c-ccg.github.io/did-spec/) *Required*    
__blob__ - [string] otp encrypted private keys *Required*    
__changed__ - [date string]  date string for preventing replay attacks *Required*  

##### Request   
http POST localhost:8000/blob id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" blob="AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw" changed="2000-01-01T00:00:00+00:00"
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
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
    "changed": "2000-01-01T00:00:00+00:00",
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
}
```

##### Response   
```
HTTP/1.1 200 OK
Content-Length: 246
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:27:27 GMT
Server: Ioflo WSGI Server
    
{
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
    "changed": "2000-01-01T00:00:00+00:00",
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
}

```

# Update OTP Encrypted Key (PUT)
The PUT endpoint can be used for updating otp encrypted blobs. Each request should include the following fields:

__id__ - [string] decentralized identifier [(DID)](https://w3c-ccg.github.io/did-spec/) *Required*    
__blob__ - [string] otp encrypted private keys *Required*  
__changed__ - [date string]  date string for preventing replay attacks *Required*  

##### Request   
http PUT localhost:8000/blob/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= id="did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=" blob="AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw" changed="2000-01-01T00:00:00+00:00"
```
PUT /blob HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 246
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9
    
{
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
    "changed": "2000-01-01T00:00:00+00:00",
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
}
```

##### Response   
```
HTTP/1.1 200 OK
Content-Length: 246
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:27:27 GMT
Server: Ioflo WSGI Server
    
{
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
    "changed": "2000-01-01T00:00:00+00:00",
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
}

```

# Get Encrypted Key (GET)

##### Request    
http localhost:8000/blob/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE=
```
GET /blob/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

##### Response  
```
HTTP/1.1 200 OK
Content-Length: 246
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:30:04 GMT
Server: Ioflo WSGI Server
    
{
    "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
    "changed": "2000-01-01T00:00:00+00:00",
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
}
```

# Get All Encrypted Keys (GET)

##### Request   
http localhost:8000/blob
```
GET /blob HTTP/1.1
Accept: */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Host: localhost:8000
User-Agent: HTTPie/0.9.9
```

##### Response  
```
HTTP/1.1 200 OK
Content-Length: 506
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:32:04 GMT
Server: Ioflo WSGI Server
    
{
    "data": [
        {
            "otp_data": {
                "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
                "changed": "2000-01-01T00:00:00+00:00",
                "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
            },
            "signature": [
                "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw==" 
            ]
        },
        {
            "otp_data": {
                "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
                "changed": "2000-01-01T00:00:00+00:00",
                "id": "did:igo:dZ74MLZXD-1QHoa73w9pQ9GroAvxqFi2RTZWlkC0raY="
            },
            "signature": [
                "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw==" 
            ]
        }
    ]
}
```

# Delete OTP Encrypted Key (DELETE)
To comply with GDPR a delete otp blob option is provided.  In order to prevent bad actors from deleting the database a signature using the current signing key pair is required to delete the otp blob. Each request must include the blob's did in the body.

__id__ - [string] decentralized identifier [(DID)](https://w3c-ccg.github.io/did-spec/) *Required*

##### Request   
```
DELETE /blob/did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE= HTTP/1.1
Accept: application/json, */*
Accept-Encoding: gzip, deflate
Connection: keep-alive
Content-Length: 246
Content-Type: application/json
Host: localhost:8000
User-Agent: HTTPie/0.9.9
    
{
    "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
}
```

##### Response   
```
HTTP/1.1 200 OK
Content-Length: 246
Content-Type: application/json; charset=UTF-8
Date: Mon, 30 Apr 2018 23:27:27 GMT
Server: Ioflo WSGI Server
    
{
    "deleted": {
        "otp_data": {
            "blob": "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCgo9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw",
            "changed": "2000-01-01T00:00:00+00:00",
            "id": "did:dad:Qt27fThWoNZsa88VrTkep6H-4HA8tr54sHON1vWl6FE="
        },
        "signature": [
            "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw==" 
        ]
    }
}

```