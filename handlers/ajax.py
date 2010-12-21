# Oden
# Copyright (C) 2010 Robin Nilsson <robinnilsson@gmail.com>
#
# This is released under GNU aGPL, see COPYRIGHT for full license.

import tornado.web
import tornado.escape
import re
import helper
from data import people,aspects,request
from lib.oden import poster

class PersonByHandle(helper.AuthHandler):
    def post(self):

        # TODO: Validate this input!!
        handle = self.get_argument("q",None)

        if handle == None:
            raise tornado.web.HTTPError(404)

        person = people.People()
        person.get_by_handle(handle)

        # If person now exist, send response
        if person.data != None:
            self.render("templates/ajax/personbyid.html",
                        handle=person.data[u'profile'][u'oden_handle'],
                        guid=person.data[u'_id'],
                        name=person.get_full_name_or_nickname())
        else:
            # 404
            raise tornado.web.HTTPError(404)


class SendContactRequest(helper.AuthHandler):
    def post(self):

        # TODO: Validate this input!!
        person_ref = self.get_argument("id",None)
        aspect_ref = self.get_argument("aspect",None)

        if person_ref and aspect_ref:
            
            aspect = aspects.Aspects()
            person = people.People()

            valid_aspect = aspect.get_by_id(aspect_ref)
            valid_person = person.get_by_id(person_ref)

            if valid_person and valid_aspect:

                # Everything seem ok, try pushing a request to this person
                sender_person_id = people.People().get_by_user_id(self.current_user)[u'_id']
                receiver_person_id = valid_person[u'_id']
                
                request_obj = request.Request()
                if request_obj.new(sender_person_id,receiver_person_id):
            
                    # Send the message
                    postman = poster.Poster()
                    if postman.post_to_person(self.current_user,receiver_person_id,request_obj.to_xml()):
                        self.write("ok")
                    else:
                        # Error
                        raise tornado.web.HTTPError(500)
                else:
                    # Error
                    raise tornado.web.HTTPError(500)
            else:
                # Not found
                raise tornado.web.HTTPError(404)

        else:
            # Not found
            raise tornado.web.HTTPError(404)
