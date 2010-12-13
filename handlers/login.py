# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

import tornado.web
import helper
from data.user import *
import re

# login.Index
# - Default route for users who are not authenticated
# - Presents the user with a login box
#
# GET Template: login.index.html
class Index(helper.PublicHandler):

    def get(self):

        # No need to be on loginpage if user is logged in
        if self.current_user:
            self.redirect("/")

        # Page title
        title = "ODEN | Sign In"

        self.render("templates/login.index.html",title=title,errors=[])

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
            self.render("templates/login.index.html",title=title,errors=["Credentials missing"])
            return

        # Authenticate user
        usr_auth = User()
        if usr_auth.authenticate(_user,_pass):
            # Save user id to cookie
            self.set_secure_cookie("user_id", str(usr_auth.data[u'_id']))
            self.redirect("/")
        else:
            self.render("templates/login.index.html",title=title,errors=["Wrong username or password"])

# login.Logout
# - Clear cookies (sign out current user)
#
# GET Template: None
class Logout(helper.AuthHandler):
    def get(self):
        # Clear cookies to make sure the user is logged out
        self.clear_all_cookies()
        self.redirect("/login")

# login.Register
# - Creates a new user
#
# GET Template: login.register.html
#
# Async activated as key generation is a slow process

class Register(helper.PublicHandler):
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
            new_user = User().new(_user,_pass,_email)
            if new_user:
                self.render("templates/login.register.success.html",title="ODEN | Welcome",user=_user)
            else:
                self.render("templates/login.register.html",title="ODEN | Sign Up",errors=["Unknown server error"],user=_user,email=_email)
        else:
            # Let the user try again
            title = "Sign up"
            self.render("templates/login.register.html",title="ODEN | Sign Up",errors=errors,user=_user,email=_email)

  

