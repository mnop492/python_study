import hashlib
import pyDes
import base64
 
# 字符串加密
 
def getMd5EncryptEncode(string):
    keye = 'hi%$so12'  # MD5
    keyb = '34up56^&'  # IvParameterSpec
 
    s = string.encode('utf-8')
 
    md = hashlib.md5()
    md.update(keye.encode('utf-8'))
    desKeySpec = md.hexdigest()
 
    for i in range(1, 12):
        md = hashlib.md5()
        md.update(keye.encode('utf-8'))
        desKeySpec = md.digest()        
    k = pyDes.des(desKeySpec[:8], pyDes.CBC, keyb.encode('utf-8'), pad=None, padmode=pyDes.PAD_PKCS5)
    return (base64.b64encode(k.encrypt(s))).decode('utf-8')
    
 
# 密文解码
 
def getMd5EncryptDecode(string):
    keye = '123456!@#$'  # MD5
    keyb = '123456!@#$'  # IvParameterSpec
 
    s = base64.b64decode(string.encode('utf-8'))
 
    md = hashlib.md5()
    md.update(keye.encode('utf-8'))
    desKeySpec = md.hexdigest()
 
    for i in range(1, 12):
        md = hashlib.md5()
        md.update(keye.encode('utf-8'))
        desKeySpec = md.digest()        
    k = pyDes.des(desKeySpec[:8], pyDes.CBC, keyb.encode('utf-8'), pad=None, padmode=pyDes.PAD_PKCS5)
    return str(k.decrypt(s).decode('utf-8'))
