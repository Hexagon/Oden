# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

import tornado.web
import helper
import config
from data import user
import re

# users.New
# - Creates a new user
#
# GET Template: login.register.html
#
# Async activated as key generation is a slow process

class New(helper.PublicHandler):
    def get(self):

        # No need to be on Register page if user is signed in
        if self.current_user:
            self.redirect("/")

        title = "Sign up"
        self.render("templates/login.register.html",title="ODEN | Sign Up",errors=[],user='',email='')

    def post(self):

        # No need to login if user is logged in
        if self.current_user:
            self.redirect("/")

        # Validate user
        errors = []
        
        try:
            _user = self.get_argument("username").strip().lower()
        except:
            _user = ""
            errors.append("Missing required field username")

        try:
            _pass = self.get_argument("password")
        except:
            _pass = ""
            errors.append("Missing required field password")

        try:
            _pass_confirm = self.get_argument("password_confirm")
        except:
            _pass_confirm = ""
            errors.append("Missing required field password confirmation")

        try:
            _email = self.get_argument("email")
        except:
            _email = ""
            errors.append("Missing required field email")

        # Skip validation if we have errors
        if len(errors) == 0:
            # Check for valid username
            if len(_user) < 4 or len(_user) > 32:
                errors.append("Username is too long or too short")
            elif re.match("^[a-zA-Z0-9_.-]+$", _user) == None:
                errors.append("Username contained illegal characters")

            # Check for valid password
            if _pass != _pass_confirm:
                errors.append("Passwords do not match")
            elif len(_pass) < 6:
                errors.append("Password is too short")

            # Check for valid email
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", _email) == None:
                errors.append("Email does not seem valid")

            # ToDo, check that user or email doesnt exist
            # + 

        if len(errors) == 0:
            # Registrera anvandaren
            new_user = user.User().new(_user,_pass,_email)
            if new_user:
                self.render("templates/login.register.success.html",title="ODEN | Welcome",user=_user)
            else:
                self.render("templates/login.register.html",title="ODEN | Sign Up",errors=["Unknown server error"],user=_user,email=_email)
        else:
            # Let the user try again
            title = "Sign up"
            self.render("templates/login.register.html",title="ODEN | Sign Up",errors=errors,user=_user,email=_email)

class Edit(helper.AuthHandler):
    def get(self):
        
        errors = []

        edit_user = user.User()
        edit_user.get_by_id(self.current_user)
        handle = edit_user.data[u'username'].strip().lower() + "@" + config.pod_domain

        self.render("templates/user.edit.html",title="ODEN | Edit user",handle=handle,done=False,errors=errors,email=edit_user.data[u'email'])

    def post(self):

        # Validate new password
        errors = []

        edit_user = user.User()
        edit_user.get_by_id(self.current_user)
        handle = edit_user.data[u'username'].strip().lower() + "@" + config.pod_domain

        try:
            _pass = self.get_argument("password")
        except:
            _pass = ""

        try:
            _pass_confirm = self.get_argument("password_confirm")
        except:
            _pass_confirm = ""

        try:
            _email = self.get_argument("email")
        except:
            _email = ""
            errors.append("Missing required field email")

        # Skip validation if we have errors
        if len(errors) == 0:

            # Check for valid password
            if not _pass == "" or not _pass_confirm == "":
                if _pass != _pass_confirm:
                    errors.append("Passwords do not match")
                elif len(_pass) < 6:
                    errors.append("Password is too short")

            # Check for valid email
            if re.match("^.+\\@(\\[?)[a-zA-Z0-9\\-\\.]+\\.([a-zA-Z]{2,3}|[0-9]{1,3})(\\]?)$", _email) == None:
                errors.append("Email does not seem valid")

            # ToDo, check that email doesnt exist
            # + 

        if len(errors) == 0:
            update_user = user.User()
            try:
                if not _pass == "" or not _pass_confirm == "":
                    update_user.update(self.current_user,_email,password=_pass)
                else:
                    update_user.update(self.current_user,_email)
                self.render("templates/user.edit.html",title="ODEN | Welcome",done=True,errors=errors,handle=handle,email=_email)
            except:
                errors.append("Could not save changes, unknown error.")

        # We got errors
        self.render("templates/user.edit.html",title="ODEN | Welcome",done=False,errors=errors,handle=handle,email=_email)


