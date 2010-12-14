import config
from subprocess import call

# Generate RSA by _using system calls_
# ( using python rsa lib was too slow for now )
def generate_rsa(bits):

    public_path = config.temp_path+"publ.key"
    private_path = config.temp_path+"priv.key"

    retcode_private = call([config.openssl_executable, "genrsa", "-out", private_path, "%i" % (bits)],shell=False)

    if retcode_private == 0:
        retcode_public = call([config.openssl_executable, "rsa", "-in", private_path, "-pubout", "-out",public_path],shell=False)
        if retcode_public == 0:

            # Try reading
            try:
                f = open(public_path, 'r')
                public_key = f.read()
                f.close()

                f = open(private_path, 'r')
                private_key = f.read()
                f.close()

                return [public_key,private_key]
            except:
                pass

            # Clean up
            try:
                call(["rm","-f",private_path],shell=False)
                call(["rm","-f",public_path],shell=False)
            except:
                pass

            return None
        
        else:

            # Clean private
            try:
                call(["rm","-f",private_path],shell=False)
            except:
                pass

            return None
    else:

        return None
