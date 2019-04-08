from ..didering import Did


class Dad(Did):
    def __init__(self, did_reference):
        Did.__init__(self, did_reference)
        self.vk = self.idString
