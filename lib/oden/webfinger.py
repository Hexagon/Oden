import urllib2
from xml.etree import ElementTree
import base64
import re

class OdenWFResult:
    def __init__(self):
        self.lrdd_url = None
        self.uri = None

        self.guid = None
        self.seed_location = None
        self.updates_from = None
        self.public_key = None
        self.public_key_type = None

        self.hcard_url = None
        self.hcard_nickname = None
        self.hcard_first_name = None
        self.hcard_last_name = None
        self.hcard_image_large = None
        self.hcard_image_medium = None
        self.hcard_image_small = None
        self.hcard_searchable = None

        self.valid = False

    def Validate(self):
        # TODO: Make this much better
        if self.guid != None and self.uri != None and len(self.hcard_nickname) > 2 and (self.hcard_searchable == "true" or self.hcard_searchable == "false"):
            self.valid = True
            return True
        else:
            self.valid = False
            return False

        

class Webfinger:
    def __init__(self):
        self.result = OdenWFResult()
        self.error = None
        pass

    def finger(self,uri):
  
        self.result.uri = uri

        # Split uri in pieces
        uri_arr = uri.lower().split("@")
        if len(uri_arr) != 2:
            return None

        self.user = uri_arr[0]
        self.host = uri_arr[1]
        self.host_meta = None

        # Try HTTP
        try:
            f = urllib2.urlopen('http://%s/.well-known/host-meta' % (self.host))
            self.host_meta = f.read(4096)
        except:
            # Try HTTPS
            try:
                f = urllib2.urlopen('https://%s/.well-known/host-meta' % (self.domain))
                self.host_meta = f.read(4096)
            except:
                self.error = "Could not get host-meta"
                return None

        # Validate that we have a host meta document
        try:        
            host_meta_tree = ElementTree.fromstring(self.host_meta)
            self.host = host_meta_tree.findtext('.//{http://host-meta.net/xrd/1.0}Host')
            self.lrdd_template = host_meta_tree.find('.//{http://docs.oasis-open.org/ns/xri/xrd-1.0}Link').get('template')
        except:
            self.error = "Could not verify host-meta"
            return None

        self.result.lrdd_url = self.lrdd_template.replace("{uri}",uri)

        # Try getting webfinger profile
        try:
            f = urllib2.urlopen(self.result.lrdd_url)
            self.webfinger_profile = f.read(4096)
        except:
            self.error = "Could not get webfinger profile"
            return None

        # Parse the webfinger profile
        #try:        
        webfinger_profile_tree = ElementTree.fromstring(self.webfinger_profile)
        self.result.seed_location = webfinger_profile_tree.findtext('.//{http://docs.oasis-open.org/ns/xri/xrd-1.0}Subject')
        for node in webfinger_profile_tree.getiterator():
            if node.tag == "{http://docs.oasis-open.org/ns/xri/xrd-1.0}Link":
                if node.get("rel") == "http://microformats.org/profile/hcard":
                    self.result.hcard_url = node.get("href")
                elif node.get("rel") == "http://joindiaspora.com/seed_location":
                    self.result.seed_location = node.get("href")
                elif node.get("rel") == "http://joindiaspora.com/guid":
                    self.result.guid = node.get("href")
                elif node.get("rel") == "http://schemas.google.com/g/2010#updates-from":
                    self.result.updates_from = node.get("href")
                elif node.get("rel") == "diaspora-public-key":
                    self.result.public_key_type = node.get("type")
                    self.result.public_key = base64.b64decode(node.get("href").replace(" ","").replace("\n",""))
        #except:
        #    self.error = "Could not parse webfinger profile"
        #    return None
    
        # Try getting the hcard
        try:
            f = urllib2.urlopen(self.result.hcard_url)
            self.hcard_data = f.read()
        except:
            self.error = "Could not get hcard"
            return None

        # Parse the hcard
        
        # This is probably the worst solution ever, in all categories,
        # but i don't want to include another depency just to get
        # this fixed. ElementTree cant parse the profile when it
        # has un-ended tags
        try:
            self.hcard_data = re.sub("(<img[^>]*)", "\\1/", self.hcard_data);
            self.hcard_data = self.hcard_data.replace("//>","/>")
            hcard_tree = ElementTree.fromstring(self.hcard_data)
            for node in hcard_tree.findall('.//div/div/dl'):
                node_class = node.get("class")
                if node_class == "entity_searchable":
                    self.result.hcard_searchable = node.findtext("dd/span")
                if node_class == "entity_nickname":
                    self.result.hcard_nickname = node.findtext("dd/a")
                if node_class == "entity_given_name":
                    self.result.hcard_first_name = node.findtext("dd/span")
                if node_class == "entity_family_name":
                    self.result.hcard_last_name = node.findtext("dd/span")
                if node_class == "entity_photo":
                    self.result.hcard_image_large = node.find("dd/img").get("src")
                if node_class == "entity_photo_small":
                    self.result.hcard_image_small = node.find("dd/img").get("src")
                if node_class == "entity_photo_medium":
                    self.result.hcard_image_medium = node.find("dd/img").get("src")
            test = self.result.Validate()
            return self.result
        except:
            self.error = "Could not parse hcard"
            return None

