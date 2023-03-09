import binascii
from pyDes import des, CBC, PAD_PKCS5
import base64


bArr = [1, 2, 3, 4, 5, 6, 7, 8]

def des_encrypt(s):
    """
    DES 加密
    :param s: 原始字符串
    :return: 加密后字符串，16进制
    """
    secret_key = '1c38dedb'
    iv = bytearray(bArr)
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    en = k.encrypt(s, padmode=PAD_PKCS5)
    #return binascii.b2a_hex(en)
    return en


def des_descrypt(s):
    """
    DES 解密
    :param s: 加密后的字符串，16进制
    :return:  解密后的字符串
    """
    secret_key = '20171117'
    iv = secret_key
    k = des(secret_key, CBC, iv, pad=None, padmode=PAD_PKCS5)
    de = k.decrypt(binascii.a2b_hex(s), padmode=PAD_PKCS5)
    return de


encrypted = des_encrypt('Qa7Ly4Tj4Y')
print (str(base64.b64encode(encrypted),'utf-8'))
#str_en = des_encrypt('Qa7Ly4Tj4Y')
#print(str_en)
#str_de = des_descrypt(str_en)
#print(str_de)
