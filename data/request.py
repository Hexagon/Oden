import pymongo
from pymongo.objectid import ObjectId
import dbobject
import config
from data import people

class Request(dbobject.Base):
    def __init__(self):
        dbobject.Base.__init__(self)
        self.collection = self.db['request']
        self.debug = None

    # Creates a new person
    def new(self,from_id,to_id):

        # Construct profile (is to be included directly in the people object)
        request =   {
                    "from_id":ObjectId(from_id),
                    "to_id":ObjectId(to_id)
                    }

        # Try inserting object
        try:
            self.object_id = self.collection.insert(request)
            self.data = self.collection.find_one({"_id":self.object_id})
            return self.object_id
        except:
            self.debug = "Could not insert object ..."
            return False

    def to_xml(self):
        from_person = people.People().get_by_id(self.data[u'from_id'])
        to_person = people.People().get_by_id(self.data[u'to_id'])
        return "<XML><post><request><sender_handle>%s</sender_handle><recipient_handle>%s</recipient_handle></request></post></XML>" % (from_person[u'oden_handle'],to_person[u'oden_handle'])
        
    def remove(self):
        self.collection.remove(self.object_id)
        self.object_id = None
        self.data = None
        return True

