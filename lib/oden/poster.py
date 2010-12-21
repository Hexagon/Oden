from data.people import People
from data.user import User
from lib.oden import salmon
from tornado import httpclient

class Poster:
    def __init__(self):
        pass

    def post_to_person(self,author_user_id,person_id,xml):
        
        # Get the person to post to
        person = People()
        person.get_by_id(person_id)

        # Get poster person
        author_obj = People()
        author_person = author_obj.get_by_user_id(author_user_id)
        author_name = author_obj.get_full_name_or_nickname()
        author_user = User().get_by_id(author_user_id)

        # Generate salmon envelope
        if person.data:

            # TODO: This should be in a try clause
            salmon_obj = salmon.Salmon()
            salmon_obj.create(author_name,author_person[u'oden_handle'],author_user[u'serialized_private_key'],person.data[u'serialized_public_key'],xml)
            
            salmon_xml = salmon_obj.write_xml()

            url = person.data[u'url'].rstrip('/') + '/receive/ussers/' + str(person.data[u'_id'])

            result = httpclient.HTTPRequest(
                    method='POST',
                    headers={'Content-Type':'text/xml'},
                    url=url,
                    body=salmon_xml,
                    connect_timeout=0.5,
                    request_timeout=3)

            if result:
                return True
            else:
                return False
        else:
            return False
