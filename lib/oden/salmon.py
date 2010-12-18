from Crypto.Cipher import AES
from lib.oden import aes_helper,rsa_helper
from lib.magicsig import magicsigalg, MagicEnvelopeProtocol, Envelope, utils
from xml.etree import ElementTree
import sys
import re
import base64
import simplejson

class Salmon:
    def __init__(self,author_name,author_uri,author_private_key,receiver_public_key,activity):

        self.author = author_name
        self.author_uri = utils.NormalizeUserIdToUri(author_uri)
        self.author_private_key = rsa_helper.pem_to_private_tuple(author_private_key)
        self.public_key = receiver_public_key

        # Generate AES Key
        self.aes_key = aes_helper.get_random_key()

        # Encrypt activity
        self.env_message = base64.urlsafe_b64encode(aes_helper.encrypt(activity,self.aes_key))

        # Sign the activity data
        self.env_signature = self.sign_salmon(self.env_message,self.author_private_key)

        # Create the magic signature envelope
        env_protocol = MagicEnvelopeProtocol()
        self.envelope = MagicEnvelopeProtocol().ToXmlString(Envelope(self.env_message,'application/atom+xml',self.env_signature),fulldoc=False)

    def __init__(self):
        pass

    def sign_salmon(self,message,author_key):

        # Sign the message using the authors private key and RSA-SHA256
        magicsig = magicsigalg.SignatureAlgRsaSha256(author_key)
        return magicsig.Sign(message)

    def write_xml(self):
        # Created Salmon decrypted header
        decrypted_header = "<decrypted_header>\n\
                    <iv>%s</iv>\n\
                    <aes_key>%s</aes_key>\n\
                    <author>\n\
                        <name>%s</name>\n\
                        <uri>acct:%s</uri>\n\
                    </author>\n\
                 </decrypted_header>\n" % (base64.urlsafe_b64encode(self.aes_key[1]),base64.urlsafe_b64encode(self.aes_key[0]),self.author,self.author_uri)
        
        # Encrypt decrypted_header
        key = aes_helper.get_random_key()
        ciphertext = base64.b64encode(aes_helper.encrypt(decrypted_header,key))
        
        # Encrypt AES session-key with the receivers public key
        key_hash = simplejson.dumps({'key':base64.b64encode(key[0]),'iv':base64.b64encode(key[1])})
        encrypted_key = base64.b64encode(rsa_helper.encrypt(key_hash,self.public_key))

        # Put it all together to a nice Salmon-friendly atom XML
        xml =  "<?xml version='1.0' encoding='UTF-8'?>\n\
                <entry xmlns='http://www.w3.org/2005/Atom'>\n\
                    <encrypted_header>%s</encrypted_header>\n\
                    %s\n\
                </entry>" % (ciphertext,self.envelope)

        return xml

    def filter_printable(str):
        return ''.join([c for c in str if ord(c) > 31 or ord(c) == 9])

    def read_xml(self,xml,private_key):
        
        # Parse Salmon document
        tree = ElementTree.fromstring(xml)
        
        encrypted_header = tree.findtext('.//{http://www.w3.org/2005/Atom}encrypted_header')
        envelope_data_encrypted = tree.findtext('.//{http://salmon-protocol.org/ns/magic-env}data')
        envelope_signature = tree.findtext('.//{http://salmon-protocol.org/ns/magic-env}data')
        envelope_encoding = tree.findtext('.//{http://salmon-protocol.org/ns/magic-env}encoding')
        envelope_alg = tree.findtext('.//{http://salmon-protocol.org/ns/magic-env}alg')

        # Validate stuff
        if envelope_encoding != 'base64url':
            # Wrong encoding in salmon
            return None
        
        if envelope_alg != 'RSA-SHA256':
            # Wrong algorithm used for signature
            return None
        
        # Check signature
        # TODO: IMPORTANT! Verify signature

        # B64decode and unfold encrypted header
        encrypted_header = simplejson.loads(base64.b64decode(encrypted_header))
        encrypted_header_key = base64.b64decode(encrypted_header['aes_key'])
        encrypted_header_cipher = base64.b64decode(encrypted_header['ciphertext'])
        
        # Extract the key json (diaspora adds some random padding before json data, so we'll filter that out)
        test_dec = re.search('\{\".*\"}',rsa_helper.decrypt(encrypted_header_key,private_key))
        if test_dec.group(0) == None:
            test_dec = re.search('\{\'.*\'}',rsa_helper.decrypt(encrypted_header_key,private_key))

        # Save key and iv and decrypt header
        encrypted_header_decrypted_key = [  base64.b64decode(simplejson.loads(test_dec.group(0))[u'key']),
                                            base64.b64decode(simplejson.loads(test_dec.group(0))[u'iv'])]

        decrypted_header = self.filter_printable(aes_helper.decrypt(encrypted_header_cipher,encrypted_header_decrypted_key))
        
        # Extract AES iv and key from decrypted header
        tree_header = ElementTree.fromstring(decrypted_header)
        header_iv = base64.urlsafe_b64decode(tree_header.findtext('.//iv'))
        header_key = base64.urlsafe_b64decode(tree_header.findtext('.//aes_key'))
        header_author = tree_header.findtext('.//author/name')
        header_author_handle = tree_header.findtext('.//author/uri')

        # Decrypt Salmon message
        envelope_data = self.filter_printable(aes_helper.decrypt(base64.b64decode(base64.b64decode(envelope_data_encrypted)),[header_key,header_iv]))

        return [header_author_handle,envelope_data]
