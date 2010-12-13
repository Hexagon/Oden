# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

import tornado.web
import helper
from data import user
# main.Index
# - Default page for logged in users
#
# GET Template: main.index.html

class Index(helper.AuthHandler):
    def get(self):

        current_user_id = tornado.escape.xhtml_escape(self.current_user)

        # Get current user
        current_user_obj = user.User()
        current_user_obj.get_by_id(current_user_id) # Populate object with data
        
        title = "Welcome %s" % (current_user_obj.get_full_name_or_nickname())
        self.render("templates/main.index.html",title=title)
