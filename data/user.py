import pymongo
import crypt
import dbobject
import datetime
import config
from handlers import helper
from data import people

class User(dbobject.Base):
    def __init__(self):
        dbobject.Base.__init__(self)
        self.collection = self.db['users']
        self.debug = None

        # These get populated when a user is searched for or created
        self.objectid = None
        self.data = None
        self.person = None

    # Creates a new user
    def new(self,username,password,email):
        
        try:
            _user = username
            _pass = password
            _email = email
            _salt = "%s%s" % (_user[1],_email[0])
            _enc_pass = crypt.crypt(_pass, _salt)

        except:
            self.debug = "Data preparation failed ..."
            return False

        _diaspora_handle = _user + "@" + config.pod_domain
        _pod_url = config.pod_url

        # Generate RSA key pair, 4096 bit
        keys = helper.generate_rsa(4096)
        if keys != None:
            _priv_key = keys[1]
            _pub_key = keys[0]
        else:
            self.debug = "Key generation failed ..."
            return False

        # Construct user document
        user = {"username": _user,
                "email": _email,
                "encrypted_password":_enc_pass,
                "password_salt":"",
                "pending_request_ids":[],
                "visible_person_ids":[],
                "visible_post_ids": [],
                "current_sign_in_ip": "",
                "current_sign_in_at": datetime.datetime.utcnow(),
                "last_sign_in_ip": "",
                "last_sign_in_at": datetime.datetime.utcnow(),
                "sign_in_count": 0,
                "serialized_private_key": _priv_key,
                "getting_started": True
                }

        # Try inserting object
        try:

            self.object_id = self.collection.insert(user)

            # Populate self.data
            self.get_by_id(self.object_id)

            # Force creation of a corresponding people object
            people_obj = people.People().new(self.object_id,_diaspora_handle,_pub_key,_pod_url)
            if people_obj:
                return True
            else:
                # No profile could be created
                # TODO: Delete the newly created user object ( with id - self.object_id )
                self.debug = "People object could not be created ..."
                return False
        except:
            # User could not be created
            self.debug = "Could not insert object in  ..."
            return False

    # Authenticates a user, using username and password
    def authenticate(self,username,password):
        _user = username.lower().strip()
        _pass = password
        ret = self.collection.find_one({"username":_user})
        if ret:
            _enc_pass = ret[u'encrypted_password']
            res = crypt.crypt(_pass,_enc_pass)
            if res == _enc_pass:    
                # Populate object with the authenticated user
                self.data = ret
                self.object_id = self.data[u'_id']
                return True
            else:
                self.debug = "Incorrect password"
                return False
        else:
            self.debug = "Username not found"
            return False

    # Fetch a user by username
    def get_by_username(self,_user):
        self.data = self.collection.find_one({"username":_user})
        if self.data != None:
            self.object_id = self.data[u'_id']
        return self.data

    # Get full name if existant, else nickname
    def get_full_name_or_nickname(self):
        # Prevent person from being fetched multiple times
        if self.person == None:
            self.person = people.People()
            self.person.get_by_user_id(self.object_id)
        return self.person.get_full_name_or_nickname()

