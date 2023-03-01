from Crypto.Hash import MD5
from Crypto.Cipher import DES
import base64
import re

_password = b'q1w2e3r4t5y6'
_salt = b'\x80\x40\xe0\x10\xf8\x04\xfe\x01'

_iterations = 50

plaintext_to_encrypt = 'MyP455w0rd'

# Pad plaintext per RFC 2898 Section 6.1
padding = 8 - len(plaintext_to_encrypt) % 8
plaintext_to_encrypt += chr(padding) * padding

if "__main__" == __name__:

    """Mimic Java's PBEWithMD5AndDES algorithm to produce a DES key"""
    hasher = MD5.new()
    hasher.update(_password)
    hasher.update(_salt)
    result = hasher.digest()

    for i in range(1, _iterations):
        hasher = MD5.new()
        hasher.update(result)
        result = hasher.digest()

    encoder = DES.new(result[:8], DES.MODE_CBC, result[8:16])
    encrypted = encoder.encrypt(plaintext_to_encrypt.encode("utf8"))

    print (str(base64.b64encode(encrypted),'utf-8'))

    decoder = DES.new(result[:8], DES.MODE_CBC, result[8:])
    d = str(decoder.decrypt(encrypted),'utf-8')
    print (re.sub(r'[\x01-\x08]','',d))
