# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

import tornado.web
import helper
import re
import config
from data import people

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
        _pubkey = _people_obj.data[u'serialized_public_key']

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


