Error Types
===========

The API returns standard HTTP success or error status codes. If an error
occurs, extra information about what went wrong will be encoded in the
response as JSON. The various HTTP status codes we might return are
listed below.

HTTP Status codes
~~~~~~~~~~~~~~~~~

+--------+-------------------------+------------------------------------------+
| Code   | Title                   | Description                              |
+========+=========================+==========================================+
| 200    | OK                      | The request was successful.              |
+--------+-------------------------+------------------------------------------+
| 201    | Created                 | The resource was successfully created.   |
+--------+-------------------------+------------------------------------------+
| 400    | Bad Request             | Bad request                              |
+--------+-------------------------+------------------------------------------+
| 401    | Unauthorized            | Signature(s) verification failed.        |
+--------+-------------------------+------------------------------------------+
| 404    | Not found               | The resource does not exist.             |
+--------+-------------------------+------------------------------------------+
| 50X    | Internal Server Error   | An error occurred with our API.          |
+--------+-------------------------+------------------------------------------+

Error Types
~~~~~~~~~~~

All errors are returned in the form of JSON with a title and optional
description.

+-----------------------+----------------------------------------------------+
| Type                  | Description                                        |
+=======================+====================================================+
| Missing Required      | Error reading request body.                        |
| Field                 |                                                    |
+-----------------------+----------------------------------------------------+
| Request Error         | Could not decode the request body. The JSON was    |
|                       | incorrect.                                         |
+-----------------------+----------------------------------------------------+
| Malformed Query       | Problem with the url query string.                 |
| String                |                                                    |
+-----------------------+----------------------------------------------------+
| Validation Error      | Error validating the request body or request       |
|                       | header values.                                     |
+-----------------------+----------------------------------------------------+
| Resource Already      | Resource cannot be created twice.                  |
| Exists                |                                                    |
+-----------------------+----------------------------------------------------+
