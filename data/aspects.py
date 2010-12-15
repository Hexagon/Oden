import pymongo
import dbobject
import datetime
import handlers.helper
import config

class Aspects(dbobject.Base):
    def __init__(self):
        dbobject.Base.__init__(self)
        self.collection = self.db['aspects']
        self.debug = None

        # Specify what data is to be included in federation

    # Creates a new aspect
    def new(self,name,user_id):

        # Construct profile (is to be included directly in the people object)
        aspect =   {
                    "name":name,
                    "user_id":user_id,
                    "created_at":datetime.datetime.utcnow(),
                    "updated_at":datetime.datetime.utcnow(),
                    "post_ids":[],
                    "request_ids":[]
                    }

        # Try inserting object
        try:
            self.object_id = self.collection.insert(aspect)
            self.data = self.collection.find_one({"_id":self.object_id})
            return self.object_id
        except:
            self.debug = "Could not insert object ..."
            return False

    # Fetch all aspect object by the owners user id
    def get_all_by_user_id(self,_uid):
        self.data = self.collection.find({"user_id":_uid})
        if self.data != None:
            self.object_id = []
            for aspect in self.data:
                self.object_id.append(aspect[u'_id'])
            self.data.rewind()
        return self.data

    # Delete the current aspect
    def delete(self):
        if self.data != None:
            self.collection.remove(self.data)
            self.object_id = None
            self.data = None
            return True
        else:
            return False
