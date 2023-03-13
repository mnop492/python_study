import base64
import hashlib
from pyDes import des, CBC, PAD_PKCS5

class Cryption():

    @staticmethod
    def des_encrypt_b64(secret_key, password):
        bArr = [1, 2, 3, 4, 5, 6, 7, 8]
        input_text = password
        iv = bytearray(bArr)
        k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
        en = k.encrypt(input_text, padmode=PAD_PKCS5)
        return str(base64.b64encode(en),'utf-8')

    @staticmethod
    def sign(data_dict):
        SECRET = 'mx-muc5.0-sign' 
        data_dict.pop('sign')
        data_dict = dict(sorted(data_dict.items()))
        str = ""
        for key in data_dict:
            str += key
            str += data_dict[key]        
        md5 = hashlib.md5((SECRET + str +SECRET).encode("utf8")).hexdigest()   
        return md5
    
    @staticmethod
    def signString(str):                
        md5 = hashlib.md5((str).encode("utf8")).hexdigest()   
        return md5
