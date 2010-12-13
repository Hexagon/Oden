# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

# See readme for dependencies and installation instructions

import tornado.httpserver
import tornado.ioloop
import tornado.web
import os

import config

def main():
    # Fire up the server
    settings = {
        "static_path": os.path.join(os.path.dirname(__file__), config.public_dir),
        "cookie_secret": config.cookie_secret,
        "login_url": config.login_url,
        "xsrf_cookies": config.xsrf_cookies,
    }
    application = tornado.web.Application(config.routes,**settings)
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(config.port)
    tornado.ioloop.IOLoop.instance().start()

if __name__ == "__main__":
    main()
