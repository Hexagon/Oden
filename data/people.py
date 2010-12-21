import pymongo
import crypt
import base64
import dbobject
import datetime
import handlers.helper
import config
from lib.oden import webfinger

class People(dbobject.Base):
    def __init__(self):
        dbobject.Base.__init__(self)
        self.collection = self.db['people']
        self.debug = None

        self.xml_attr = ['_id','diaspora_handle','url','profile']

    # Creates a new person
    def new(self,user_id,oden_handle,serialized_public_key,pod_url,   # Mandatory
            searchable=True,image_url=None,gender=""                        # Optionals
            ,birthday=None,last_name="",first_name="",bio="",guid=None):

        # Construct profile (is to be included directly in the people object)
        profile =   {
                    "searchable":searchable,
                    "image_url":image_url,
                    "image_url_medium":image_url,
                    "image_url_small":image_url,
                    "gender":gender,
                    "oden_handle":oden_handle,
                    "birthday":birthday,
                    "last_name":last_name,
                    "first_name":first_name,
                    "bio":bio
                    }

        # Construct people document
        people =    {
                    "owner_id":user_id,
                    "created_at":datetime.datetime.utcnow(),
                    "profile":  profile,
                    "updated_at":datetime.datetime.utcnow(),
                    "url":pod_url,
                    "serialized_public_key":serialized_public_key,
                    "oden_handle":oden_handle
                    }

        # Add GUID if specified
        if guid != None:
            people[u'_id'] = pymongo.objectid.ObjectId(guid)

        # Try inserting object
        try:
            self.object_id = self.collection.insert(people)
            self.data = self.collection.find_one({"_id":self.object_id})
            return self.object_id
        except:
            self.debug = "Could not insert object ..."
            return False

    # Fetch a people object by handle
    def get_by_handle(self,_handle,is_retry=False):
        self.data = self.collection.find_one({"oden_handle":_handle.lower().strip()})
        if self.data != None:
            self.object_id = self.data[u'_id']
        elif not is_retry:
            # If person is not found, webfinger the uri and try again
            mock_res = self.build_from_webfinger(_handle.lower().strip())
            return self.get_by_handle(_handle,True)

        return self.data

    # Fetch a people object by owners user id
    def get_by_user_id(self,_uid):
        self.data = self.collection.find_one({"owner_id":pymongo.objectid.ObjectId(_uid)})
        if self.data != None:
            self.object_id = self.data[u'_id']
        return self.data

    # Get full name if existant, else nickname
    def get_full_name_or_nickname(self):
        if self.data != None:
            if  ((self.data[u'profile'][u'first_name'] == "" 
                and self.data[u'profile'][u'last_name'] == "") or (self.data[u'profile'][u'first_name'] == None 
                and self.data[u'profile'][u'last_name'] == None)):
                return self.get_username()
            else:
                return self.data[u'profile'][u'first_name'].strip() + " " + self.data[u'profile'][u'last_name'].strip()

    # Get username directly from people object
    def get_username(self):
        if self.data != None:
            return self.data[u'oden_handle'].split("@%s" % (config.pod_domain))[0].strip().lower()
        else:
            return None

    # Construct a people object by webfinger
    def build_from_webfinger(self,uri):
    	wf_obj = webfinger.Webfinger()
        wf = wf_obj.finger(uri)
        if wf == None:
            print "DEBUG: " + wf_obj.error
            return None
        elif wf.valid:
            if wf.hcard_searchable == "true":
                wf.hcard_searchable = True
            else:
                wf.hcard_searchable = False
            return self.new(None,wf.uri,wf.public_key,wf.seed_location,
            searchable=wf.hcard_searchable,image_url=wf.hcard_image_large                        
            ,last_name=wf.hcard_last_name,first_name=wf.hcard_first_name,guid=wf.guid)
        else:
            return None
