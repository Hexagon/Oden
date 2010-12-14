# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

import tornado.web
import tornado.escape
import re
import helper
from data import aspects, user

# aspects.All
# - Default page for logged in users
#
# aspects.All
class All(helper.AuthHandler):
    def get(self):

        create_status = self.get_argument("create",None)
        remove_status = self.get_argument("remove",None)

        status = None
        status = "Aspect is now deleted"                 if remove_status == "success" else status
        status = "New aspect successfully created"       if create_status == "success" else status
        status = "The new aspect could not be created"   if create_status == "fail"    else status 
        status = "The aspect name was not valid"         if create_status == "invalid" else status 

        current_user_obj = user.User()
        current_user_obj.get_by_id(self.current_user) # Fetch user

        user_aspects = aspects.Aspects()
        user_aspects.get_all_by_user_id(self.current_user) # Fetch all aspects
        
        title = "Welcome %s" % (current_user_obj.get_full_name_or_nickname())

        self.render("templates/aspects.all.html",user_params=self.user_params,title=title,status=status)

class Create(helper.AuthHandler):
    def post(self):
        # This should be fetched using ajax eventually
        if not self.get_argument("name",None):
            self.redirect("/aspects/all/?create=invalid1")

        if re.match("^[a-zA-Z0-9_.-]+$", self.get_argument("name")):
            if aspects.Aspects().new(self.get_argument("name"),self.current_user):
                self.redirect("/aspects/all/?create=success")
            else:
                self.redirect("/aspects/all/?create=fail")
        else:
            self.redirect("/aspects/all/?create=invalid")

class Remove(helper.AuthHandler):
    def get(self,_id):
        
        # Check that this is the users aspect
        

        self.redirect("/aspects/all?remove=success")




