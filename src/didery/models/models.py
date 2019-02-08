import arrow

try:
    import simplejson as json
except ImportError:
    import json


class DataModel:
    def __init__(self, data):
        """

        Args:
            data: dict
        """
        self.data = data

    def toJson(self):
        return json.dumps(self.data)

    def toBytes(self):
        return json.dumps(self.data).encode()

    def fromJson(self, data):
        self.data = json.loads(data)

    def fromBytes(self, data):
        self.data = json.loads(data.decode())


class BasicHistoryModel(DataModel):
    def __init__(self, data):
        DataModel.__init__(self, data)

    @property
    def id(self):
        return self.data['id']

    @property
    def changed(self):
        return self.data['changed']

    @property
    def parsedChanged(self):
        return arrow.get(self.data['changed'])

    @property
    def signer(self):
        return self.data['signer']

    @property
    def signers(self):
        return self.data['signers']

    @property
    def history(self):
        return self.data


class ValidatedHistoryModel(DataModel):
    def __init__(self, data, vk=None, mode="method"):
        DataModel.__init__(self, data)
        self.mode = mode
        self.vk = None
        self.index = None

        if vk is not None:
            self.selected = vk

    @property
    def id(self):
        return self.data[self.index]['history']['id']

    @property
    def changed(self):
        return self.data[self.index]['history']['changed']

    @property
    def parsedChanged(self):
        return arrow.get(self.data[self.index]['history']['changed'])

    @property
    def signer(self):
        return self.data[self.index]['history']['signer']

    @property
    def signers(self):
        return self.data[self.index]['history']['signers']

    @property
    def history(self):
        return self.data[self.index]['history']

    @property
    def signatures(self):
        return self.data[self.index]['signatures']

    @property
    def selected(self):
        return self.data[self.index]

    @selected.setter
    def selected(self, vk):
        self.vk = vk

        self.index = self.find(vk)

    def update(self, index, update):
        if index >= len(self.data):
            return

        self.data[index] = update

        if self.vk is not None:
            self.selected = self.vk

    def find(self, vk):
        index = None

        if self.data is None:
            return

        for key, value in enumerate(self.data):
            if value is not None and value['history']['signers'][0] == vk:
                index = key
                break

        return index


class EventsModel(DataModel):
    def __init__(self, data, mode="method"):
        DataModel.__init__(self, data)
        self.mode = mode
