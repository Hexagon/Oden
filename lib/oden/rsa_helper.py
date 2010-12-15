import config
from Crypto.PublicKey import RSA

# Generate a RSA key pair using Crypto.PublicKey.RSA
def generate_rsa(bits):
    key = RSA.generate(4096)
    private = key.exportKey('PEM')
    public = key.publickey().exportKey('PEM')
    return [public,private]
