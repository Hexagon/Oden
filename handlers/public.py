# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

import tornado.web
import helper
import re
import config
import datetime
import base64
from data import people,user
from lib.oden import salmon

# Serves the pod host-meta file

# Serve the host meta file at /.well-known/host-meta
class HostMeta(helper.PublicHandler):
    def get(self):
        self.set_header("Content-Type", "application/xrd+xml")
        self.render("templates/public.host-meta.html",host=config.pod_domain,url=config.pod_url)

# Serve the webfinger profile at /webfinger
class Webfinger(helper.PublicHandler):
    def get(self):
        try:
            # Only respond to usernames@local.pod
            _people_handle = self.get_argument("q").strip().lower()
            _user = _people_handle.split("@%s" % (config.pod_domain))[0].strip().lower()

            # Check for valid username
            if len(_user) < 4 or len(_user) > 32 or re.match("^[a-zA-Z0-9_.-]+$", _user) == None:
                # Invalid username, return 403 Unauthorized
                raise tornado.web.HTTPError(403)

            if _user == _people_handle:
                # Username does not belong to this pod, return 403 Unauthorized
                raise tornado.web.HTTPError(403)

            # Check for people object in db
            _people_obj = people.People()
            _people_obj.get_by_handle(_people_handle)
            if _people_obj.data == None:
                # Invalid user, return 403 Unauthorized
                raise tornado.web.HTTPError(403)

            # All is ok, keep on rocking ...
        except:
            # Error, return 403 Unauthorized
            raise tornado.web.HTTPError(403)

        _people_guid = _people_obj.data[u'_id']
        _pubkey_type="RSA"
        _pubkey = base64.b64encode(_people_obj.data[u'serialized_public_key'])

        self.set_header("Content-Type", "application/xrd+xml")
        self.render("templates/public.webfinger.html",
                    pod_url=config.pod_url,
                    user=_user,
                    people_handle=_people_handle,
                    people_guid=_people_guid,
                    pubkey=_pubkey,
                    pubkey_type=_pubkey_type)

# Serve the hcard at /hcard/users/<user_id>
class Hcard(helper.PublicHandler):
    def get(self,user_id):
        try:
            # Check for people object in db
            _people_obj = people.People()
            _people_obj.get_by_id(user_id)

            # Check for valid username
            _username = _people_obj.get_username()
            if _username == None:
                # Invalid people_id, return 403 Unauthorized
                raise tornado.web.HTTPError(405)

            # All is ok, keep on rocking ...
        except:
            # Error, return 500 Internal server error
            raise tornado.web.HTTPError(500)


        if _people_obj.data[u'profile'][u'image_url'] == None:
            photo_large_url = config.pod_url + "static/images/default_large.png"
            photo_medium_url = config.pod_url + "static/images/default_medium.png"
            photo_small_url = config.pod_url + "static/images/default_small.png"
        else:
            #TODO: Add support for custom avatars, for now, just use defaults
            photo_large_url = config.pod_url + "static/images/default_large.png"
            photo_medium_url = config.pod_url + "static/images/default_medium.png"
            photo_small_url = config.pod_url + "static/images/default_small.png"
        
        if _people_obj.data[u'profile'][u'searchable']:
            people_searchable = "true"
        else:
            people_searchable = "false"

        full_name = _people_obj.get_full_name_or_nickname()
   
        first_name = _people_obj.data[u'profile'][u'first_name']
        if first_name == None:
            first_name = ""
        else:
            first_name =  first_name

        family_name = _people_obj.data[u'profile'][u'last_name']
        if family_name == None:
            family_name = ""
        else:
            family_name =  family_name
        self.render("templates/public.hcard.html",
                    pod_url=config.pod_url,
                    people_searchable=people_searchable,
                    photo_large_url=photo_large_url,
                    photo_medium_url=photo_medium_url,
                    photo_small_url=photo_small_url,
                    full_name=full_name,
                    first_name=first_name,
                    family_name=family_name)

# login.Index
# - Default route for users who are not authenticated
# - Presents the user with a login box
#
# GET Template: login.index.html
class Login(helper.PublicHandler):

    def get(self):

        # No need to be on loginpage if user is logged in
        if self.current_user:
            self.redirect("/")

        # Page title
        title = "ODEN | Sign In"

        self.render("templates/login.index.html",title=title,errors=[],pod_domain=config.pod_domain)

    def post(self):

        # Page title
        title = "ODEN | Signing In"

        # No need to login if user is logged in
        if self.current_user:
            self.redirect("/")

        # Get username and password from post arguments
        try:
            _user = self.get_argument("username")
            _pass = self.get_argument("password")
        except:
            # Credentials missing
            self.render("templates/login.index.html",title=title,errors=["Credentials missing"],pod_domain=config.pod_domain)
            return

        # Authenticate user
        usr_auth = user.User()
        if usr_auth.authenticate(_user,_pass):
            # Save user id to cookie
            self.set_secure_cookie("user_id", str(usr_auth.data[u'_id']))
            self.redirect("/")
        else:
            self.render("templates/login.index.html",title=title,errors=["Wrong username or password"],pod_domain=config.pod_domain)

# login.Logout
# - Clear cookies (sign out current user)
#
# GET Template: None
class Logout(helper.AuthHandler):
    def get(self):
        # Clear cookies to make sure the user is logged out
        self.clear_all_cookies()
        self.redirect("/login")

# public.Receive
# - This is where all remote data is received
#
class Receive(helper.PublicHandler):

    # Disable XSRF-Cookie check as these requests isn't supposed to have one
    def check_xsrf_cookie(self): 
        pass

    def get(self,_id):

        # No need to get this one
        raise tornado.web.HTTPError(404)

    def post(self,_id):

        # Get username and password from post arguments
        _xml = self.get_argument("xml",None)
        _id = _id

        if _xml == None: 
            tornado.web.HTTPError(422)

        # TODO: check that person exists
        print "Received remote data"
        print "To ID: %s \n" % _id
        print "Data:\n"

        # Get recepient
        recv_user = user.User()
        if recv_user.get_by_id(_id) != None:
            # Decode salmon
            decoder = salmon.Salmon()
            result = decoder.read_xml(_xml,recv_user[u'serialized_private_key'])
            
            print result

            # We currently pretend that the object is received and handled
            tornado.web.HTTPError(200)

        else:
            tornado.web.HTTPError(404)

# Host the public atom feed for users at /username.atom and /username
class AtomFeed(helper.PublicHandler):
    def get(self,user_name):
        #try:
        # Check for people object in db
        _people_obj = people.People()
        _people_obj.get_by_handle(user_name+"@"+config.pod_domain)

        # Check for valid username
        _username = _people_obj.get_username()
        if _username == None:
            # Invalid people_id, return 404 Not found
            raise tornado.web.HTTPError(404)

        # All is ok, keep on rocking ...
        #except:
            # Error, return 500 Internal server error
        #   raise tornado.web.HTTPError(500)

        if _people_obj.data[u'profile'][u'image_url'] == None:
            image_url = config.pod_url + "static/images/default_large.png"
        else:
            #TODO: Add support for custom avatars, for now, just use defaults
            image_url = config.pod_url + "static/images/default_large.png"

        full_name = _people_obj.get_full_name_or_nickname()

        self.set_header("Content-Type", "application/atom+xml")
        self.render("templates/public.atom.xml",
                    pod_url=config.pod_url,
                    image_url=image_url,
                    full_name=full_name,
                    user=_username,
                    time_now=datetime.datetime.utcnow())
