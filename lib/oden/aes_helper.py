from Crypto.Cipher import AES
from Crypto.Util.number import GCD
from Crypto import Random

def get_random_key():
    rand = Random.new()
    Random.atfork()
    key = rand.read(16).encode("hex")
    iv  = rand.read(8).encode("hex")
    return [key,iv]
    
def encrypt(plain,keys):
    crypt = AES.new(keys[0],AES.MODE_CBC,keys[1])
    pad =(16-len(plain)%16)%16
    tmp_str = ""

    # Pad string with whitespaces
    for a in range(pad):
        tmp_str+=" "

    plain+=tmp_str

    return crypt.encrypt(plain)

def decrypt(cipher,keys):
    crypt = AES.new(keys[0],AES.MODE_CBC,keys[1])
    return crypt.decrypt(cipher)
