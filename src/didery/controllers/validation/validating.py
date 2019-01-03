class Validator:
    def __init__(self):
        pass

    def validate(self, data):
        """
        Validates data, raises Falcon.HTTPError if validation fails.

        :param data: (dict) data items
        :return: None
        """
        pass


class HasSignatureValidator(Validator):
    def __init__(self):
        Validator.__init__(self)

    def validate(self, data):
        pass
