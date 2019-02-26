class DBMock:
    def __init__(self, db_data):
        """
        :param db_data: dict
            mock data
        """
        self.db_data = db_data

    def count(self):
        """
            Gets a count of the number of entries in the table

            :return: int count
        """
        return len(self.db_data)

    def save(self, key, data):
        """
            Store a key value pair

            :param key: string
                key to identify data
            :param data: dict
                A dict of the data to be stored

        """

    def get(self, key):
        """
            Find and return a key value pair

            :param key: string
                key to look up
            :return: dict
        """
        return self.db_data[key]

    def getAll(self, offset=0, limit=10):
        """
            Get all key value pairs in a range between the offset and offset+limit

            :param offset: int starting point of the range
            :param limit: int maximum number of entries to return
            :return: dict
        """
        values = {"data": []}
        for key, value in self.db_data.items():
            values["data"].append(value)

        return values

    def delete(self, key):
        """
            Find and delete a key value pair matching the supplied key.

            :param key: string
                key to delete
            :return: boolean
        """
        return self.db_data.pop(key, False)
