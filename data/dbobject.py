import pymongo
from pymongo.objectid import ObjectId
import config

# This class is used as a base for all mongodb-related objects
class Base:
    def __init__(self):
        # Connect to the db
        try:
            self.connection = pymongo.Connection(config.mongo_host, config.mongo_port)
            self.db = self.connection[config.mongo_db]
            self.ready = True
        except:
            self.error = "Connection failure"
            self.ready = False

    # All documents should be searchable by id
    def get_by_id(self,_id):
        self.object_id = ObjectId(_id)
        self.data = self.collection.find_one({"_id":self.object_id})
        return self.data
