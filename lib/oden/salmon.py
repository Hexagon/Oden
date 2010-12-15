from Crypto.Cipher import AES
from lib.oden import aes_helper,rsa_helper
from lib.magicsig import magicsigalg, MagicEnvelopeProtocol, Envelope, utils
import base64
import json

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
        key_hash = json.dumps({'key':base64.b64encode(key[0]),'iv':base64.b64encode(key[1])})
        encrypted_key = base64.b64encode(rsa_helper.encrypt(key_hash,self.public_key))

        # Put it all together to a nice Salmon-friendly atom XML
        xml =  "<?xml version='1.0' encoding='UTF-8'?>\n\
                <entry xmlns='http://www.w3.org/2005/Atom'>\n\
                    <encrypted_header>%s</encrypted_header>\n\
                    %s\n\
                </entry>" % (ciphertext,self.envelope)

        return xml

