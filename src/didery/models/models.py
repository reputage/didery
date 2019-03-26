import arrow

try:
    import simplejson as json
except ImportError:
    import json

from copy import deepcopy


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
    def __init__(self, data, vk=None, mode="method", data_type="history"):
        DataModel.__init__(self, data)
        self.mode = mode
        self.vk = None
        self.index = None
        self.data_type = data_type

        if vk is not None:
            self.selected = vk

    @property
    def id(self):
        return self.data[self.index][self.data_type]['id']

    @property
    def changed(self):
        return self.data[self.index][self.data_type]['changed']

    @property
    def parsedChanged(self):
        return arrow.get(self.data[self.index][self.data_type]['changed'])

    @property
    def signer(self):
        return self.data[self.index][self.data_type]['signer']

    @property
    def signers(self):
        return self.data[self.index][self.data_type]['signers']

    @property
    def history(self):
        return self.data[self.index][self.data_type]

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
        if self.data is not None:
            for key, value in enumerate(self.data):
                if value is None:
                    continue

                initial_vk = value[self.data_type]['signers'][0]

                if initial_vk == vk:
                    return key

        return None


class ValidatedEventsModel(DataModel):
    def __init__(self, data, vk=None, mode="method"):
        self.mode = mode
        self.vk = vk
        self.index = None

        data = self.__convert(data)

        DataModel.__init__(self, data)

    def __convert(self, data):
        for rkey, rotations in enumerate(data):
            for ekey, event in enumerate(rotations):
                data[rkey][ekey] = ValidatedHistoryModel(event, data_type="event")

        return data

    def find(self, vk):
        """

        Args:
            vk: a rotation histories public key

        Returns: index

        """
        if self.data is not None:
            for key, history in enumerate(self.data):
                initial_vk = history[0].data['event']['signers'][0]

                if initial_vk == vk:
                    return key

        return None

    def toDict(self):
        data = deepcopy(self.data)

        for rkey, rotations in enumerate(data):
            for ekey, event in enumerate(rotations):
                data[rkey][ekey] = event.data

        return data

    def toList(self):
        return self.toDict()

    def toJson(self):
        data = self.toDict()

        return json.dumps(data)

    def toBytes(self):
        return self.toJson().encode()

    def fromJson(self, data):
        data = json.loads(data)

        self.data = self.__convert(data)

    def fromBytes(self, data):
        self.fromJson(data.decode())
