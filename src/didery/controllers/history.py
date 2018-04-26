import falcon
try:
    import simplejson as json
except ImportError:
    import json


class History:
    def __init__(self, store=None):
        """
        :param store: Store
            store is reference to ioflo data store
        """
        self.store = store

    def on_get(self, req, resp, did=None):
        """
        Handle and respond to incoming GET request.
        :param req: Request object
        :param resp: Response object
        :param did: string
            URL parameter specifying a rotation history
        """
        if did is not None:
            body = {
                "history":
                {
                    "id": did,
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
        else:
            body = {
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
                }, {
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

        resp.body = json.dumps(body, ensure_ascii=False)

    def on_post(self, req, resp):
        """
        Handle and respond to incoming POST request.
        :param req: Request object
        :param resp: Response object
        """
        result_json = req.body

        response_json = {
            "history": result_json,
            "signatures": [
                "AeYbsHot0pmdWAcgTo5sD8iAuSQAfnH5U6wiIGpVNJQQoYKBYrPPxAoIc1i5SHCIDS8KFFgf8i0tDq8XGizaCg==",
                "o9yjuKHHNJZFi0QD9K6Vpt6fP0XgXlj8z_4D-7s3CcYmuoWAh6NVtYaf_GWw_2sCrHBAA2mAEsml3thLmu50Dw=="
            ]
        }

        resp.body = json.dumps(response_json, ensure_ascii=False)
