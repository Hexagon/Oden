# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

import tornado.web
import helper
from data import aspects, user

# aspects.All
# - Default page for logged in users
#
# aspects.All
class All(helper.AuthHandler):
    def get(self):

        self.current_user

        current_user_obj = user.User()
        current_user_obj.get_by_id(self.current_user) # Fetch user

        user_aspects = aspects.Aspects()
        user_aspects.get_all_by_user_id(self.current_user) # Fetch all aspects
        
        title = "Welcome %s" % (current_user_obj.get_full_name_or_nickname())
        self.render("templates/aspects.all.html",title=title)
