# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

import tornado.web
import pymongo
from data import user
from data import aspects

# Request Handlers
class PublicHandler(tornado.web.RequestHandler):
    def get_current_user(self):
        return self.get_secure_cookie("user_id")

class AuthHandler(PublicHandler):
    def prepare(self):
        # Redirect user if not logged in
        if not self.get_current_user():
            self.redirect("/login")

        try:
            current_user_obj = user.User()
            current_user_obj.get_by_id(self.current_user)

            tmp_aspects = aspects.Aspects()
            tmp_aspects.get_all_by_user_id(self.current_user)

            self.user_params = {'aspects':tmp_aspects.data,'username':current_user_obj.data[u'username']}
        except:
            # This is wierd, log out
            self.clear_all_cookies()
            self.redirect("/login")

