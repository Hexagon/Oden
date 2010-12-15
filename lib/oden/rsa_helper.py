import config
from Crypto.PublicKey import RSA

# Generate a RSA key pair using Crypto.PublicKey.RSA
def generate_rsa(bits):
    key = RSA.generate(4096)
    private = key.exportKey('PEM')
    public = key.publickey().exportKey('PEM')
    return [public,private]

def encrypt(plain,pem_key):
    key = RSA.importKey(pem_key)
    return key.encrypt(plain,None)[0]

def decrypt(cipher,pem_key):
    key = RSA.importKey(pem_key)
    return key.decrypt(cipher)

def pem_to_private_tuple(pem_key):
    rsa_key = RSA.importKey(pem_key)
    return (rsa_key.n, rsa_key.e, rsa_key.d)

def pem_to_public_tuple(pem_key):
    rsa_key = RSA.importKey(pem_key)
    return (rsa_key.n, rsa_key.e)
